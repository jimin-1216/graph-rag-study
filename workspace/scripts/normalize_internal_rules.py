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
    "자금세탁방지업무 취급규정 원문-원본.md",
    "자금세탁방지업무 취급지침 원문-원본.md",
]

FILE_SLUGS = {
    "자금세탁방지업무 취급규정 원문-원본.md": "aml_policy",
    "자금세탁방지업무 취급지침 원문-원본.md": "aml_guideline",
}

ARTICLE_RE = re.compile(r"^(?:-+\s*)?(제\d+(?:의\d+)?조)\(([^)]+)\)\s*(.*)$")
STRUCTURE_RE = re.compile(r"^(제\d+(?:편|장|절))\s+(.+)$")
SUPPLEMENTARY_RE = re.compile(r"^(?:#+\s*)?부칙(?:<[^>]+>)?\s*$")
APPENDIX_RE = re.compile(r"^(?:-+\s*)?\[?(별표|별지서식)\s*([0-9]+)?\]?\s*(.*)$")
LAW_NAME_PATTERN = re.compile(r"「([^」]+)」")
SHORT_LAW_PATTERN = re.compile(
    r"(특정금융정보법(?: 시행령)?|특정금융거래정보의 보고 및 이용 등에 관한 법률(?: 시행령)?|"
    r"금융실명거래 및 비밀보장에 관한 법률|신용정보의 이용 및 보호에 관한 법률|"
    r"자금세탁방지 및 공중협박자금조달금지에 관한 업무규정|자금세탁방지업무 취급규정)"
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def clean_text(value: str) -> str:
    value = value.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", value).strip()


def normalize_line(line: str) -> str:
    return clean_text(line.lstrip("#").strip())


def make_document_id(slug: str) -> str:
    return f"internal:{slug}"


def make_unit_id(document_id: str, unit_type: str, unit_no: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z가-힣]+", "_", unit_no).strip("_")
    return f"{document_id}:{unit_type}:{normalized or 'root'}"


def split_circled(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩)", text))
    if not matches:
        return []
    rows = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        rows.append((match.group(1), text[start:end].strip()))
    return rows


def split_numbered(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?m)(?:^|\n)\s*-?\s*(\d+\.)\s+", text))
    if not matches:
        return []
    rows = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        rows.append((match.group(1), text[start:end].strip()))
    return rows


def split_korean(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?m)(?:^|\n|\s-\s*)([가-하]\.)\s+", text))
    if not matches:
        return []
    rows = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        rows.append((match.group(1), text[start:end].strip()))
    return rows


def split_paren_number(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?m)(?:^|\n|\s-\s*)(\d+\))\s+", text))
    if not matches:
        return []
    rows = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        rows.append((match.group(1), text[start:end].strip()))
    return rows


def append_reference_relations(source_id: str, text: str, relations: list[dict]) -> None:
    seen = set()
    for law_name in LAW_NAME_PATTERN.findall(text):
        if law_name in seen:
            continue
        seen.add(law_name)
        relations.append(
            {
                "source_id": source_id,
                "relation_type": "REFERS_TO_LAW_NAME",
                "target_id": law_name,
                "source_text": text,
            }
        )
    for law_name in SHORT_LAW_PATTERN.findall(text):
        if law_name in seen:
            continue
        seen.add(law_name)
        relations.append(
            {
                "source_id": source_id,
                "relation_type": "REFERS_TO_LAW_NAME",
                "target_id": law_name,
                "source_text": text,
            }
        )


def sanitize_for_children(text: str) -> str:
    text = re.sub(r"<[^>]*(개정|신설|삭제|본조신설)[^>]*>", " ", text)
    text = re.sub(r"\[[^\]]*(개정|신설|삭제|본조신설)[^\]]*\]", " ", text)
    return text


def trim_at_next_article(text: str) -> str:
    match = re.search(r"(?m)\n\s*-?\s*(제\d+(?:의\d+)?조)\(", text)
    if match:
        return text[: match.start()].strip()
    return text.strip()


def should_skip_preamble(line: str) -> bool:
    if not line:
        return True
    if re.match(r"^\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.?\s+제?\d+차?\s*(개정|제정)", line):
        return True
    if line == "(전부개정)":
        return True
    return False


