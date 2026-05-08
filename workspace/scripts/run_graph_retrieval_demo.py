from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path

from neo4j import GraphDatabase


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_DIR = ROOT / "workspace"
ENV_PATH = WORKSPACE_DIR / ".env"
OUTPUT_DIR = WORKSPACE_DIR / "queries"

DEFAULT_QUERIES = [
    "의심거래 보고 절차는 어떻게 되나",
    "고액 현금거래 보고 기한은?",
    "보고책임자의 역할은 무엇인가",
]

STOPWORDS = {
    "은",
    "는",
    "이",
    "가",
    "을",
    "를",
    "에",
    "의",
    "와",
    "과",
    "도",
    "로",
    "무엇",
    "무엇인가",
    "어떻게",
    "되나",
    "관련",
    "대한",
    "대해",
}

PHRASE_OVERRIDES = [
    "의심거래",
    "의심되는거래",
    "고액현금거래",
    "보고책임자",
    "담당책임자",
    "고객확인",
    "자금세탁방지",
]

DEADLINE_TERMS = ["이내", "영업일", "즉시", "지체 없이", "지체없이", "신속하게", "적시에"]
ROLE_TERMS = ["역할", "책임", "업무", "총괄", "수행", "보조"]
ROLE_TITLE_NEGATIVES = ["자료의 보존", "보존", "시행일", "부칙", "보고시기", "보고방법", "보고내용"]
ROLE_TEXT_NEGATIVES = ["보존", "기록", "서식"]
ROLE_BODY_PATTERNS = [
    "역할 및 책임",
    "책임은 다음 각 호와 같다",
    "역할은 다음 각 호와 같다",
    "총괄",
    "수행한다",
    "보조한다",
    "하여야 한다",
]
OTHER_SUBJECTS = ["이사회", "은행장", "감사", "준법감시인", "전담부서", "담당책임자"]

SUBJECT_CANONICAL_MAP = {
    "보고책임자": [
        "보고책임자",
        "보고 책임자",
        "보고의 책임자",
        "aml보고책임자",
    ],
    "담당책임자": [
        "담당책임자",
        "담당 책임자",
        "담당의 책임자",
    ],
    "전담부서": [
        "전담부서",
        "전담 부서",
    ],
    "고객확인": [
        "고객확인",
        "고객 확인",
    ],
    "고액현금거래": [
        "고액현금거래",
        "고액 현금거래",
    ],
    "의심거래": [
        "의심거래",
        "의심 거래",
        "의심되는거래",
        "의심되는 거래",
    ],
}

ROLE_WEIGHTS = {
    "subject_in_title": 5.0,
    "subject_in_lead": 4.5,
    "subject_in_text": 2.5,
    "role_term_in_title": 4.0,
    "role_term_in_text": 1.5,
    "role_pattern_in_text": 4.5,
    "enumeration_pattern": 2.0,
    "negative_title": -4.0,
    "negative_text": -1.5,
    "deadline_term": -1.0,
    "wrong_subject_title": -5.0,
    "wrong_subject_lead": -4.0,
    "article_type_bonus": 1.0,
    "paragraph_type_bonus": 0.5,
}

DEADLINE_WEIGHTS = {
    "deadline_term": 5.0,
    "deadline_title": 4.0,
    "report_title": 2.5,
    "subject_in_text": 1.0,
    "negative_title": -3.0,
    "article_type_bonus": 1.0,
    "paragraph_type_bonus": 0.5,
}

PROCEDURE_WEIGHTS = {
    "procedure_title": 5.5,
    "procedure_pattern": 3.5,
    "enumeration_pattern": 2.0,
    "subject_in_text": 1.0,
    "negative_title": -4.0,
    "negative_text": -2.0,
    "wrong_subject_title": -3.0,
    "wrong_subject_lead": -2.0,
    "article_type_bonus": 1.0,
    "paragraph_type_bonus": 0.5,
}


