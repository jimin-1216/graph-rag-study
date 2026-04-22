from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "workspace" / "extracted" / "opendataloader"
OUTPUT_DIR = ROOT / "data" / "processed" / "internal_rules"

DOCUMENTS_PATH = OUTPUT_DIR / "internal_documents.json"
UNITS_PATH = OUTPUT_DIR / "internal_units.json"
RELATIONS_PATH = OUTPUT_DIR / "internal_relations.json"

TARGET_FILES = [
    "자금세탁방지업무 취급규정 원문-원본.json",
    "자금세탁방지업무 취급지침 원문-원본.json",
]

FILE_SLUGS = {
    "자금세탁방지업무 취급규정 원문-원본.pdf": "aml_policy",
    "자금세탁방지업무 취급지침 원문-원본.pdf": "aml_guideline",
}

ARTICLE_HEAD_RE = re.compile(r"^(제\d+(?:의\d+)?조)\(([^)]+)\)\s*(.*)$")
STRUCTURE_HEAD_RE = re.compile(r"^(제\d+편|제\d+장|제\d+절)\s+(.+)$")
LAW_NAME_PATTERN = re.compile(r"「([^」]+)」")
SHORT_LAW_PATTERN = re.compile(r"(특정금융정보법(?: 시행령)?|특정금융거래정보의 보고 및 이용 등에 관한 법률(?: 시행령)?|금융실명거래 및 비밀보장에 관한 법률|신용정보의 이용 및 보호에 관한 법률)")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def clean_text(value: object) -> str:
    if isinstance(value, list):
        return " ".join(clean_text(v) for v in value).strip()
    if isinstance(value, dict):
        if "content" in value:
            return clean_text(value["content"])
        return clean_text(list(value.values()))
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def make_document_id(slug: str) -> str:
    return f"internal:{slug}"


def make_unit_id(document_id: str, unit_type: str, unit_no: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z가-힣]+", "_", unit_no).strip("_")
    return f"{document_id}:{unit_type}:{normalized or 'root'}"


def flatten_item(item: dict) -> str:
    item_type = item.get("type", "")
    if item_type == "list":
        return " ".join(clean_text(li.get("content", "")) for li in item.get("list items", []))
    return clean_text(item.get("content", ""))


def split_circled(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩)", text))
    if not matches:
        return []
    rows = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        rows.append((match.group(1), clean_text(text[start:end])))
    return rows


def split_numbered(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?<!\d)(\d+\.)", text))
    if len(matches) <= 1:
        return []
    rows = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        rows.append((match.group(1), clean_text(text[start:end])))
    return rows


def split_korean(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"([가-하]\.)", text))
    if len(matches) <= 1:
        return []
    rows = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        rows.append((match.group(1), clean_text(text[start:end])))
    return rows


def append_reference_relations(source_id: str, text: str, relations: list[dict]) -> None:
    for law_name in LAW_NAME_PATTERN.findall(text):
        relations.append(
            {
                "source_id": source_id,
                "relation_type": "REFERS_TO_LAW_NAME",
                "target_id": law_name,
                "source_text": text,
            }
        )
    for law_name in SHORT_LAW_PATTERN.findall(text):
        relations.append(
            {
                "source_id": source_id,
                "relation_type": "REFERS_TO_LAW_NAME",
                "target_id": law_name,
                "source_text": text,
            }
        )


def build_article_blocks(payload: dict) -> tuple[list[dict], list[dict]]:
    headings = []
    articles = []
    current_article = None
    current_heading = ""

    for idx, item in enumerate(payload.get("kids", []), start=1):
        text = flatten_item(item)
        if not text:
            continue

        article_match = ARTICLE_HEAD_RE.match(text)
        structure_match = STRUCTURE_HEAD_RE.match(text)

        if article_match:
            if current_article:
                articles.append(current_article)
            article_no, article_title, rest = article_match.groups()
            current_article = {
                "article_no": article_no,
                "title": article_title,
                "heading_id": current_heading,
                "page": item.get("page number"),
                "parts": [text] if text else [],
            }
            continue

        if structure_match:
            heading_no, heading_title = structure_match.groups()
            current_heading = heading_no
            headings.append(
                {
                    "heading_no": heading_no,
                    "title": heading_title,
                    "text": text,
                    "page": item.get("page number"),
                }
            )
            continue

        if current_article is not None:
            current_article["parts"].append(text)

    if current_article:
        articles.append(current_article)

    return headings, articles