def build_blocks(markdown: str) -> tuple[list[dict], list[dict], list[dict]]:
    headings: list[dict] = []
    articles: list[dict] = []
    extras: list[dict] = []

    current_article: dict | None = None
    current_extra: dict | None = None
    heading_stack: list[dict] = []
    started = False
    extra_seq = 0

    def flush_article() -> None:
        nonlocal current_article
        if current_article:
            current_article["raw_text"] = "\n".join(current_article["parts"])
            current_article["text"] = clean_text(current_article["raw_text"])
            articles.append(current_article)
            current_article = None

    def flush_extra() -> None:
        nonlocal current_extra
        if current_extra:
            current_extra["text"] = clean_text(" ".join(current_extra["parts"]))
            extras.append(current_extra)
            current_extra = None

    for raw_line in markdown.splitlines():
        line = normalize_line(raw_line)
        if not line:
            continue

        structure_match = STRUCTURE_RE.match(line)
        article_match = ARTICLE_RE.match(line)
        supplementary_match = SUPPLEMENTARY_RE.match(line)
        appendix_match = APPENDIX_RE.match(line)

        if not started:
            if structure_match or article_match:
                started = True
            else:
                continue

        if should_skip_preamble(line):
            continue

        if supplementary_match:
            flush_article()
            flush_extra()
            extra_seq += 1
            current_extra = {
                "unit_type": "supplementary",
                "unit_no": f"부칙_{extra_seq}",
                "title": line,
                "parent_heading_id": "",
                "parts": [line],
            }
            continue

        if appendix_match and "증서식" not in line:
            flush_article()
            flush_extra()
            extra_seq += 1
            appendix_type, appendix_no, appendix_title = appendix_match.groups()
            current_extra = {
                "unit_type": "appendix",
                "unit_no": f"{appendix_type}_{appendix_no or extra_seq}",
                "title": clean_text(f"{appendix_type} {appendix_no or ''} {appendix_title}"),
                "parent_heading_id": "",
                "parts": [line],
            }
            continue

        if structure_match:
            flush_article()
            flush_extra()
            heading_no, heading_title = structure_match.groups()
            heading_type = "part" if heading_no.endswith("편") else "chapter" if heading_no.endswith("장") else "section"
            if heading_type == "part":
                heading_stack = []
            elif heading_type == "chapter":
                heading_stack = [h for h in heading_stack if h["unit_type"] == "part"]
            elif heading_type == "section":
                heading_stack = [h for h in heading_stack if h["unit_type"] in ("part", "chapter")]
            headings.append(
                {
                    "unit_type": heading_type,
                    "unit_no": heading_no,
                    "title": heading_title,
                    "parent_heading_no": heading_stack[-1]["unit_no"] if heading_stack else "",
                    "text": line,
                }
            )
            heading_stack.append({"unit_type": heading_type, "unit_no": heading_no})
            continue

        if article_match:
            flush_article()
            flush_extra()
            article_no, article_title, rest = article_match.groups()
            current_article = {
                "article_no": article_no,
                "title": article_title,
                "parent_heading_no": heading_stack[-1]["unit_no"] if heading_stack else "",
                "parts": [clean_text(" ".join([article_no, f"({article_title})", rest]).strip())],
            }
            continue

        if current_extra is not None:
            current_extra["parts"].append(line)
            continue

        if current_article is not None:
            current_article["parts"].append(line)

    flush_article()
    flush_extra()
    return headings, articles, extras


