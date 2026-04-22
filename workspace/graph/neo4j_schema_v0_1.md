# Neo4j Schema v0.1

이번 PoC의 핵심은 의미 추출 이전에 법령 구조를 먼저 안정적으로 잡는 것이다.
따라서 `조문`은 통짜 노드가 아니라 `조/항/호/목`까지 분해 가능한 구조로 설계한다.

## 설계 원칙

- 문서 위계와 조문 위계를 먼저 표현한다.
- 의미 노드는 구조 노드에 매달리는 방식으로 설계한다.
- 상위법령과 내부규정의 관계를 먼저 표현한다.
- 인용/참조/위임 관계를 별도 관계 타입으로 분리한다.
- 검사매뉴얼 항목과의 대응관계까지 확장 가능해야 한다.

## 노드

### `LegalDocument`

- 예: 법률, 시행령, 고시, 내부규정, 내부지침, 검사매뉴얼
- 주요 속성
  - `document_id`
  - `title`
  - `document_type`
  - `authority`
  - `effective_date`
  - `promulgation_date`
  - `version_label`
  - `source_url`
  - `source_system`

### `LegalUnit`

- 예: 조, 항, 호, 목
- 주요 속성
  - `unit_id`
  - `document_id`
  - `unit_type`
  - `unit_no`
  - `full_citation`
  - `heading`
  - `text`
  - `page_start`
  - `page_end`
  - `effective_date`

### `SemanticUnit`

- 구조 노드에서 추출된 의미 단위
- 주요 속성
  - `semantic_id`
  - `semantic_type`
  - `label`
  - `text`
  - `confidence`

### `ControlItem`

- 검사매뉴얼의 점검 항목
- 주요 속성
  - `control_id`
  - `name`
  - `category`
  - `description`

## `SemanticUnit.semantic_type` 초기값

- `Definition`
- `Obligation`
- `Subject`
- `Exception`
- `Sanction`

필요 시 다음을 추가한다.

- `Agency`
- `Report`
- `Deadline`
- `Procedure`

## 관계

### 구조 관계

- `(:LegalDocument)-[:HAS_UNIT]->(:LegalUnit)`
- `(:LegalUnit)-[:HAS_CHILD]->(:LegalUnit)`
- `(:LegalUnit)-[:PART_OF]->(:LegalUnit)`

### 문서 관계

- `(:LegalDocument)-[:DELEGATED_BY]->(:LegalDocument)`
- `(:LegalDocument)-[:IMPLEMENTS]->(:LegalDocument)`
- `(:LegalDocument)-[:BASED_ON]->(:LegalDocument)`

### 조문 관계

- `(:LegalUnit)-[:CITES]->(:LegalUnit)`
- `(:LegalUnit)-[:REFERS_TO]->(:LegalUnit)`
- `(:LegalUnit)-[:IMPLEMENTS]->(:LegalUnit)`

### 의미 관계

- `(:LegalUnit)-[:EXPRESSES]->(:SemanticUnit)`
- `(:SemanticUnit)-[:APPLIES_TO]->(:SemanticUnit)`
- `(:SemanticUnit)-[:EXCEPTION_TO]->(:SemanticUnit)`
- `(:SemanticUnit)-[:SANCTION_FOR]->(:SemanticUnit)`

### 검사 대응 관계

- `(:LegalDocument)-[:ALIGNS_WITH]->(:ControlItem)`
- `(:LegalUnit)-[:ALIGNS_WITH]->(:ControlItem)`
- `(:SemanticUnit)-[:ALIGNS_WITH]->(:ControlItem)`

## 식별자 예시

- `document_id`
  - `law:spec_financial_transaction_act`
  - `internal:aml_policy`
- `unit_id`
  - `law:spec_financial_transaction_act:art4:para2:item1`
  - `internal:aml_policy:art12:para3`
- `semantic_id`
  - `sem:internal:aml_policy:art12:para3:obligation:001`

## 최소 질의 예시

### 1. 특정 내부규정 조항이 어떤 상위 법령을 근거로 하는가

```cypher
MATCH (d:LegalDocument {document_id: "internal:aml_policy"})-[:IMPLEMENTS]->(upper:LegalDocument)
RETURN d, upper
```

### 2. 특정 조항의 하위 항/호/목 구조 조회

```cypher
MATCH (u:LegalUnit {unit_id: "internal:aml_policy:art12"})
OPTIONAL MATCH (u)-[:HAS_CHILD*1..3]->(child:LegalUnit)
RETURN u, child
```

### 3. 특정 의무의 대상과 예외 찾기

```cypher
MATCH (u:LegalUnit)-[:EXPRESSES]->(o:SemanticUnit {semantic_type: "Obligation"})
OPTIONAL MATCH (o)-[:APPLIES_TO]->(s:SemanticUnit {semantic_type: "Subject"})
OPTIONAL MATCH (e:SemanticUnit {semantic_type: "Exception"})-[:EXCEPTION_TO]->(o)
RETURN u, o, s, e
```

## 이번 주 구현 범위

- `LegalDocument`
- `LegalUnit`
- `SemanticUnit`
  - `Definition`, `Obligation`, `Subject`, `Exception`, `Sanction`
- `ControlItem`
- 구조 관계
  - `HAS_UNIT`, `HAS_CHILD`
- 핵심 관계
  - `IMPLEMENTS`, `CITES`, `REFERS_TO`, `EXPRESSES`, `APPLIES_TO`, `EXCEPTION_TO`, `SANCTION_FOR`, `ALIGNS_WITH`

## 이번 주에는 아직 하지 않는 것

- 모든 조문 자동 정규화 완성
- 모든 상위법령 자동 수집 완성
- 개정 이력 전수 반영
- 판례/해석례/FAQ 통합
- 완전한 ontology 확정
