from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEGAL_DOCS_PATH = ROOT / "data" / "legal" / "processed" / "legal_documents.json"
ADDITIONAL_MANIFEST_PATH = ROOT / "data" / "legal" / "processed" / "additional_law_manifest_2026-04-23.json"
INTERNAL_RELATIONS_PATH = ROOT / "data" / "processed" / "internal_rules" / "internal_relations.json"
OUTPUT_DIR = ROOT / "data" / "processed" / "internal_rules"


LOCAL_ALIAS_OVERRIDES = {
    "특정금융정보법": "law:spec_financial_transaction_act",
    "특정금융정보법시행령": "law:spec_financial_transaction_act_enforcement_decree",
    "금융실명법": "law:real_name_financial_transactions_act",
    "금융실명법시행령": "law:real_name_financial_transactions_act_enforcement_decree",
    "범죄수익규제법": "law:proceeds_of_crime_act",
}


QUOTED_ALIAS_PATTERN = re.compile(
    r"「(?P<full>[^」]+)」\s*\(이하\s*[“\"](?P<alias>[^”\"]+)[”\"]이라\s*한다\)"
)
UNQUOTED_ALIAS_PATTERN = re.compile(
    r"(?P<full>[가-힣0-9\s·]+?(?:법률|법|시행령|시행규칙|업무규정|규정|고시))\s*\(이하\s*[“\"](?P<alias>[^”\"]+)[”\"]이라\s*한다\)"
)
SPACING_BREAK_PATTERN = re.compile(
    r"([가-힣])\s+(법률|법|시행령|시행규칙|업무규정|규정|고시)"
)
MULTISPACE_PATTERN = re.compile(r"\s+")
BRACKET_PATTERN = re.compile(r"[「」“”\"']")
ANGLE_REVISION_PATTERN = re.compile(r"<개정[^>]*>")
PAREN_PATTERN = re.compile(r"\([^)]*\)")
NON_HANGUL_WORD_PATTERN = re.compile(r"[^0-9A-Za-z가-힣]+")


@dataclass
class Candidate:
    document_id: str
    title: str
    document_type: str
    score: float
    method: str


def read_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_legal_documents() -> list[dict]:
    documents = read_json(LEGAL_DOCS_PATH)
    seen = {doc["document_id"] for doc in documents}

    if ADDITIONAL_MANIFEST_PATH.exists():
        manifest = json.loads(ADDITIONAL_MANIFEST_PATH.read_text(encoding="utf-8"))
        for target in manifest.get("targets", []):
            document_id = f"law:{target['slug']}"
            if document_id in seen:
                continue
            documents.append(
                {
                    "document_id": document_id,
                    "slug": target["slug"],
                    "document_type": "법률",
                    "title": target.get("title", "") or target.get("query", ""),
                    "kind": target.get("kind", "law"),
                    "law_id": target.get("law_id", ""),
                    "mst": target.get("mst", ""),
                }
            )
            seen.add(document_id)

    return documents


def normalize_spacing_breaks(text: str) -> str:
    prev = None
    current = text
    while current != prev:
        prev = current
        current = SPACING_BREAK_PATTERN.sub(r"\1\2", current)
    return current


def normalize_text(text: str) -> str:
    cleaned = ANGLE_REVISION_PATTERN.sub(" ", text)
    cleaned = BRACKET_PATTERN.sub(" ", cleaned)
    cleaned = PAREN_PATTERN.sub(" ", cleaned)
    cleaned = normalize_spacing_breaks(cleaned)
    cleaned = MULTISPACE_PATTERN.sub(" ", cleaned).strip()
    return cleaned


def compact_text(text: str) -> str:
    cleaned = normalize_text(text)
    cleaned = NON_HANGUL_WORD_PATTERN.sub("", cleaned)
    return cleaned


def infer_target_type(raw_target: str) -> str:
    compact = compact_text(raw_target)
    if "시행령" in compact:
        return "decree"
    if "시행규칙" in compact:
        return "rule"
    if "업무규정" in compact or "고시" in compact or "규정" in compact:
        return "adm_rule"
    if "법" in compact or "법률" in compact:
        return "law"
    return "unknown"


def infer_document_bucket(document: dict) -> str:
    title = document["title"]
    if "시행령" in title:
        return "decree"
    if "시행규칙" in title:
        return "rule"
    if document.get("kind") == "adm_rule" or "업무규정" in title or document.get("document_type") in {"고시", "훈령"}:
        return "adm_rule"
    return "law"


def is_legal_like(text: str) -> bool:
    compact = compact_text(text)
    return any(
        suffix in compact
        for suffix in ("법률", "시행령", "시행규칙", "업무규정", "고시", "규정", "법")
    )


def token_set(text: str) -> set[str]:
    normalized = normalize_text(text)
    parts = [token for token in re.split(r"\s+", normalized) if len(token) >= 2]
    return set(parts)


def build_alias_catalog(relations: list[dict]) -> dict[str, set[str]]:
    alias_to_full_names: dict[str, set[str]] = {}
    for rel in relations:
        if rel.get("relation_type") != "REFERS_TO_LAW_NAME":
            continue
        source_text = rel.get("source_text", "")
        for pattern in (QUOTED_ALIAS_PATTERN, UNQUOTED_ALIAS_PATTERN):
            for match in pattern.finditer(source_text):
                full_name = normalize_text(match.group("full"))
                alias = normalize_text(match.group("alias"))
                if not full_name or not alias or not is_legal_like(full_name):
                    continue
                alias_to_full_names.setdefault(alias, set()).add(full_name)
    return alias_to_full_names


