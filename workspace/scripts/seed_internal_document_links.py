from __future__ import annotations

import os
from pathlib import Path

from neo4j import GraphDatabase


ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / "workspace" / ".env"

LINKS = [
    ("internal:aml_policy", "law:spec_financial_transaction_act"),
    ("internal:aml_policy", "law:spec_financial_transaction_act_enforcement_decree"),
    ("internal:aml_policy", "law:aml_and_cft_business_rule"),
    ("internal:aml_guideline", "law:spec_financial_transaction_act"),
    ("internal:aml_guideline", "law:spec_financial_transaction_act_enforcement_decree"),
    ("internal:aml_guideline", "law:aml_and_cft_business_rule"),
    ("internal:foreign_aml_guideline", "law:spec_financial_transaction_act"),
    ("internal:foreign_aml_guideline", "law:spec_financial_transaction_act_enforcement_decree"),
    ("internal:vasp_aml_guideline", "law:spec_financial_transaction_act"),
    ("internal:vasp_aml_guideline", "law:spec_financial_transaction_act_enforcement_decree"),
    ("internal:rba_risk_guideline", "law:aml_and_cft_business_rule"),
    ("internal:fiu_security_standard", "law:aml_and_cft_business_rule"),
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
    driver = GraphDatabase.driver(
        require_env("NEO4J_URI"),
        auth=(require_env("NEO4J_USERNAME"), require_env("NEO4J_PASSWORD")),
    )
    database = os.environ.get("NEO4J_DATABASE", "neo4j").strip() or "neo4j"
    try:
        with driver.session(database=database) as session:
            session.run(
                """
                UNWIND $rows AS row
                MATCH (src:LegalDocument {document_id: row.source_id})
                MATCH (dst:LegalDocument {document_id: row.target_id})
                MERGE (src)-[:IMPLEMENTS_CANDIDATE]->(dst)
                """,
                rows=[{"source_id": s, "target_id": t} for s, t in LINKS],
            )
            for record in session.run(
                """
                MATCH (src:LegalDocument {kind:'internal_rule'})-[:IMPLEMENTS_CANDIDATE]->(dst:LegalDocument)
                RETURN src.title AS source, dst.title AS target
                ORDER BY source, target
                """
            ):
                print(record.data())
        return 0
    finally:
        driver.close()


if __name__ == "__main__":
    raise SystemExit(main())