@dataclass
class QueryIntent:
    label: str
    subject: str


@dataclass
class QueryResult:
    query: str
    keywords: list[str]
    intent: QueryIntent
    top_internal_units: list[dict]
    linked_legal_documents: list[dict]
    issues: list[str]


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"`{name}` 환경변수가 필요합니다.")
    return value


def normalize_keyword(token: str) -> str:
    return re.sub(r"(은|는|이|가|을|를|의|에|와|과|도|로|인가|인가요|은가|는가|기한은|절차는|역할은)$", "", token)


def extract_keywords(query: str) -> list[str]:
    tokens = re.findall(r"[가-힣A-Za-z0-9]+", query)
    keywords: list[str] = []
    for token in tokens:
        token = normalize_keyword(token)
        if len(token) <= 1:
            continue
        if token in STOPWORDS:
            continue
        keywords.append(token)

    collapsed = query.replace(" ", "")
    for phrase in PHRASE_OVERRIDES:
        if phrase in collapsed and phrase not in keywords:
            keywords.append(phrase)

    deduped: list[str] = []
    seen = set()
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            deduped.append(keyword)
    return deduped


def infer_intent(query: str, keywords: list[str]) -> QueryIntent:
    subject = normalize_subject(query)

    if any(term in query for term in ["역할", "책임", "무엇"]):
        return QueryIntent(label="role", subject=subject)
    if any(term in query for term in ["기한", "시기", "언제", "이내"]):
        return QueryIntent(label="deadline", subject=subject)
    if any(term in query for term in ["절차", "방법", "흐름"]):
        return QueryIntent(label="procedure", subject=subject)
    return QueryIntent(label="generic", subject=subject)


def normalize_subject(text: str) -> str:
    compact = compact_korean(text)
    for canonical, variants in SUBJECT_CANONICAL_MAP.items():
        for variant in variants:
            if compact_korean(variant) in compact:
                return canonical
    return ""


def compact_korean(text: str) -> str:
    normalized = re.sub(r"[의는은이가을를와과도\s]+", "", text)
    return normalized


def subject_variant_hits(text: str, canonical_subject: str) -> int:
    if not canonical_subject:
        return 0
    compact = compact_korean(text)
    hits = 0
    for variant in SUBJECT_CANONICAL_MAP.get(canonical_subject, [canonical_subject]):
        if compact_korean(variant) in compact:
            hits += 1
    return hits


def search_internal_units(session, keywords: list[str], limit: int = 20) -> list[dict]:
    if not keywords:
        return []
    rows = session.run(
        """
        UNWIND $keywords AS kw
        MATCH (u:LegalUnit)-[:BELONGS_TO]->(d:LegalDocument {kind:'internal_rule'})
        WHERE u.unit_type IN ['article', 'paragraph', 'item', 'subitem', 'detail_item']
          AND (
            coalesce(u.text, '') CONTAINS kw
            OR coalesce(u.title, '') CONTAINS kw
            OR coalesce(d.title, '') CONTAINS kw
          )
        WITH u, d, collect(DISTINCT kw) AS matched_keywords
        RETURN
          u.unit_id AS unit_id,
          u.unit_type AS unit_type,
          u.unit_no AS unit_no,
          u.title AS title,
          u.text AS text,
          d.document_id AS document_id,
          d.title AS document_title,
          matched_keywords,
          size(matched_keywords) AS base_score
        ORDER BY base_score DESC,
                 CASE u.unit_type
                   WHEN 'article' THEN 1
                   WHEN 'paragraph' THEN 2
                   WHEN 'item' THEN 3
                   WHEN 'subitem' THEN 4
                   WHEN 'detail_item' THEN 5
                   ELSE 99
                 END ASC,
                 size(coalesce(u.text, '')) ASC
        LIMIT $limit
        """,
        keywords=keywords,
        limit=limit,
    ).data()
    return rows


