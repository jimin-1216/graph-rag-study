from __future__ import annotations

import json
import os
from pathlib import Path

from neo4j import GraphDatabase


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_DIR = ROOT / "workspace"
ENV_PATH = WORKSPACE_DIR / ".env"
PROCESSED_DIR = ROOT / "data" / "processed" / "internal_rules"

DOCUMENTS_PATH = PROCESSED_DIR / "internal_documents.json"
UNITS_PATH = PROCESSED_DIR / "internal_units.json"
RELATIONS_PATH = PROCESSED_DIR / "internal_relations.json"

BATCH_SIZE = 200


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def read_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def batch_rows(rows: list[dict], size: int) -> list[list[dict]]:
    return [rows[idx : idx + size] for idx in range(0, len(rows), size)]


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"`{name}` 환경변수가 필요합니다.")
    return value


def run_batches(session, query: str, rows: list[dict]) -> None:
    for batch in batch_rows(rows, BATCH_SIZE):
        session.run(query, rows=batch)


def main() -> int:
    load_dotenv(ENV_PATH)
    uri = require_env("NEO4J_URI")
    username = require_env("NEO4J_USERNAME")
    password = require_env("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE", "neo4j").strip() or "neo4j"

    documents = read_json(DOCUMENTS_PATH)
    units = read_json(UNITS_PATH)
    relations = read_json(RELATIONS_PATH)

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        with driver.session(database=database) as session:
            session.run(
                """
                MATCH (d:LegalDocument {kind:'internal_rule'})
                DETACH DELETE d
                """
            )
            session.run(
                """
                MATCH (u:LegalUnit)
                WHERE u.document_id STARTS WITH 'internal:'
                DETACH DELETE u
                """
            )
            session.run(
                """
                MATCH (r:LegalReference)
                WHERE NOT ()--(r)
                DELETE r
                """
            )
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

            run_batches(
                session,
                """
                UNWIND $rows AS row
                MERGE (d:LegalDocument {document_id: row.document_id})
                SET d += row
                """,
                documents,
            )

            run_batches(
                session,
                """
                UNWIND $rows AS row
                MERGE (u:LegalUnit {unit_id: row.unit_id})
                SET u += row
                """,
                units,
            )

            session.run(
                """
                MATCH (u:LegalUnit)
                MATCH (d:LegalDocument {document_id: u.document_id})
                MERGE (u)-[:BELONGS_TO]->(d)
                """
            )

            run_batches(
                session,
                """
                UNWIND $rows AS row
                MATCH (d:LegalDocument {document_id: row.source_id})
                MATCH (u:LegalUnit {unit_id: row.target_id})
                MERGE (d)-[:HAS_UNIT]->(u)
                """,
                [r for r in relations if r["relation_type"] == "HAS_UNIT"],
            )

            run_batches(
                session,
                """
                UNWIND $rows AS row
                MATCH (s:LegalUnit {unit_id: row.source_id})
                MATCH (t:LegalUnit {unit_id: row.target_id})
                MERGE (s)-[:HAS_CHILD]->(t)
                """,
                [r for r in relations if r["relation_type"] == "HAS_CHILD"],
            )

            ref_rows = [r for r in relations if r["relation_type"] in ("REFERS_TO_LAW_NAME", "CITES_ARTICLE_TEXT")]
            run_batches(
                session,
                """
                UNWIND $rows AS row
                OPTIONAL MATCH (sd:LegalDocument {document_id: row.source_id})
                OPTIONAL MATCH (su:LegalUnit {unit_id: row.source_id})
                WITH row, coalesce(sd, su) AS source
                WHERE source IS NOT NULL
                MERGE (ref:LegalReference {reference_key: row.reference_key})
                SET ref.reference_type = row.reference_type,
                    ref.target_id = row.target_id
                MERGE (source)-[r:LEGAL_REFERENCE]->(ref)
                SET r.relation_type = row.relation_type,
                    r.source_text = row.source_text
                """,
                [
                    {
                        "source_id": r["source_id"],
                        "target_id": r["target_id"],
                        "reference_key": f"{r['relation_type']}:{r['target_id']}",
                        "reference_type": "LAW_NAME" if r["relation_type"] == "REFERS_TO_LAW_NAME" else "ARTICLE_TEXT",
                        "relation_type": r["relation_type"],
                        "source_text": r.get("source_text", ""),
                    }
                    for r in ref_rows
                ],
            )

            session.run(
                """
                WITH [
                  {alias:'특정금융정보법', document_id:'law:spec_financial_transaction_act'},
                  {alias:'특정금융정보법 시행령', document_id:'law:spec_financial_transaction_act_enforcement_decree'},
                  {alias:'특정 금융거래정보의 보고 및 이용 등에 관한 법률', document_id:'law:spec_financial_transaction_act'},
                  {alias:'특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령', document_id:'law:spec_financial_transaction_act_enforcement_decree'}
                ] AS aliases
                UNWIND aliases AS aliasRow
                MATCH (target:LegalDocument {document_id: aliasRow.document_id})
                MATCH (src:LegalDocument {kind:'internal_rule'})-[:HAS_UNIT]->(u:LegalUnit)
                WHERE u.text CONTAINS aliasRow.alias
                MERGE (src)-[:IMPLEMENTS]->(target)
                MERGE (u)-[:REFERS_TO_DOCUMENT]->(target)
                """
            )

        print(f"documents: {len(documents)}")
        print(f"units: {len(units)}")
        print(f"relations: {len(relations)}")
        print(f"database: {database}")
        return 0
    finally:
        driver.close()


if __name__ == "__main__":
    raise SystemExit(main())