def add_article_children(document_id: str, article: dict, article_id: str, units: list[dict], relations: list[dict]) -> None:
    article_text = sanitize_for_children(article["raw_text"])
    paragraphs = split_circled(article_text)

    if not paragraphs:
        items = split_numbered(article_text)
        if items:
            for i_idx, (i_no, i_text) in enumerate(items, start=1):
                i_text = trim_at_next_article(i_text)
                item_id = make_unit_id(document_id, "item", f"{article['article_no']}_{i_no}_{i_idx}")
                units.append(
                    {
                        "unit_id": item_id,
                        "document_id": document_id,
                        "parent_unit_id": article_id,
                        "unit_type": "item",
                        "unit_no": i_no,
                        "title": "",
                        "text": clean_text(i_text),
                        "effective_date": "",
                        "raw_key": "",
                    }
                )
                relations.append({"source_id": article_id, "relation_type": "HAS_CHILD", "target_id": item_id, "source_text": ""})
                append_reference_relations(item_id, clean_text(i_text), relations)
                for s_idx, (s_no, s_text) in enumerate(split_korean(i_text), start=1):
                    s_text = trim_at_next_article(s_text)
                    subitem_id = make_unit_id(document_id, "subitem", f"{article['article_no']}_{i_no}_{s_no}_{s_idx}")
                    units.append(
                        {
                            "unit_id": subitem_id,
                            "document_id": document_id,
                            "parent_unit_id": item_id,
                            "unit_type": "subitem",
                            "unit_no": s_no,
                            "title": "",
                            "text": clean_text(s_text),
                            "effective_date": "",
                            "raw_key": "",
                        }
                    )
                    relations.append({"source_id": item_id, "relation_type": "HAS_CHILD", "target_id": subitem_id, "source_text": ""})
                    append_reference_relations(subitem_id, clean_text(s_text), relations)
                    for d_idx, (d_no, d_text) in enumerate(split_paren_number(s_text), start=1):
                        d_text = trim_at_next_article(d_text)
                        detail_id = make_unit_id(document_id, "detail_item", f"{article['article_no']}_{i_no}_{s_no}_{d_no}_{d_idx}")
                        units.append(
                            {
                                "unit_id": detail_id,
                                "document_id": document_id,
                                "parent_unit_id": subitem_id,
                                "unit_type": "detail_item",
                                "unit_no": d_no,
                                "title": "",
                                "text": clean_text(d_text),
                                "effective_date": "",
                                "raw_key": "",
                            }
                        )
                        relations.append({"source_id": subitem_id, "relation_type": "HAS_CHILD", "target_id": detail_id, "source_text": ""})
                        append_reference_relations(detail_id, clean_text(d_text), relations)
        return

    for p_idx, (p_no, p_text) in enumerate(paragraphs, start=1):
        p_text = trim_at_next_article(p_text)
        paragraph_id = make_unit_id(document_id, "paragraph", f"{article['article_no']}_{p_no}_{p_idx}")
        units.append(
            {
                "unit_id": paragraph_id,
                "document_id": document_id,
                "parent_unit_id": article_id,
                "unit_type": "paragraph",
                "unit_no": p_no,
                "title": "",
                "text": clean_text(p_text),
                "effective_date": "",
                "raw_key": "",
            }
        )
        relations.append({"source_id": article_id, "relation_type": "HAS_CHILD", "target_id": paragraph_id, "source_text": ""})
        append_reference_relations(paragraph_id, clean_text(p_text), relations)

        for i_idx, (i_no, i_text) in enumerate(split_numbered(p_text), start=1):
            i_text = trim_at_next_article(i_text)
            item_id = make_unit_id(document_id, "item", f"{article['article_no']}_{p_no}_{i_no}_{i_idx}")
            units.append(
                {
                    "unit_id": item_id,
                    "document_id": document_id,
                    "parent_unit_id": paragraph_id,
                    "unit_type": "item",
                    "unit_no": i_no,
                    "title": "",
                    "text": clean_text(i_text),
                    "effective_date": "",
                    "raw_key": "",
                }
            )
            relations.append({"source_id": paragraph_id, "relation_type": "HAS_CHILD", "target_id": item_id, "source_text": ""})
            append_reference_relations(item_id, clean_text(i_text), relations)

            for s_idx, (s_no, s_text) in enumerate(split_korean(i_text), start=1):
                s_text = trim_at_next_article(s_text)
                subitem_id = make_unit_id(document_id, "subitem", f"{article['article_no']}_{p_no}_{i_no}_{s_no}_{s_idx}")
                units.append(
                    {
                        "unit_id": subitem_id,
                        "document_id": document_id,
                        "parent_unit_id": item_id,
                        "unit_type": "subitem",
                        "unit_no": s_no,
                        "title": "",
                        "text": clean_text(s_text),
                        "effective_date": "",
                        "raw_key": "",
                    }
                )
                relations.append({"source_id": item_id, "relation_type": "HAS_CHILD", "target_id": subitem_id, "source_text": ""})
                append_reference_relations(subitem_id, clean_text(s_text), relations)
                for d_idx, (d_no, d_text) in enumerate(split_paren_number(s_text), start=1):
                    d_text = trim_at_next_article(d_text)
                    detail_id = make_unit_id(document_id, "detail_item", f"{article['article_no']}_{p_no}_{i_no}_{s_no}_{d_no}_{d_idx}")
                    units.append(
                        {
                            "unit_id": detail_id,
                            "document_id": document_id,
                            "parent_unit_id": subitem_id,
                            "unit_type": "detail_item",
                            "unit_no": d_no,
                            "title": "",
                            "text": clean_text(d_text),
                            "effective_date": "",
                            "raw_key": "",
                        }
                    )
                    relations.append({"source_id": subitem_id, "relation_type": "HAS_CHILD", "target_id": detail_id, "source_text": ""})
                    append_reference_relations(detail_id, clean_text(d_text), relations)