def count_matches(text: str, patterns: list[str]) -> int:
    return sum(1 for pattern in patterns if pattern and pattern in text)


def leading_text(text: str, limit: int = 120) -> str:
    return (text or "")[:limit]


def build_features(intent: QueryIntent, row: dict) -> dict[str, float]:
    title = row.get("title") or ""
    text = row.get("text") or ""
    lead = leading_text(text)
    unit_type = row.get("unit_type") or ""
    subject = intent.subject or ""

    features: dict[str, float] = {}

    if subject:
        if subject_variant_hits(title, subject):
            features["subject_in_title"] = 1.0
        if subject_variant_hits(lead, subject):
            features["subject_in_lead"] = 1.0
        subject_hits = subject_variant_hits(text, subject)
        if subject_hits:
            features["subject_in_text"] = float(min(subject_hits, 3))

    if unit_type == "article":
        features["article_type_bonus"] = 1.0
    elif unit_type == "paragraph":
        features["paragraph_type_bonus"] = 1.0

    if intent.label == "role":
        role_title_hits = count_matches(title, ROLE_TERMS)
        role_text_hits = count_matches(text, ROLE_TERMS)
        role_pattern_hits = count_matches(text, ROLE_BODY_PATTERNS)
        negative_title_hits = count_matches(title, ROLE_TITLE_NEGATIVES)
        negative_text_hits = count_matches(text, ROLE_TEXT_NEGATIVES)
        enumeration_hits = 1.0 if re.search(r"다음 각 호와 같다|1\.\s|2\.\s", text) else 0.0
        deadline_hits = sum(1 for term in DEADLINE_TERMS if term in text)
        wrong_subject_title_hits = 0
        wrong_subject_lead_hits = 0

        for other in OTHER_SUBJECTS:
            if other == subject:
                continue
            if subject_variant_hits(title, other):
                wrong_subject_title_hits += 1
            if subject_variant_hits(lead, other):
                wrong_subject_lead_hits += 1

        if role_title_hits:
            features["role_term_in_title"] = float(role_title_hits)
        if role_text_hits:
            features["role_term_in_text"] = float(min(role_text_hits, 3))
        if role_pattern_hits:
            features["role_pattern_in_text"] = float(min(role_pattern_hits, 3))
        if enumeration_hits:
            features["enumeration_pattern"] = enumeration_hits
        if negative_title_hits:
            features["negative_title"] = float(negative_title_hits)
        if negative_text_hits:
            features["negative_text"] = float(min(negative_text_hits, 2))
        if deadline_hits:
            features["deadline_term"] = float(min(deadline_hits, 2))
        if wrong_subject_title_hits:
            features["wrong_subject_title"] = float(min(wrong_subject_title_hits, 2))
        if wrong_subject_lead_hits:
            features["wrong_subject_lead"] = float(min(wrong_subject_lead_hits, 2))

    elif intent.label == "deadline":
        deadline_hits = sum(1 for term in DEADLINE_TERMS if term in text)
        deadline_title_hits = count_matches(title, ["보고시기", "보고기한", "시기", "기한", "방법"])
        report_title_hits = count_matches(title, ["보고", "고액 현금거래", "의심되는 거래"])
        negative_title_hits = count_matches(title, ["보존대상", "자료의 보존", "보존", "서식", "보고내용"])

        if deadline_hits:
            features["deadline_term"] = float(min(deadline_hits, 3))
        if deadline_title_hits:
            features["deadline_title"] = float(deadline_title_hits)
        if report_title_hits:
            features["report_title"] = float(report_title_hits)
        if negative_title_hits:
            features["negative_title"] = float(negative_title_hits)

    elif intent.label == "procedure":
        procedure_title_hits = count_matches(title, ["절차", "방법", "제도운용", "모니터링 결과분석 및 보고", "보고시기 및 방법"])
        procedure_pattern_hits = count_matches(text, ["절차는 다음 각 호와 같다", "방법은 다음 각 호와 같다", "다음 각 호와 같다"])
        enumeration_hits = 1.0 if re.search(r"1\.\s|2\.\s|가\.\s|나\.\s", text) else 0.0
        negative_title_hits = count_matches(title, ["정의", "시행일", "자료의 보존", "보존", "보고내용", "보고대상"])
        negative_text_hits = count_matches(text, ["보고하여야 할 내용", "보존하여야 할 자료", "보존대상"])
        wrong_subject_title_hits = count_matches(title, ["이사회", "은행장", "감사"])
        wrong_subject_lead_hits = count_matches(lead, ["이사회", "은행장", "감사"])

        if procedure_title_hits:
            features["procedure_title"] = float(procedure_title_hits)
        if procedure_pattern_hits:
            features["procedure_pattern"] = float(procedure_pattern_hits)
        if enumeration_hits:
            features["enumeration_pattern"] = enumeration_hits
        if negative_title_hits:
            features["negative_title"] = float(negative_title_hits)
        if negative_text_hits:
            features["negative_text"] = float(min(negative_text_hits, 2))
        if wrong_subject_title_hits:
            features["wrong_subject_title"] = float(min(wrong_subject_title_hits, 2))
        if wrong_subject_lead_hits:
            features["wrong_subject_lead"] = float(min(wrong_subject_lead_hits, 2))

    return features