def normalize_document(path: Path) -> tuple[dict, list[dict], list[dict]]:
    payload = read_json(path)
    file_name = payload["file name"]
    slug = FILE_SLUGS[file_name]
    document_id = make_document_id(slug)

    document = {
        "document_id": document_id,
        "slug": slug,
        "document_type": "내규",
        "title": Path(file_name).stem,
        "promulgation_date": "",
        "effective_date": "",
        "department": "",
        "kind": "internal_rule",
        "source_file": file_name,
    }

    units: list[dict] = []
    relations: list[dict] = []

    headings, articles = build_article_blocks(payload)

    for heading in headings:
        heading_id = make_unit_id(document_id, "heading", heading["heading_no"])
        units.append(
            {
                "unit_id": heading_id,
                "document_id": document_id,
                "parent_unit_id": "",
                "unit_type": "heading",
                "unit_no": heading["heading_no"],
                "title": heading["title"],
                "text": heading["text"],
                "effective_date": "",
                "raw_key": "",
            }
        )
        relations.append({"source_id": document_id, "relation_type": "HAS_UNIT", "target_id": heading_id, "source_text": ""})

    for article in articles:
        article_text = clean_text(" ".join(article["parts"]))
        article_id = make_unit_id(document_id, "article", article["article_no"])
        parent_heading_id = make_unit_id(document_id, "heading", article["heading_id"]) if article["heading_id"] else ""
        units.append(
            {
                "unit_id": article_id,
                "document_id": document_id,
                "parent_unit_id": parent_heading_id,
                "unit_type": "article",
                "unit_no": article["article_no"],
                "title": article["title"],
                "text": article_text,
                "effective_date": "",
                "raw_key": "",
            }
        )
        if parent_heading_id:
            relations.append({"source_id": parent_heading_id, "relation_type": "HAS_CHILD", "target_id": article_id, "source_text": ""})
        else:
            relations.append({"source_id": document_id, "relation_type": "HAS_UNIT", "target_id": article_id, "source_text": ""})
        append_reference_relations(article_id, article_text, relations)

        paragraphs = split_circled(article_text)
        for p_idx, (p_no, p_text) in enumerate(paragraphs, start=1):
            paragraph_id = make_unit_id(document_id, "paragraph", f"{article['article_no']}_{p_no}_{p_idx}")
            units.append(
                {
                    "unit_id": paragraph_id,
                    "document_id": document_id,
                    "parent_unit_id": article_id,
                    "unit_type": "paragraph",
                    "unit_no": p_no,
                    "title": "",
                    "text": p_text,
                    "effective_date": "",
                    "raw_key": "",
                }
            )
            relations.append({"source_id": article_id, "relation_type": "HAS_CHILD", "target_id": paragraph_id, "source_text": ""})
            append_reference_relations(paragraph_id, p_text, relations)

            items = split_numbered(p_text)
            for i_idx, (i_no, i_text) in enumerate(items, start=1):
                item_id = make_unit_id(document_id, "item", f"{article['article_no']}_{p_no}_{i_no}_{i_idx}")
                units.append(
                    {
                        "unit_id": item_id,
                        "document_id": document_id,
                        "parent_unit_id": paragraph_id,
                        "unit_type": "item",
                        "unit_no": i_no,
                        "title": "",
                        "text": i_text,
                        "effective_date": "",
                        "raw_key": "",
                    }
                )
                relations.append({"source_id": paragraph_id, "relation_type": "HAS_CHILD", "target_id": item_id, "source_text": ""})
                append_reference_relations(item_id, i_text, relations)

                subitems = split_korean(i_text)
                for s_idx, (s_no, s_text) in enumerate(subitems, start=1):
                    subitem_id = make_unit_id(document_id, "subitem", f"{article['article_no']}_{p_no}_{i_no}_{s_no}_{s_idx}")
                    units.append(
                        {
                            "unit_id": subitem_id,
                            "document_id": document_id,
                            "parent_unit_id": item_id,
                            "unit_type": "subitem",
                            "unit_no": s_no,
                            "title": "",
                            "text": s_text,
                            "effective_date": "",
                            "raw_key": "",
                        }
                    )
                    relations.append({"source_id": item_id, "relation_type": "HAS_CHILD", "target_id": subitem_id, "source_text": ""})
                    append_reference_relations(subitem_id, s_text, relations)

    return document, units, relations


def main() -> int:
    documents = []
    units = []
    relations = []
    for file_name in TARGET_FILES:
        document, doc_units, doc_relations = normalize_document(INPUT_DIR / file_name)
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
