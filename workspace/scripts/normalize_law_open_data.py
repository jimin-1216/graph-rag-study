from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "legal" / "raw"
PROCESSED_DIR = ROOT / "data" / "legal" / "processed"
MANIFEST_PATH = PROCESSED_DIR / "law_open_data_manifest.json"

DOCUMENTS_PATH = PROCESSED_DIR / "legal_documents.json"
UNITS_PATH = PROCESSED_DIR / "legal_units.json"
RELATIONS_PATH = PROCESSED_DIR / "legal_relations.json"

LAW_NAME_PATTERN = re.compile(r"「([^」]+)」")
ARTICLE_REF_PATTERN = re.compile(r"제\s*\d+(?:의\d+)?조(?:의\d+)?(?:제\s*\d+항)?(?:제\s*\d+호)?(?:제\s*\d+목)?")
ADMIN_ARTICLE_PATTERN = re.compile(r"^(제\d+(?:의\d+)?조)\(([^)]+)\)\s*(.*)$")
HEADING_PATTERN = re.compile(r"^(제\d+편|제\d+장|제\d+절)\s+(.+)$")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_list(value: object) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    return []


def clean_text(value: object) -> str:
    if isinstance(value, list):
        return " ".join(clean_text(item) for item in value).strip()
    if value is None:
        return ""
    if isinstance(value, dict):
        if "content" in value:
            return clean_text(value["content"])
        return clean_text(list(value.values()))
    return re.sub(r"\s+", " ", str(value)).strip()


def slug_from_path(path: str) -> str:
    name = Path(path).name
    suffixes = ["_body.json", "_search.json", "_structure.json"]
    for suffix in suffixes:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return Path(path).stem


def make_document_id(slug: str) -> str:
    return f"law:{slug}"


def make_unit_id(document_id: str, unit_type: str, unit_no: str) -> str:
    normalized_no = re.sub(r"[^0-9A-Za-z가-힣]+", "_", unit_no).strip("_")
    return f"{document_id}:{unit_type}:{normalized_no or 'root'}"


def append_relation(
    relations: list[dict[str, str]],
    source_id: str,
    relation_type: str,
    target_id: str,
    source_text: str = "",
) -> None:
    relations.append(
        {
            "source_id": source_id,
            "relation_type": relation_type,
            "target_id": target_id,
            "source_text": source_text,
        }
    )


def extract_citation_relations(source_id: str, text: str, relations: list[dict[str, str]]) -> None:
    if not text:
        return

    for law_name in LAW_NAME_PATTERN.findall(text):
        append_relation(
            relations,
            source_id=source_id,
            relation_type="REFERS_TO_LAW_NAME",
            target_id=law_name,
            source_text=text,
        )

    for article_ref in ARTICLE_REF_PATTERN.findall(text):
        append_relation(
            relations,
            source_id=source_id,
            relation_type="CITES_ARTICLE_TEXT",
            target_id=article_ref.replace(" ", ""),
            source_text=text,
        )