def score_row(intent: QueryIntent, row: dict) -> tuple[float, dict[str, float]]:
    features = build_features(intent, row)
    score = float(row.get("base_score", 0))

    if intent.label == "role":
        weights = ROLE_WEIGHTS
    elif intent.label == "deadline":
        weights = DEADLINE_WEIGHTS
    elif intent.label == "procedure":
        weights = PROCEDURE_WEIGHTS
    else:
        weights = {}

    for name, value in features.items():
        score += weights.get(name, 0.0) * value

    return score, features


def rerank_internal_units(intent: QueryIntent, rows: list[dict], limit: int = 8) -> list[dict]:
    reranked = []
    for row in rows:
        score, features = score_row(intent, row)
        reranked.append(
            {
                **row,
                "score": round(score, 2),
                "features": features,
            }
        )

    reranked.sort(
        key=lambda row: (
            -row["score"],
            -row.get("base_score", 0),
            0 if row["unit_type"] == "article" else 1,
            len(row.get("text") or ""),
        )
    )
    return reranked[:limit]


def expand_legal_documents(session, unit_ids: list[str]) -> list[dict]:
    if not unit_ids:
        return []
    return session.run(
        """
        UNWIND $unit_ids AS unit_id
        MATCH (u:LegalUnit {unit_id: unit_id})-[:BELONGS_TO]->(src:LegalDocument)

        OPTIONAL MATCH (u)-[resolved:REFERS_TO_DOCUMENT]->(resolved_doc:LegalDocument)
        OPTIONAL MATCH (src)-[doc_rel:IMPLEMENTS_RESOLVED]->(doc_target:LegalDocument)

        OPTIONAL MATCH (u)-[lr:LEGAL_REFERENCE]->(ref:LegalReference)
        OPTIONAL MATCH (fallback_doc:LegalDocument)
        WHERE fallback_doc.kind <> 'internal_rule'
          AND (
            fallback_doc.title = ref.target_id
            OR fallback_doc.title CONTAINS ref.target_id
            OR ref.target_id CONTAINS fallback_doc.title
          )

        WITH
          u,
          src,
          collect(DISTINCT CASE
            WHEN resolved_doc IS NULL THEN NULL
            ELSE {
              relation_type: 'REFERS_TO_DOCUMENT',
              raw_target_id: resolved.raw_target_id,
              matched_document_id: resolved_doc.document_id,
              matched_document_title: resolved_doc.title,
              method: resolved.method,
              score: resolved.score,
              confidence: resolved.confidence
            }
          END) AS resolved_refs,
          collect(DISTINCT CASE
            WHEN doc_target IS NULL THEN NULL
            ELSE {
              relation_type: type(doc_rel),
              matched_document_id: doc_target.document_id,
              matched_document_title: doc_target.title,
              method: doc_rel.method,
              score: doc_rel.best_score,
              confidence: doc_rel.confidence
            }
          END) AS document_links,
          collect(DISTINCT CASE
            WHEN fallback_doc IS NULL THEN NULL
            ELSE {
              relation_type: lr.relation_type,
              raw_target_id: ref.target_id,
              matched_document_id: fallback_doc.document_id,
              matched_document_title: fallback_doc.title
            }
          END) AS fallback_refs
        RETURN
          u.unit_id AS unit_id,
          src.document_id AS source_document_id,
          src.title AS source_document_title,
          [x IN resolved_refs WHERE x IS NOT NULL] AS resolved_refs,
          [x IN document_links WHERE x IS NOT NULL] AS document_links,
          [x IN fallback_refs WHERE x IS NOT NULL] AS fallback_refs
        """,
        unit_ids=unit_ids,
    ).data()


