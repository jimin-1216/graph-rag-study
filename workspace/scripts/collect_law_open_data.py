from __future__ import annotations

import json
import os
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_DIR = ROOT / "workspace"
ENV_PATH = WORKSPACE_DIR / ".env"
RAW_DIR = ROOT / "data" / "legal" / "raw"
PROCESSED_DIR = ROOT / "data" / "legal" / "processed"
MANIFEST_PATH = PROCESSED_DIR / "law_open_data_manifest.json"

LAW_SEARCH_URL = "https://www.law.go.kr/DRF/lawSearch.do"
LAW_SERVICE_URL = "https://www.law.go.kr/DRF/lawService.do"
ADM_RULE_SEARCH_URL = "https://www.law.go.kr/DRF/lawSearch.do"
ADM_RULE_SERVICE_URL = "https://www.law.go.kr/DRF/lawService.do"


TARGETS: list[dict[str, str]] = [
    {
        "slug": "spec_financial_transaction_act",
        "kind": "law",
        "query": "특정 금융거래정보의 보고 및 이용 등에 관한 법률",
        "target": "eflaw",
    },
    {
        "slug": "spec_financial_transaction_act_enforcement_decree",
        "kind": "law",
        "query": "특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령",
        "target": "eflaw",
    },
    {
        "slug": "aml_and_cft_business_rule",
        "kind": "adm_rule",
        "query": "자금세탁방지 및 공중협박자금조달금지에 관한 업무규정",
        "target": "admrul",
    },
    {
        "slug": "proceeds_of_crime_act",
        "kind": "law",
        "query": "범죄수익은닉의 규제 및 처벌 등에 관한 법률",
        "target": "eflaw",
    },
    {
        "slug": "real_name_financial_transactions_act",
        "kind": "law",
        "query": "금융실명거래 및 비밀보장에 관한 법률",
        "target": "eflaw",
    },
    {
        "slug": "real_name_financial_transactions_act_enforcement_decree",
        "kind": "law",
        "query": "금융실명거래 및 비밀보장에 관한 법률 시행령",
        "target": "eflaw",
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
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def fetch(url: str, params: dict[str, str]) -> str:
    request_url = f"{url}?{urlencode(params)}"
    with urlopen(request_url) as response:
        return response.read().decode("utf-8")


def sanitize_response_text(content: str) -> str:
    return re.sub(r"OC=[^&\"']+", "OC=REDACTED", content)


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sanitize_response_text(content), encoding="utf-8")


def parse_json(content: str) -> dict:
    return json.loads(content)


def ensure_list(value: object) -> list[dict[str, str]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def pick_exact_law(search_text: str, query: str) -> dict[str, str]:
    payload = parse_json(search_text)
    candidates = ensure_list(payload.get("LawSearch", {}).get("law", []))
    for candidate in candidates:
        if candidate.get("법령명한글") == query:
            return candidate
    if candidates:
        return candidates[0]
    raise ValueError(f"검색 결과가 없습니다: {query}")


def pick_exact_admin_rule(search_text: str, query: str) -> dict[str, str]:
    payload = parse_json(search_text)
    candidates = ensure_list(payload.get("AdmRulSearch", {}).get("admrul", []))
    for candidate in candidates:
        if candidate.get("행정규칙명") == query:
            return candidate
    if candidates:
        return candidates[0]
    raise ValueError(f"행정규칙 검색 결과가 없습니다: {query}")


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
        "target": item["target"],
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
        "search_path": str(base.with_name(f"{item['slug']}_search.json")),
        "body_path": str(base.with_name(f"{item['slug']}_body.json")),
        "structure_path": str(base.with_name(f"{item['slug']}_structure.json")),
    }


def collect_admin_rule(oc_key: str, item: dict[str, str]) -> dict[str, str]:
    search_params = {
        "OC": oc_key,
        "target": "admrul",
        "type": "JSON",
        "query": item["query"],
        "display": "20",
    }
    search_text = fetch(ADM_RULE_SEARCH_URL, search_params)
    exact = pick_exact_admin_rule(search_text, item["query"])
    rule_id = exact.get("행정규칙일련번호") or exact.get("ID")

    body_params = {
        "OC": oc_key,
        "target": item["target"],
        "type": "JSON",
        "ID": rule_id,
    }

    body_text = fetch(ADM_RULE_SERVICE_URL, body_params)

    base = RAW_DIR / item["slug"]
    write_text(base.with_name(f"{item['slug']}_search.json"), search_text)
    write_text(base.with_name(f"{item['slug']}_body.json"), body_text)

    return {
        "slug": item["slug"],
        "kind": item["kind"],
        "query": item["query"],
        "rule_id": rule_id,
        "search_path": str(base.with_name(f"{item['slug']}_search.json")),
        "body_path": str(base.with_name(f"{item['slug']}_body.json")),
    }


def main() -> int:
    load_dotenv(ENV_PATH)

    oc_key = os.environ.get("LAW_OPEN_OC")
    if not oc_key:
        raise SystemExit(
            "`LAW_OPEN_OC`가 필요합니다. "
            "workspace/.env 또는 환경변수에 넣어주세요."
        )

    ensure_dirs()

    collected = []
    for item in TARGETS:
        if item["kind"] == "law":
            collected.append(collect_law(oc_key, item))
        elif item["kind"] == "adm_rule":
            collected.append(collect_admin_rule(oc_key, item))
        else:
            raise ValueError(f"지원하지 않는 kind: {item['kind']}")

    manifest = {
        "collected_at": "2026-04-22",
        "source": "https://open.law.go.kr/LSO/openApi/guideList.do",
        "target_count": len(TARGETS),
        "targets": collected,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"collected {len(collected)} targets")
    print(f"manifest: {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
