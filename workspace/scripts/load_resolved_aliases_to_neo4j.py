from __future__ import annotations

import json
import os
from pathlib import Path

from neo4j import GraphDatabase


ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / "workspace" / ".env"
BASE_LEGAL_DOCS_PATH = ROOT / "data" / "legal" / "processed" / "legal_documents.json"
ADDITIONAL_MANIFEST_PATH = ROOT / "data" / "legal" / "processed" / "additional_law_manifest_2026-04-23.json"
RESOLVED_PATH = ROOT / "data" / "processed" / "internal_rules" / "legal_reference_resolved.json"

BATCH_SIZE = 200


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


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def batch_rows(rows: list[dict], size: int) -> list[list[dict]]:
    return [rows[idx : idx + size] for idx in range(0, len(rows), size)]


def run_batches(session, query: str, rows: list[dict]) -> None:
    for batch in batch_rows(rows, BATCH_SIZE):
        session.run(query, rows=batch)


def load_document_catalog() -> dict[str, dict]:
    documents = {doc["document_id"]: doc for doc in read_json(BASE_LEGAL_DOCS_PATH)}
    if ADDITIONAL_MANIFEST_PATH.exists():
        manifest = read_json(ADDITIONAL_MANIFEST_PATH)
        for target in manifest.get("targets", []):
            document_id = f"law:{target['slug']}"
            documents.setdefault(
                document_id,
                {
                    "document_id": document_id,
                    "slug": target["slug"],
                    "document_type": "법률",
                    "title": target.get("title", "") or target.get("query", ""),
                    "kind": target.get("kind", "law"),
                    "law_id": target.get("law_id", ""),
                    "mst": target.get("mst", ""),
                    "collected_at": manifest.get("collected_at", ""),
                },
            )
    return documents


def main() -> int:
    load_dotenv(ENV_PATH)
    uri = require_env("NEO4J_URI")
    username = require_env("NEO4J_USERNAME")
    password = require_env("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE", "neo4j").strip() or "neo4j"

    documents = load_document_catalog()
    resolved_rows = read_json(RESOLVED_PATH)

    target_documents = {
        row["matched_document_id"]: documents[row["matched_document_id"]]
        for row in resolved_rows
        if row["matched_document_id"] in documents
    }

    unit_links = [
        {
            "source_id": row["source_id"],
            "target_document_id": row["matched_document_id"],
            "raw_target_id": row["raw_target_id"],
            "normalized_target_id": row["normalized_target_id"],
            "score": row["score"],
            "method": row["method"],
            "confidence": row["confidence"],
        }
        for row in resolved_rows
    ]

    doc_links_map: dict[tuple[str, str], dict] = {}
    for row in resolved_rows:
        source_document_id = row["source_id"].split(":article:")[0] if ":article:" in row["source_id"] else row["source_id"].split(":paragraph:")[0]
        key = (source_document_id, row["matched_document_id"])
        current = doc_links_map.get(key)
        if current is None or row["score"] > current["best_score"]:
            doc_links_map[key] = {
                "source_document_id": source_document_id,
                "target_document_id": row["matched_document_id"],
                "best_score": row["score"],
                "method": row["method"],
                "confidence": row["confidence"],
            }

    document_links = list(doc_links_map.values())

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        with driver.session(database=database) as session:
            run_batches(
                session,
                """
                UNWIND $rows AS row
                MERGE (d:LegalDocument {document_id: row.document_id})
                SET d += row
                """,
                list(target_documents.values()),
            )

            session.run(
                """
                MATCH (:LegalUnit)-[r:REFERS_TO_DOCUMENT]->(:LegalDocument)
                WHERE r.resolver = 'alias_pipeline_v1'
                DELETE r
                """
            )
            session.run(
                """
                MATCH (:LegalDocument)-[r:IMPLEMENTS_RESOLVED]->(:LegalDocument)
                WHERE r.resolver = 'alias_pipeline_v1'
                DELETE r
                """
            )

            run_batches(
                session,
                """
                UNWIND $rows AS row
                MATCH (u:LegalUnit {unit_id: row.source_id})
                MATCH (d:LegalDocument {document_id: row.target_document_id})
                MERGE (u)-[r:REFERS_TO_DOCUMENT]->(d)
                SET r.raw_target_id = row.raw_target_id,
                    r.normalized_target_id = row.normalized_target_id,
                    r.score = row.score,
                    r.method = row.method,
                    r.confidence = row.confidence,
                    r.resolver = 'alias_pipeline_v1'
                """,
                unit_links,
            )

            run_batches(
                session,
                """
                UNWIND $rows AS row
                MATCH (src:LegalDocument {document_id: row.source_document_id})
                MATCH (dst:LegalDocument {document_id: row.target_document_id})
                MERGE (src)-[r:IMPLEMENTS_RESOLVED]->(dst)
                SET r.best_score = row.best_score,
                    r.method = row.method,
                    r.confidence = row.confidence,
                    r.resolver = 'alias_pipeline_v1'
                """,
                document_links,
            )

            summary = session.run(
                """
                CALL {
                  MATCH (:LegalUnit)-[r:REFERS_TO_DOCUMENT]->(:LegalDocument)
                  WHERE r.resolver = 'alias_pipeline_v1'
                  RETURN count(r) AS unit_ref_count
                }
                CALL {
                  MATCH (:LegalDocument)-[r:IMPLEMENTS_RESOLVED]->(:LegalDocument)
                  WHERE r.resolver = 'alias_pipeline_v1'
                  RETURN count(r) AS doc_ref_count
                }
                RETURN unit_ref_count, doc_ref_count
                """
            ).single()

        print(f"target_documents: {len(target_documents)}")
        print(f"unit_links: {len(unit_links)}")
        print(f"document_links: {len(document_links)}")
        print(f"neo4j_unit_ref_count: {summary['unit_ref_count']}")
        print(f"neo4j_doc_ref_count: {summary['doc_ref_count']}")
        print(f"database: {database}")
        return 0
    finally:
        driver.close()


if __name__ == "__main__":
    raise SystemExit(main())
