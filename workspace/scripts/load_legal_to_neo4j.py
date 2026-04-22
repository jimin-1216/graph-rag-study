from __future__ import annotations

import json
import os
from pathlib import Path

from neo4j import GraphDatabase


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_DIR = ROOT / "workspace"
ENV_PATH = WORKSPACE_DIR / ".env"
PROCESSED_DIR = ROOT / "data" / "legal" / "processed"

DOCUMENTS_PATH = PROCESSED_DIR / "legal_documents.json"
UNITS_PATH = PROCESSED_DIR / "legal_units.json"
RELATIONS_PATH = PROCESSED_DIR / "legal_relations.json"

BATCH_SIZE = 200


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def read_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def flatten_value(value):
    if isinstance(value, dict):
        if "content" in value:
            return flatten_value(value["content"])
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return [flatten_value(item) for item in value]
    return value


def flatten_rows(rows: list[dict]) -> list[dict]:
    return [{key: flatten_value(value) for key, value in row.items()} for row in rows]


def batch_rows(rows: list[dict], size: int) -> list[list[dict]]:
    return [rows[idx : idx + size] for idx in range(0, len(rows), size)]


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"`{name}` 환경변수가 필요합니다. workspace/.env에 넣어주세요.")
    return value


def create_constraints(session) -> None:
    session.run(
        """
        CREATE CONSTRAINT legal_document_id IF NOT EXISTS
        FOR (d:LegalDocument)
        REQUIRE d.document_id IS UNIQUE
        """
    )
    session.run(
        """
        CREATE CONSTRAINT legal_unit_id IF NOT EXISTS
        FOR (u:LegalUnit)
        REQUIRE u.unit_id IS UNIQUE
        """
    )
    session.run(
        """
        CREATE CONSTRAINT legal_reference_key IF NOT EXISTS
        FOR (r:LegalReference)
        REQUIRE r.reference_key IS UNIQUE
        """
    )


def upsert_documents(session, rows: list[dict]) -> None:
    session.run(
        """
        UNWIND $rows AS row
        MERGE (d:LegalDocument {document_id: row.document_id})
        SET d += row
        """,
        rows=rows,
    )


def upsert_units(session, rows: list[dict]) -> None:
    session.run(
        """
        UNWIND $rows AS row
        MERGE (u:LegalUnit {unit_id: row.unit_id})
        SET u += row
        """,
        rows=rows,
    )


def create_belongs_to(session) -> None:
    session.run(
        """
        MATCH (u:LegalUnit)
        MATCH (d:LegalDocument {document_id: u.document_id})
        MERGE (u)-[:BELONGS_TO]->(d)
        """
    )


def create_has_unit(session, rows: list[dict]) -> None:
    session.run(
        """
        UNWIND $rows AS row
        MATCH (d:LegalDocument {document_id: row.source_id})
        MATCH (u:LegalUnit {unit_id: row.target_id})
        MERGE (d)-[:HAS_UNIT]->(u)
        """,
        rows=rows,
    )


def create_has_child(session, rows: list[dict]) -> None:
    session.run(
        """
        UNWIND $rows AS row
        MATCH (source:LegalUnit {unit_id: row.source_id})
        MATCH (target:LegalUnit {unit_id: row.target_id})
        MERGE (source)-[:HAS_CHILD]->(target)
        """,
        rows=rows,
    )


def create_reference_links(session, rows: list[dict], relation_type: str, reference_type: str) -> None:
    session.run(
        """
        UNWIND $rows AS row
        OPTIONAL MATCH (source_doc:LegalDocument {document_id: row.source_id})
        OPTIONAL MATCH (source_unit:LegalUnit {unit_id: row.source_id})
        WITH row, coalesce(source_doc, source_unit) AS source
        WHERE source IS NOT NULL
        MERGE (ref:LegalReference {
            reference_key: row.reference_key
        })
        SET ref.reference_type = row.reference_type,
            ref.target_id = row.target_id
        MERGE (source)-[r:LEGAL_REFERENCE]->(ref)
        SET r.relation_type = row.relation_type,
            r.source_text = row.source_text
        """,
        rows=[
            {
                "source_id": row["source_id"],
                "target_id": row["target_id"],
                "reference_key": f"{relation_type}:{row['target_id']}",
                "reference_type": reference_type,
                "relation_type": relation_type,
                "source_text": row.get("source_text", ""),
            }
            for row in rows
        ],
    )


def main() -> int:
    load_dotenv(ENV_PATH)

    uri = require_env("NEO4J_URI")
    username = require_env("NEO4J_USERNAME")
    password = require_env("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE", "neo4j").strip() or "neo4j"

    documents = read_json(DOCUMENTS_PATH)
    units = read_json(UNITS_PATH)
    relations = read_json(RELATIONS_PATH)
    documents = flatten_rows(documents)
    units = flatten_rows(units)
    relations = flatten_rows(relations)

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        with driver.session(database=database) as session:
            create_constraints(session)

            for batch in batch_rows(documents, BATCH_SIZE):
                upsert_documents(session, batch)

            for batch in batch_rows(units, BATCH_SIZE):
                upsert_units(session, batch)

            create_belongs_to(session)

            has_unit_rows = [row for row in relations if row["relation_type"] == "HAS_UNIT"]
            has_child_rows = [row for row in relations if row["relation_type"] == "HAS_CHILD"]
            cites_rows = [row for row in relations if row["relation_type"] == "CITES_ARTICLE_TEXT"]
            refers_rows = [row for row in relations if row["relation_type"] == "REFERS_TO_LAW_NAME"]
            implements_rows = [row for row in relations if row["relation_type"] == "IMPLEMENTS_CANDIDATE"]

            for batch in batch_rows(has_unit_rows, BATCH_SIZE):
                create_has_unit(session, batch)

            for batch in batch_rows(has_child_rows, BATCH_SIZE):
                create_has_child(session, batch)

            for batch in batch_rows(cites_rows, BATCH_SIZE):
                create_reference_links(session, batch, "CITES_ARTICLE_TEXT", "ARTICLE_TEXT")

            for batch in batch_rows(refers_rows, BATCH_SIZE):
                create_reference_links(session, batch, "REFERS_TO_LAW_NAME", "LAW_NAME")

            for batch in batch_rows(implements_rows, BATCH_SIZE):
                create_reference_links(session, batch, "IMPLEMENTS_CANDIDATE", "DOCUMENT_TITLE")

        print(f"documents: {len(documents)}")
        print(f"units: {len(units)}")
        print(f"relations: {len(relations)}")
        print(f"database: {database}")
        return 0
    finally:
        driver.close()


if __name__ == "__main__":
    raise SystemExit(main())