def evaluate_issues(query: str, intent: QueryIntent, keywords: list[str], internal_units: list[dict], linked_docs: list[dict]) -> list[str]:
    issues: list[str] = []

    if not keywords:
        issues.append("키워드 추출 결과가 비어 있음")

    if not internal_units:
        issues.append("내부문서 검색 결과가 없음")
        return issues

    top = internal_units[0]
    if top["score"] <= 1:
        issues.append("상위 검색 결과 점수가 낮아 질의 의도와의 정합성이 약함")

    linked_resolved = sum(len(row["resolved_refs"]) for row in linked_docs)
    linked_doc_level = sum(len(row["document_links"]) for row in linked_docs)
    linked_fallback = sum(len(row["fallback_refs"]) for row in linked_docs)

    if linked_resolved == 0 and linked_doc_level == 0:
        issues.append("해소된 그래프 관계 기준 상위 법령 확장이 약함")

    if linked_resolved == 0 and linked_fallback > 0:
        issues.append("문자열 fallback으로만 법령이 잡혀 alias 해소 범위가 아직 부족함")

    if linked_resolved == 0 and linked_doc_level > 0:
        issues.append("조문 직접 참조 없이 문서 수준 연결만 보여 상위법 근거가 넓게 제시됨")

    if intent.label == "deadline":
        if not any(term in (row.get("text") or "") for row in internal_units for term in DEADLINE_TERMS):
            issues.append("기한성 표현이 상위 후보에서 충분히 잡히지 않음")

    if intent.label == "role":
        title = top.get("title") or ""
        text = top.get("text") or ""
        if intent.subject and intent.subject not in title and intent.subject not in text:
            issues.append("역할 질의인데 상위 후보에서 주체가 약하게 드러남")
        if not any(term in text for term in ROLE_TERMS):
            issues.append("역할/책임 서술 패턴보다 주변 조문이 상위에 올 가능성이 있음")

    if intent.label == "procedure":
        if not re.search(r"다음 각 호와 같다|1\.\s|2\.\s", top.get("text") or ""):
            issues.append("절차 질의인데 단계형 서술이 상위에서 약함")

    return issues


def run_query(session, query: str) -> QueryResult:
    keywords = extract_keywords(query)
    intent = infer_intent(query, keywords)
    raw_units = search_internal_units(session, keywords)
    internal_units = rerank_internal_units(intent, raw_units)
    linked_docs = expand_legal_documents(session, [row["unit_id"] for row in internal_units[:5]])
    issues = evaluate_issues(query, intent, keywords, internal_units, linked_docs)
    return QueryResult(
        query=query,
        keywords=keywords,
        intent=intent,
        top_internal_units=internal_units,
        linked_legal_documents=linked_docs,
        issues=issues,
    )


