from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "data" / "legal" / "processed"
OUTPUT_DIR = ROOT / "workspace" / "graph" / "neo4j_seed"

DOCUMENTS_PATH = INPUT_DIR / "legal_documents.json"
UNITS_PATH = INPUT_DIR / "legal_units.json"
RELATIONS_PATH = INPUT_DIR / "legal_relations.json"


def read_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def stringify(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        if "content" in value:
            return str(value["content"])
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def main() -> int:
    documents = read_json(DOCUMENTS_PATH)
    units = read_json(UNITS_PATH)
    relations = read_json(RELATIONS_PATH)

    document_rows = [
        {
            "document_id:ID(LegalDocument)": doc["document_id"],
            "slug": doc.get("slug", ""),
            "title": stringify(doc.get("title", "")),
            "document_type": stringify(doc.get("document_type", "")),
            "department": stringify(doc.get("department", "")),
            "promulgation_date": doc.get("promulgation_date", ""),
            "effective_date": doc.get("effective_date", ""),
            "law_id": doc.get("law_id", ""),
            "mst": doc.get("mst", ""),
            "rule_id": doc.get("rule_id", ""),
            "kind": doc.get("kind", ""),
            ":LABEL": "LegalDocument",
        }
        for doc in documents
    ]

    unit_rows = [
        {
            "unit_id:ID(LegalUnit)": unit["unit_id"],
            "document_id": unit.get("document_id", ""),
            "parent_unit_id": unit.get("parent_unit_id", ""),
            "unit_type": unit.get("unit_type", ""),
            "unit_no": unit.get("unit_no", ""),
            "title": unit.get("title", ""),
            "text": unit.get("text", ""),
            "effective_date": unit.get("effective_date", ""),
            "raw_key": unit.get("raw_key", ""),
            ":LABEL": "LegalUnit",
        }
        for unit in units
    ]

    relation_rows = [
        {
            ":START_ID": relation["source_id"],
            ":END_ID": relation["target_id"],
            ":TYPE": relation["relation_type"],
            "source_text": relation.get("source_text", ""),
        }
        for relation in relations
    ]

    write_csv(
        OUTPUT_DIR / "legal_documents.csv",
        document_rows,
        [
            "document_id:ID(LegalDocument)",
            "slug",
            "title",
            "document_type",
            "department",
            "promulgation_date",
            "effective_date",
            "law_id",
            "mst",
            "rule_id",
            "kind",
            ":LABEL",
        ],
    )
    write_csv(
        OUTPUT_DIR / "legal_units.csv",
        unit_rows,
        [
            "unit_id:ID(LegalUnit)",
            "document_id",
            "parent_unit_id",
            "unit_type",
            "unit_no",
            "title",
            "text",
            "effective_date",
            "raw_key",
            ":LABEL",
        ],
    )
    write_csv(
        OUTPUT_DIR / "legal_relations.csv",
        relation_rows,
        [
            ":START_ID",
            ":END_ID",
            ":TYPE",
            "source_text",
        ],
    )

    print(f"documents: {len(document_rows)}")
    print(f"units: {len(unit_rows)}")
    print(f"relations: {len(relation_rows)}")
    print(f"output: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