def normalize_law_document(meta: dict, body_payload: dict, structure_payload: dict) -> tuple[dict, list[dict], list[dict]]:
    law = body_payload["법령"]
    basic = law["기본정보"]
    slug = meta["slug"]
    document_id = make_document_id(slug)

    document = {
        "document_id": document_id,
        "slug": slug,
        "document_type": clean_text(basic.get("법종구분", "")),
        "title": clean_text(basic.get("법령명_한글", "")),
        "title_hanja": clean_text(basic.get("법령명_한자", "")),
        "promulgation_date": basic.get("공포일자", ""),
        "effective_date": basic.get("시행일자", ""),
        "department": clean_text(basic.get("소관부처", "")),
        "law_id": meta.get("law_id", ""),
        "mst": meta.get("mst", ""),
        "kind": "law",
    }

    units: list[dict] = []
    relations: list[dict] = []

    for article in ensure_list(law.get("조문", {}).get("조문단위", [])):
        unit_kind = "article" if article.get("조문여부") == "조문" else "heading"
        article_no = article.get("조문번호", "")
        article_id = make_unit_id(document_id, unit_kind, article_no)
        article_text = clean_text(article.get("조문내용", ""))
        units.append(
            {
                "unit_id": article_id,
                "document_id": document_id,
                "parent_unit_id": "",
                "unit_type": unit_kind,
                "unit_no": article_no,
                "title": clean_text(article.get("조문제목", "")),
                "text": article_text,
                "effective_date": article.get("조문시행일자", ""),
                "raw_key": article.get("조문키", ""),
            }
        )
        append_relation(relations, document_id, "HAS_UNIT", article_id)
        extract_citation_relations(article_id, article_text, relations)

        paragraph_payload = article.get("항")
        if not paragraph_payload:
            continue

        paragraphs = ensure_list(paragraph_payload)
        for paragraph in paragraphs:
            if not isinstance(paragraph, dict):
                continue

            has_paragraph_number = "항번호" in paragraph or "항내용" in paragraph
            paragraph_parent_id = article_id
            paragraph_id = article_id

            if has_paragraph_number:
                paragraph_no = clean_text(paragraph.get("항번호", ""))
                paragraph_id = make_unit_id(document_id, "paragraph", f"{article_no}_{paragraph_no}")
                paragraph_text = clean_text(paragraph.get("항내용", ""))
                units.append(
                    {
                        "unit_id": paragraph_id,
                        "document_id": document_id,
                        "parent_unit_id": article_id,
                        "unit_type": "paragraph",
                        "unit_no": paragraph_no,
                        "title": "",
                        "text": paragraph_text,
                        "effective_date": article.get("조문시행일자", ""),
                        "raw_key": article.get("조문키", ""),
                    }
                )
                append_relation(relations, article_id, "HAS_CHILD", paragraph_id)
                extract_citation_relations(paragraph_id, paragraph_text, relations)
                paragraph_parent_id = paragraph_id

            for item in ensure_list(paragraph.get("호")):
                if not isinstance(item, dict):
                    continue
                item_no = clean_text(item.get("호번호", ""))
                item_text = clean_text(item.get("호내용", ""))
                item_id = make_unit_id(document_id, "item", f"{article_no}_{item_no}")
                units.append(
                    {
                        "unit_id": item_id,
                        "document_id": document_id,
                        "parent_unit_id": paragraph_parent_id,
                        "unit_type": "item",
                        "unit_no": item_no,
                        "title": "",
                        "text": item_text,
                        "effective_date": article.get("조문시행일자", ""),
                        "raw_key": article.get("조문키", ""),
                    }
                )
                append_relation(relations, paragraph_parent_id, "HAS_CHILD", item_id)
                extract_citation_relations(item_id, item_text, relations)

                for subitem in ensure_list(item.get("목")):
                    if not isinstance(subitem, dict):
                        continue
                    subitem_no = clean_text(subitem.get("목번호", ""))
                    subitem_text = clean_text(subitem.get("목내용", ""))
                    subitem_id = make_unit_id(document_id, "subitem", f"{article_no}_{item_no}_{subitem_no}")
                    units.append(
                        {
                            "unit_id": subitem_id,
                            "document_id": document_id,
                            "parent_unit_id": item_id,
                            "unit_type": "subitem",
                            "unit_no": subitem_no,
                            "title": "",
                            "text": subitem_text,
                            "effective_date": article.get("조문시행일자", ""),
                            "raw_key": article.get("조문키", ""),
                        }
                    )
                    append_relation(relations, item_id, "HAS_CHILD", subitem_id)
                    extract_citation_relations(subitem_id, subitem_text, relations)

    extract_structure_relations(document_id, structure_payload, relations)
    return document, units, relations


def split_admin_article_line(line: str) -> tuple[str, str, str] | None:
    match = ADMIN_ARTICLE_PATTERN.match(line)
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3).strip()


