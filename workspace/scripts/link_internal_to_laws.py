from __future__ import annotations

import os
from pathlib import Path

from neo4j import GraphDatabase


ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / "workspace" / ".env"

LAW_ALIASES = [
    {
        "alias": "특정금융정보법",
        "document_id": "law:spec_financial_transaction_act",
    },
    {
        "alias": "특정금융정보법 시행령",
        "document_id": "law:spec_financial_transaction_act_enforcement_decree",
    },
    {
        "alias": "금융실명거래 및 비밀보장에 관한 법률",
        "document_id": "law:real_name_financial_transactions_act",
    },
    {
        "alias": "신용정보의 이용 및 보호에 관한 법률",
        "document_id": "external:credit_information_act",
    },
]


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"`{name}` 환경변수가 필요합니다.")
    return value


def main() -> int:
    load_dotenv(ENV_PATH)
    uri = require_env("NEO4J_URI")
    username = require_env("NEO4J_USERNAME")
    password = require_env("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE", "neo4j").strip() or "neo4j"

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        with driver.session(database=database) as session:
            for row in LAW_ALIASES:
                if row["document_id"].startswith("external:"):
                    session.run(
                        """
                        MERGE (refdoc:LegalReference {reference_key: $document_id})
                        SET refdoc.reference_type = 'EXTERNAL_DOCUMENT',
                            refdoc.target_id = $alias
                        WITH refdoc
                        MATCH (d:LegalDocument {kind: 'internal_rule'})-[:HAS_UNIT]->(u:LegalUnit)
                        WHERE u.text CONTAINS $alias
                        MERGE (d)-[:IMPLEMENTS_CANDIDATE]->(refdoc)
                        """,
                        alias=row["alias"],
                        document_id=row["document_id"],
                    )
                else:
                    session.run(
                        """
                        MATCH (target:LegalDocument {document_id: $document_id})
                        MATCH (d:LegalDocument {kind: 'internal_rule'})-[:HAS_UNIT]->(u:LegalUnit)
                        WHERE u.text CONTAINS $alias
                        MERGE (d)-[:IMPLEMENTS]->(target)
                        MERGE (u)-[:REFERS_TO_DOCUMENT]->(target)
                        """,
                        alias=row["alias"],
                        document_id=row["document_id"],
                    )

            summary = session.run(
                """
                MATCH (d:LegalDocument {kind:'internal_rule'})-[r]->(t)
                WHERE type(r) IN ['IMPLEMENTS', 'IMPLEMENTS_CANDIDATE']
                RETURN d.title AS source, type(r) AS rel, coalesce(t.title, t.target_id, t.reference_key) AS target
                ORDER BY source, rel, target
                """
            )
            for record in summary:
                print(record.data())
        return 0
    finally:
        driver.close()


if __name__ == "__main__":
    raise SystemExit(main())