def normalize_document(path: Path) -> tuple[dict, list[dict], list[dict]]:
    markdown = path.read_text(encoding="utf-8")
    slug = FILE_SLUGS[path.name]
    document_id = make_document_id(slug)

    document = {
        "document_id": document_id,
        "slug": slug,
        "document_type": "내규",
        "title": path.stem,
        "promulgation_date": "",
        "effective_date": "",
        "department": "",
        "kind": "internal_rule",
        "source_file": path.name,
    }

    units: list[dict] = []
    relations: list[dict] = []

    headings, articles, extras = build_blocks(markdown)
    heading_id_map: dict[str, str] = {}

    for heading in headings:
        heading_id = make_unit_id(document_id, "heading", heading["unit_no"])
        heading_id_map[heading["unit_no"]] = heading_id
        parent_heading_id = heading_id_map.get(heading["parent_heading_no"], "")
        units.append(
            {
                "unit_id": heading_id,
                "document_id": document_id,
                "parent_unit_id": parent_heading_id,
                "unit_type": "heading",
                "unit_no": heading["unit_no"],
                "title": heading["title"],
                "text": heading["text"],
                "effective_date": "",
                "raw_key": "",
            }
        )
        if parent_heading_id:
            relations.append({"source_id": parent_heading_id, "relation_type": "HAS_CHILD", "target_id": heading_id, "source_text": ""})
        else:
            relations.append({"source_id": document_id, "relation_type": "HAS_UNIT", "target_id": heading_id, "source_text": ""})

    for article in articles:
        article_id = make_unit_id(document_id, "article", article["article_no"])
        parent_heading_id = heading_id_map.get(article["parent_heading_no"], "")
        units.append(
            {
                "unit_id": article_id,
                "document_id": document_id,
                "parent_unit_id": parent_heading_id,
                "unit_type": "article",
                "unit_no": article["article_no"],
                "title": article["title"],
                "text": article["text"],
                "effective_date": "",
                "raw_key": "",
            }
        )
        if parent_heading_id:
            relations.append({"source_id": parent_heading_id, "relation_type": "HAS_CHILD", "target_id": article_id, "source_text": ""})
        else:
            relations.append({"source_id": document_id, "relation_type": "HAS_UNIT", "target_id": article_id, "source_text": ""})
        append_reference_relations(article_id, article["text"], relations)
        add_article_children(document_id, article, article_id, units, relations)

    for extra in extras:
        extra_id = make_unit_id(document_id, extra["unit_type"], extra["unit_no"])
        units.append(
            {
                "unit_id": extra_id,
                "document_id": document_id,
                "parent_unit_id": "",
                "unit_type": extra["unit_type"],
                "unit_no": extra["unit_no"],
                "title": extra["title"],
                "text": extra["text"],
                "effective_date": "",
                "raw_key": "",
            }
        )
        relations.append({"source_id": document_id, "relation_type": "HAS_UNIT", "target_id": extra_id, "source_text": ""})
        append_reference_relations(extra_id, extra["text"], relations)

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
