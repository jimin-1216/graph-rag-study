# Alias Resolution Notes

작성일: 2026-04-23

## 작업 내용

- `workspace/scripts/resolve_legal_aliases.py` 작성
- 내부문서 `REFERS_TO_LAW_NAME` 관계를 대상으로 alias 해소 파이프라인 1차 실행
- 산출물 생성
  - `data/processed/internal_rules/legal_reference_resolved.json`
  - `data/processed/internal_rules/legal_reference_unresolved.json`
  - `data/processed/internal_rules/legal_alias_catalog.json`
  - `data/processed/internal_rules/legal_reference_resolution_summary.json`

## 현재 파이프라인

```text
raw reference
-> 문자열 정규화
-> 본문 내 이하(alias) 패턴 추출
-> 법령 후보 생성
-> 후보 점수화
-> resolved / unresolved 분리
```

## 1차 실행 결과

- resolved: `43`
- unresolved: `72`
- alias catalog: `4`

resolved 방식 분포:

- `source_text_alias`: `29`
- `compact_title`: `7`
- `override_alias`: `4`
- `exact_title`: `3`

## 해석

- 붙은 43건 중 다수는 본문에서 직접 추출한 `이하 약칭`으로 해소됐다.
- 즉 alias 문제를 전부 수동 사전으로 처리하지 않아도 되는 방향은 확인됐다.
- 다만 unresolved 72건이 남아 있고, 이 중 상당수는 현재 그래프에 없는 외부 법령을 가리킨다.

대표 unresolved 예시:

- `조세범 처벌법`
- `관세법`
- `지방세기본법`
- `특정범죄 가중처벌 등에 관한 법률`
- `공중협박자금조달금지법`

## 현재 판단

지금 unresolved는 두 부류로 나뉜다.

1. 수집 범위 밖 문제
- 현재 법령 그래프에 해당 법령이 아예 없다.
- 이 경우 alias 로직을 고쳐도 해소되지 않는다.

2. 정규화 품질 문제
- 띄어쓰기 깨짐
- 내부 규정/업무지침과 외부 법령이 섞이는 문제
- 참조 추출 시 과다 추출된 항목

## 다음 작업

1. unresolved를 `수집 필요`와 `정규화 개선 필요`로 분류한다.
2. 외부 법령 수집 우선순위를 정한다.
3. resolved 결과를 Neo4j 관계로 적재하는 스크립트를 만든다.
4. Graph RAG 데모 스크립트에서 텍스트 alias 매칭 대신 resolved 산출물을 우선 사용하도록 바꾼다.

## 추가 법령 수집 반영 후

- 추가 수집 스크립트: `workspace/scripts/collect_additional_laws.py`
- 수집 대상 계획: `study/260423/additional_law_collection_plan.md`

추가 수집 후 alias 해소 재실행 결과:

- resolved: `79`
- unresolved: `36`

증가분:

- resolved `+36`
- unresolved `-36`

해석:

- `신용정보의 이용 및 보호에 관한 법률`
- `외국환거래법`
- `조세범 처벌법`
- `관세법`
- `지방세기본법`
- `특정범죄 가중처벌 등에 관한 법률`
- `자본시장과 금융투자업에 관한 법률`
- `금융회사의 지배구조에 관한 법률`
- `금융회사의 지배구조에 관한 법률 시행령`

등이 후보군에 들어오면서 alias 해소율이 크게 올라갔다.

현재 남은 unresolved의 주된 부류:

1. 내부 문서 자기참조
- `자금세탁방지업무 취급지침`
- `자금세탁방지업무 취급규정`

2. AML 핵심 범위 밖 일반 법령
- `공공기관의 운영에 관한 법률`
- `정부출연연구기관 등의 설립·운영 및 육성에 관한 법률`
- `지방공기업법`
- `상법`

3. 별도 행정규칙/시장규정
- `유가증권시장 공시규정`
- `코스닥시장 공시규정`

현재 판단:

- AML 핵심 축 기준으로는 추가 수집 효과가 충분히 있었다.
- 다음은 `resolved 결과를 실제 그래프 관계로 적재`하는 단계로 넘어가도 된다.
