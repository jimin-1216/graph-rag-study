# 260423 Results

## 오늘 한 일

- 검색-그래프 탐색 데모를 실제로 돌려 보고 병목을 진단했다.
- 진단 메모를 작성했다.
  - `study/260423/retrieval_diagnostics.md`
- 법령 alias를 수작업 예외처리가 아니라 정규화 파이프라인으로 다루는 방향을 정했다.
- alias 해소 스크립트를 만들었다.
  - `workspace/scripts/resolve_legal_aliases.py`
- alias 해소 산출물을 만들었다.
  - `data/processed/internal_rules/legal_reference_resolved.json`
  - `data/processed/internal_rules/legal_reference_unresolved.json`
  - `data/processed/internal_rules/legal_alias_catalog.json`
  - `data/processed/internal_rules/legal_reference_resolution_summary.json`
- unresolved 기준으로 추가 법령 수집 우선순위를 정했다.
  - `study/260423/additional_law_collection_plan.md`
- 법제처 Open API로 추가 법령 11건을 수집했다.
  - `workspace/scripts/collect_additional_laws.py`
  - `data/legal/processed/additional_law_manifest_2026-04-23.json`
- 추가 수집 반영 후 alias 해소를 다시 수행했다.
  - `resolved 43 -> 79`
  - `unresolved 72 -> 36`
- 해소된 alias 결과를 Neo4j에 적재하는 로더를 만들고 실제 반영했다.
  - `workspace/scripts/load_resolved_aliases_to_neo4j.py`
- Neo4j 반영 결과:
  - `REFERS_TO_DOCUMENT`: `76`
  - `IMPLEMENTS_RESOLVED`: `17`
- 검색 데모 스크립트를 해소된 그래프 관계 우선 구조로 교체했다.
  - `workspace/scripts/run_graph_retrieval_demo.py`
- 데모 리포트를 다시 생성했다.
  - `workspace/queries/graph_retrieval_eval_2026-04-23.md`
- `REFERS_TO_DOCUMENT`를 우선 써야 하는 이유를 문서화했다.
  - `study/260423/why_prioritize_resolved_graph_links.md`

## 오늘 확인한 핵심

- 현재 병목은 alias 자체보다 `검색 단계에서 질문 의도에 맞는 조문을 고르는 문제`다.
- `REFERS_TO_DOCUMENT`를 우선 쓰면 질의 시 추측이 줄고 그래프 기반 확장이 더 안정적이다.
- 다만 `IMPLEMENTS_RESOLVED`는 문서 수준 관계라서, 조문 직접 참조가 없는 경우 상위법을 넓게 보여주는 노이즈가 있다.
- 즉 현재 파이프라인은 `alias 해소` 단계는 한 단계 올라왔고, 다음 병목은 `retriever 정밀화`다.

## 현재 상태 요약

- 내규 파싱/정규화: 기반 있음
- 법령 수집/확장: AML 핵심 축 기준으로 1차 확보 완료
- alias 해소: 파이프라인화 시작, 실제 효과 확인
- Neo4j 연결: 조문 -> 외부 법령 문서 참조 관계 적재 완료
- 검색 데모: 그래프 관계 우선으로 재구성 완료

## 남은 문제

- `역할/책임`, `기한/시기`, `절차` 같은 질문 의도별로 조문을 더 정확히 고르지 못한다.
- 현재 검색은 여전히 키워드 일치 기반 비중이 커서, 제목/구조/의미 블록 정보가 부족하다.
- `IMPLEMENTS_RESOLVED`는 조문 단위 근거가 아니라 문서 단위 근거라서 보조 신호로만 다뤄야 한다.
- unresolved 36건 중 일부는 비핵심 일반 법령 또는 내부문서 자기참조라 우선순위 재정리가 필요하다.