def score_candidate(
    raw_target: str,
    normalized_target: str,
    compact_target: str,
    target_tokens: set[str],
    target_bucket: str,
    document: dict,
    alias_catalog: dict[str, set[str]],
) -> Candidate | None:
    title = document["title"]
    normalized_title = normalize_text(title)
    compact_title = compact_text(title)
    title_tokens = token_set(title)
    document_bucket = infer_document_bucket(document)

    score = 0.0
    method = "fuzzy"

    if normalized_target == normalized_title:
        score = 1.0
        method = "exact_title"
    elif compact_target == compact_title:
        score = 0.99
        method = "compact_title"
    else:
        expanded_full_names = alias_catalog.get(normalized_target, set()) | alias_catalog.get(compact_target, set())
        compact_expanded = {compact_text(name) for name in expanded_full_names}
        if normalized_title in expanded_full_names or compact_title in compact_expanded:
            score = 0.97
            method = "source_text_alias"
        elif compact_target in LOCAL_ALIAS_OVERRIDES and LOCAL_ALIAS_OVERRIDES[compact_target] == document["document_id"]:
            score = 0.98
            method = "override_alias"
        else:
            overlap = len(target_tokens & title_tokens)
            token_ratio = overlap / max(len(target_tokens), 1)
            seq_ratio = SequenceMatcher(None, compact_target, compact_title).ratio()
            contains_bonus = 0.0
            if compact_target and compact_target in compact_title:
                contains_bonus = 0.08
            elif compact_title and compact_title in compact_target:
                contains_bonus = 0.05
            score = seq_ratio * 0.55 + token_ratio * 0.35 + contains_bonus
            if token_ratio >= 0.75 and seq_ratio >= 0.55:
                method = "token_overlap"

    if target_bucket != "unknown" and document_bucket == target_bucket:
        score += 0.03
    elif target_bucket != "unknown" and document_bucket != target_bucket:
        score -= 0.08

    if score < 0.55:
        return None

    return Candidate(
        document_id=document["document_id"],
        title=title,
        document_type=document.get("document_type", ""),
        score=round(min(score, 1.0), 4),
        method=method,
    )


def resolve_relations(legal_documents: list[dict], relations: list[dict]) -> tuple[list[dict], list[dict], dict[str, set[str]]]:
    alias_catalog = build_alias_catalog(relations)
    resolved: list[dict] = []
    unresolved: list[dict] = []

    for rel in relations:
        if rel.get("relation_type") != "REFERS_TO_LAW_NAME":
            continue

        raw_target = rel["target_id"]
        normalized_target = normalize_text(raw_target)
        compact_target = compact_text(raw_target)
        target_tokens = token_set(raw_target)
        target_bucket = infer_target_type(raw_target)

        candidates = []
        for document in legal_documents:
            candidate = score_candidate(
                raw_target=raw_target,
                normalized_target=normalized_target,
                compact_target=compact_target,
                target_tokens=target_tokens,
                target_bucket=target_bucket,
                document=document,
                alias_catalog=alias_catalog,
            )
            if candidate is not None:
                candidates.append(candidate)

        candidates.sort(key=lambda item: (-item.score, item.title))
        best = candidates[0] if candidates else None
        second = candidates[1] if len(candidates) > 1 else None

        confidence = "high"
        if best is None:
            confidence = "none"
        elif best.score < 0.9 or (second and best.score - second.score < 0.08):
            confidence = "medium"
        if second and best and best.score - second.score < 0.03:
            confidence = "low"

        row = {
            "source_id": rel["source_id"],
            "raw_target_id": raw_target,
            "normalized_target_id": normalized_target,
            "target_bucket": target_bucket,
            "source_text": rel.get("source_text", ""),
            "candidates": [
                {
                    "document_id": item.document_id,
                    "title": item.title,
                    "document_type": item.document_type,
                    "score": item.score,
                    "method": item.method,
                }
                for item in candidates[:5]
            ],
        }

        if best and confidence in {"high", "medium"}:
            resolved.append(
                {
                    **row,
                    "matched_document_id": best.document_id,
                    "matched_document_title": best.title,
                    "score": best.score,
                    "method": best.method,
                    "confidence": confidence,
                }
            )
        else:
            unresolved.append(
                {
                    **row,
                    "confidence": confidence,
                }
            )

    return resolved, unresolved, alias_catalog


def main() -> int:
    legal_documents = load_legal_documents()
    relations = read_json(INTERNAL_RELATIONS_PATH)
    resolved, unresolved, alias_catalog = resolve_relations(legal_documents, relations)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    resolved_path = OUTPUT_DIR / "legal_reference_resolved.json"
    unresolved_path = OUTPUT_DIR / "legal_reference_unresolved.json"
    alias_catalog_path = OUTPUT_DIR / "legal_alias_catalog.json"
    summary_path = OUTPUT_DIR / "legal_reference_resolution_summary.json"

    resolved_path.write_text(json.dumps(resolved, ensure_ascii=False, indent=2), encoding="utf-8")
    unresolved_path.write_text(json.dumps(unresolved, ensure_ascii=False, indent=2), encoding="utf-8")
    alias_catalog_path.write_text(
        json.dumps({key: sorted(value) for key, value in sorted(alias_catalog.items())}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    confidence_counter = Counter(item["confidence"] for item in resolved)
    summary = {
        "resolved_count": len(resolved),
        "unresolved_count": len(unresolved),
        "confidence_breakdown": dict(confidence_counter),
        "top_unresolved": [
            {
                "raw_target_id": row["raw_target_id"],
                "normalized_target_id": row["normalized_target_id"],
                "target_bucket": row["target_bucket"],
            }
            for row in unresolved[:20]
        ],
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"resolved: {len(resolved)}")
    print(f"unresolved: {len(unresolved)}")
    print(f"alias_catalog: {len(alias_catalog)}")
    print(f"output_dir: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
