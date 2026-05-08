from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / "workspace" / ".env"
RAW_DIR = ROOT / "data" / "legal" / "raw"
PROCESSED_DIR = ROOT / "data" / "legal" / "processed"
MANIFEST_PATH = PROCESSED_DIR / "additional_law_manifest_2026-04-23.json"

LAW_SEARCH_URL = "https://www.law.go.kr/DRF/lawSearch.do"
LAW_SERVICE_URL = "https://www.law.go.kr/DRF/lawService.do"


TARGETS: list[dict[str, str]] = [
    {
        "slug": "credit_information_act",
        "query": "신용정보의 이용 및 보호에 관한 법률",
        "kind": "law",
    },
    {
        "slug": "foreign_exchange_transactions_act",
        "query": "외국환거래법",
        "kind": "law",
    },
    {
        "slug": "counter_terrorism_financing_act",
        "query": "공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률",
        "kind": "law",
    },
    {
        "slug": "narcotics_illegal_trade_act",
        "query": "마약류 불법거래 방지에 관한 특례법",
        "kind": "law",
    },
    {
        "slug": "tax_crimes_punishment_act",
        "query": "조세범 처벌법",
        "kind": "law",
    },
    {
        "slug": "customs_act",
        "query": "관세법",
        "kind": "law",
    },
    {
        "slug": "local_tax_basic_act",
        "query": "지방세기본법",
        "kind": "law",
    },
    {
        "slug": "aggravated_punishment_specific_crimes_act",
        "query": "특정범죄 가중처벌 등에 관한 법률",
        "kind": "law",
    },
    {
        "slug": "capital_markets_act",
        "query": "자본시장과 금융투자업에 관한 법률",
        "kind": "law",
    },
    {
        "slug": "financial_companies_governance_act",
        "query": "금융회사의 지배구조에 관한 법률",
        "kind": "law",
    },
    {
        "slug": "financial_companies_governance_act_enforcement_decree",
        "query": "금융회사의 지배구조에 관한 법률 시행령",
        "kind": "law",
    },
]


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


def sanitize_response_text(content: str) -> str:
    return re.sub(r"OC=[^&\"']+", "OC=REDACTED", content)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sanitize_response_text(content), encoding="utf-8")


def fetch(url: str, params: dict[str, str]) -> str:
    request_url = f"{url}?{urlencode(params)}"
    with urlopen(request_url) as response:
        return response.read().decode("utf-8")


def ensure_list(value: object) -> list[dict]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def pick_exact_law(search_text: str, query: str) -> dict[str, str]:
    payload = json.loads(search_text)
    candidates = ensure_list(payload.get("LawSearch", {}).get("law", []))
    for candidate in candidates:
        if candidate.get("법령명한글") == query:
            return candidate
    if candidates:
        return candidates[0]
    raise ValueError(f"검색 결과가 없습니다: {query}")


def collect_law(oc_key: str, item: dict[str, str]) -> dict[str, str]:
    search_params = {
        "OC": oc_key,
        "target": "law",
        "type": "JSON",
        "query": item["query"],
        "search": "1",
        "display": "20",
    }
    search_text = fetch(LAW_SEARCH_URL, search_params)
    exact = pick_exact_law(search_text, item["query"])
    mst = exact["법령일련번호"]

    body_params = {
        "OC": oc_key,
        "target": "eflaw",
        "type": "JSON",
        "MST": mst,
    }
    structure_params = {
        "OC": oc_key,
        "target": "lsStmd",
        "type": "JSON",
        "MST": mst,
    }

    body_text = fetch(LAW_SERVICE_URL, body_params)
    structure_text = fetch(LAW_SERVICE_URL, structure_params)

    base = RAW_DIR / item["slug"]
    write_text(base.with_name(f"{item['slug']}_search.json"), search_text)
    write_text(base.with_name(f"{item['slug']}_body.json"), body_text)
    write_text(base.with_name(f"{item['slug']}_structure.json"), structure_text)

    return {
        "slug": item["slug"],
        "kind": item["kind"],
        "query": item["query"],
        "mst": mst,
        "law_id": exact.get("법령ID", ""),
        "title": exact.get("법령명한글", ""),
        "search_path": str(base.with_name(f"{item['slug']}_search.json")),
        "body_path": str(base.with_name(f"{item['slug']}_body.json")),
        "structure_path": str(base.with_name(f"{item['slug']}_structure.json")),
    }


def main() -> int:
    load_dotenv(ENV_PATH)
    oc_key = require_env("LAW_OPEN_OC")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    collected: list[dict[str, str]] = []
    for item in TARGETS:
        collected.append(collect_law(oc_key, item))

    manifest = {
        "collected_at": "2026-04-23",
        "source": "https://open.law.go.kr/LSO/openApi/guideList.do",
        "target_count": len(TARGETS),
        "targets": collected,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"collected {len(collected)} targets")
    print(f"manifest: {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