def normalize_admin_rule(meta: dict, body_payload: dict) -> tuple[dict, list[dict], list[dict]]:
    service = body_payload["AdmRulService"]
    basic = service["행정규칙기본정보"]
    slug = meta["slug"]
    document_id = make_document_id(slug)

    document = {
        "document_id": document_id,
        "slug": slug,
        "document_type": clean_text(basic.get("행정규칙종류", "")),
        "title": clean_text(basic.get("행정규칙명", "")),
        "promulgation_date": basic.get("발령일자", ""),
        "effective_date": basic.get("시행일자", ""),
        "department": clean_text(basic.get("소관부처명", "")),
        "rule_id": meta.get("rule_id", ""),
        "kind": "adm_rule",
    }

    units: list[dict] = []
    relations: list[dict] = []
    current_heading_id = ""

    for idx, raw_line in enumerate(ensure_list(service.get("조문내용", [])), start=1):
        line = clean_text(raw_line)
        if not line:
            continue

        heading_match = HEADING_PATTERN.match(line)
        if heading_match:
            heading_no = heading_match.group(1)
            heading_id = make_unit_id(document_id, "heading", heading_no)
            units.append(
                {
                    "unit_id": heading_id,
                    "document_id": document_id,
                    "parent_unit_id": "",
                    "unit_type": "heading",
                    "unit_no": heading_no,
                    "title": clean_text(heading_match.group(2)),
                    "text": line,
                    "effective_date": basic.get("시행일자", ""),
                    "raw_key": f"line_{idx}",
                }
            )
            append_relation(relations, document_id, "HAS_UNIT", heading_id)
            current_heading_id = heading_id
            continue

        article_match = split_admin_article_line(line)
        if article_match:
            article_no, article_title, article_body = article_match
            article_id = make_unit_id(document_id, "article", article_no)
            units.append(
                {
                    "unit_id": article_id,
                    "document_id": document_id,
                    "parent_unit_id": current_heading_id,
                    "unit_type": "article",
                    "unit_no": article_no,
                    "title": article_title,
                    "text": line,
                    "effective_date": basic.get("시행일자", ""),
                    "raw_key": f"line_{idx}",
                }
            )
            if current_heading_id:
                append_relation(relations, current_heading_id, "HAS_CHILD", article_id)
            else:
                append_relation(relations, document_id, "HAS_UNIT", article_id)
            extract_citation_relations(article_id, line, relations)

            paragraph_splits = split_circled_paragraphs(article_body)
            if paragraph_splits:
                for paragraph_no, paragraph_text in paragraph_splits:
                    paragraph_id = make_unit_id(document_id, "paragraph", f"{article_no}_{paragraph_no}")
                    units.append(
                        {
                            "unit_id": paragraph_id,
                            "document_id": document_id,
                            "parent_unit_id": article_id,
                            "unit_type": "paragraph",
                            "unit_no": paragraph_no,
                            "title": "",
                            "text": paragraph_text,
                            "effective_date": basic.get("시행일자", ""),
                            "raw_key": f"line_{idx}",
                        }
                    )
                    append_relation(relations, article_id, "HAS_CHILD", paragraph_id)
                    extract_citation_relations(paragraph_id, paragraph_text, relations)
                    for item_no, item_text in split_numbered_items(paragraph_text):
                        item_id = make_unit_id(document_id, "item", f"{article_no}_{paragraph_no}_{item_no}")
                        units.append(
                            {
                                "unit_id": item_id,
                                "document_id": document_id,
                                "parent_unit_id": paragraph_id,
                                "unit_type": "item",
                                "unit_no": item_no,
                                "title": "",
                                "text": item_text,
                                "effective_date": basic.get("시행일자", ""),
                                "raw_key": f"line_{idx}",
                            }
                        )
                        append_relation(relations, paragraph_id, "HAS_CHILD", item_id)
                        extract_citation_relations(item_id, item_text, relations)
            continue

    return document, units, relations


def split_circled_paragraphs(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩)", text))
    if not matches:
        return []
    parts: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        marker = match.group(1)
        content = clean_text(text[start:end])
        parts.append((marker, content))
    return parts


def split_numbered_items(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(\d+\.)", text))
    if len(matches) <= 1:
        return []
    parts: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        marker = match.group(1)
        content = clean_text(text[start:end])
        parts.append((marker, content))
    return parts


def extract_structure_relations(document_id: str, structure_payload: dict, relations: list[dict]) -> None:
    system = structure_payload.get("법령체계도", {})
    if not system:
        return

    parent_basic = system.get("기본정보", {})
    walk_structure_node(document_id, parent_basic, system.get("상하위법", {}), relations)


def walk_structure_node(
    root_document_id: str,
    current_basic: dict,
    node: object,
    relations: list[dict],
) -> None:
    if isinstance(node, list):
        for item in node:
            walk_structure_node(root_document_id, current_basic, item, relations)
        return

    if not isinstance(node, dict):
        return

    basic = node.get("기본정보")
    if isinstance(basic, dict):
        title = basic.get("법령명") or basic.get("행정규칙명")
        if title:
            relation_type = "IMPLEMENTS_CANDIDATE"
            append_relation(relations, root_document_id, relation_type, title)

    for key, value in node.items():
        if key == "기본정보":
            continue
        walk_structure_node(root_document_id, current_basic, value, relations)


def main() -> int:
    manifest = read_json(MANIFEST_PATH)
    documents: list[dict] = []
    units: list[dict] = []
    relations: list[dict] = []

    for target in manifest["targets"]:
        body_path = Path(target["body_path"])
        body_payload = read_json(body_path)

        if target["kind"] == "law":
            structure_path = Path(target["structure_path"])
            structure_payload = read_json(structure_path)
            document, doc_units, doc_relations = normalize_law_document(target, body_payload, structure_payload)
        else:
            document, doc_units, doc_relations = normalize_admin_rule(target, body_payload)

        documents.append(document)
        units.extend(doc_units)
        relations.extend(doc_relations)

    write_json(DOCUMENTS_PATH, documents)
    write_json(UNITS_PATH, units)
    write_json(RELATIONS_PATH, relations)

    print(f"documents: {len(documents)}")
    print(f"units: {len(units)}")
    print(f"relations: {len(relations)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