def format_features(features: dict[str, float]) -> str:
    if not features:
        return "-"
    return ", ".join(f"{key}={value}" for key, value in features.items())


def write_report(results: list[QueryResult], output_path: Path) -> None:
    lines = ["# Graph Retrieval Eval", "", "작성일: 2026-04-24", ""]
    for idx, result in enumerate(results, start=1):
        lines.append(f"## Query {idx}")
        lines.append("")
        lines.append(f"- 질문: `{result.query}`")
        lines.append(f"- 의도: `{result.intent.label}`")
        lines.append(f"- 주체: `{result.intent.subject or '-'} `")
        lines.append(f"- 키워드: `{', '.join(result.keywords)}`")
        lines.append("")
        lines.append("### 상위 내부규정 검색 결과")
        lines.append("")
        if result.top_internal_units:
            for row in result.top_internal_units[:5]:
                snippet = (row.get("text") or "")[:240].replace("\n", " ")
                lines.append(
                    f"- `{row['document_title']} / {row['unit_no']} / {row['unit_type']}` "
                    f"score={row['score']} base={row['base_score']} keywords={','.join(row['matched_keywords'])}"
                )
                lines.append(f"  - features: {format_features(row.get('features', {}))}")
                lines.append(f"  - {snippet}")
        else:
            lines.append("- 결과 없음")

        lines.append("")
        lines.append("### 상위 법령 확장")
        lines.append("")
        expanded = False
        for row in result.linked_legal_documents[:5]:
            resolved_refs = row["resolved_refs"]
            document_links = row["document_links"]
            fallback_refs = row["fallback_refs"]
            if not resolved_refs and not document_links and not fallback_refs:
                continue
            expanded = True
            lines.append(f"- `{row['unit_id']}`")
            for match in resolved_refs:
                lines.append(
                    f"  - REFERS_TO_DOCUMENT `{match['raw_target_id']}` -> `{match['matched_document_title']}` "
                    f"(method={match['method']}, score={match['score']})"
                )
            if not resolved_refs:
                for match in document_links[:3]:
                    lines.append(
                        f"  - {match['relation_type']} -> `{match['matched_document_title']}` "
                        f"(method={match['method']}, score={match['score']})"
                    )
            if not resolved_refs:
                for match in fallback_refs[:3]:
                    lines.append(
                        f"  - FALLBACK {match['relation_type']} `{match['raw_target_id']}` -> `{match['matched_document_title']}`"
                    )
        if not expanded:
            lines.append("- 연결된 상위 법령 후보가 충분히 나오지 않음")

        lines.append("")
        lines.append("### 관찰된 문제")
        lines.append("")
        if result.issues:
            for issue in result.issues:
                lines.append(f"- {issue}")
        else:
            lines.append("- 뚜렷한 문제 없음")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", action="append", dest="queries")
    parser.add_argument("--output", default=str(OUTPUT_DIR / "graph_retrieval_eval_2026-04-24.md"))
    args = parser.parse_args()

    queries = args.queries or DEFAULT_QUERIES

    load_dotenv(ENV_PATH)
    driver = GraphDatabase.driver(
        require_env("NEO4J_URI"),
        auth=(require_env("NEO4J_USERNAME"), require_env("NEO4J_PASSWORD")),
    )
    database = os.environ.get("NEO4J_DATABASE", "neo4j").strip() or "neo4j"

    try:
        with driver.session(database=database) as session:
            results = [run_query(session, query) for query in queries]
    finally:
        driver.close()

    output_path = Path(args.output)
    write_report(results, output_path)

    print(f"queries: {len(queries)}")
    print(f"output: {output_path}")
    for result in results:
        print(
            f"- {result.query}: intent={result.intent.label}, "
            f"keywords={result.keywords}, hits={len(result.top_internal_units)}, issues={len(result.issues)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
