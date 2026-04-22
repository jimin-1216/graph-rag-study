# Neo4j 데모 쿼리

작성일: 2026-04-22

## 목적

20분 내 데모에서 "법령 그래프가 실제로 올라가 있고 탐색 가능하다"는 점을 보여주기 위한 최소 Cypher 모음.

## 1. 전체 적재 상태 확인

```cypher
MATCH (d:LegalDocument) RETURN count(d) AS document_count;
```

```cypher
MATCH (u:LegalUnit) RETURN count(u) AS unit_count;
```

```cypher
MATCH (r:LegalReference) RETURN count(r) AS reference_count;
```

```cypher
MATCH ()-[rel]->() RETURN type(rel) AS relation_type, count(*) AS count ORDER BY count DESC;
```

## 2. 어떤 법령이 올라가 있는지 보기

```cypher
MATCH (d:LegalDocument)
RETURN d.document_id, d.title, d.document_type, d.effective_date
ORDER BY d.title;
```

## 3. 특금법의 조문 구조 보기

```cypher
MATCH (d:LegalDocument {document_id: 'law:spec_financial_transaction_act'})-[:HAS_UNIT]->(u:LegalUnit)
RETURN u.unit_id, u.unit_type, u.unit_no, u.title
ORDER BY u.unit_type, u.unit_no
LIMIT 30;
```

## 4. 특정 조문 아래 항/호/목 보기

```cypher
MATCH (a:LegalUnit {unit_id: 'law:spec_financial_transaction_act:article:2'})
OPTIONAL MATCH (a)-[:HAS_CHILD*1..3]->(child:LegalUnit)
RETURN a.unit_id AS article_id, child.unit_id AS child_id, child.unit_type, child.unit_no, child.title, child.text
LIMIT 30;
```

## 5. 내부적으로 많이 참조되는 법령명 보기

```cypher
MATCH (:LegalUnit)-[r:LEGAL_REFERENCE]->(ref:LegalReference)
WHERE r.relation_type = 'REFERS_TO_LAW_NAME'
RETURN ref.target_id AS referenced_law_name, count(*) AS freq
ORDER BY freq DESC
LIMIT 20;
```

## 6. 특정 업무규정이 어떤 법령명을 참조하는지 보기

```cypher
MATCH (d:LegalDocument {document_id: 'law:aml_and_cft_business_rule'})-[:HAS_UNIT]->(u:LegalUnit)
MATCH (u)-[r:LEGAL_REFERENCE]->(ref:LegalReference)
WHERE r.relation_type = 'REFERS_TO_LAW_NAME'
RETURN DISTINCT ref.target_id AS referenced_law_name
ORDER BY referenced_law_name
LIMIT 30;
```

## 7. 특금법 체계도 기반 구현 후보 보기

```cypher
MATCH (d:LegalDocument {document_id: 'law:spec_financial_transaction_act'})-[r:LEGAL_REFERENCE]->(ref:LegalReference)
WHERE r.relation_type = 'IMPLEMENTS_CANDIDATE'
RETURN ref.target_id AS candidate_document_title
ORDER BY candidate_document_title;
```

## 8. 법령 간 연결 시연용 설명 포인트

- `LegalDocument`: 법률, 시행령, 고시 같은 문서 단위
- `LegalUnit`: 조/항/호/목 같은 조문 구조 단위
- `HAS_UNIT`, `HAS_CHILD`: 문서 구조 탐색
- `LEGAL_REFERENCE`: 인용, 참조, 구현 후보 같은 관계의 보존 노드

## 9. 데모 멘트

- "법제처 Open API로 상위 법령과 행정규칙을 가져왔다."
- "문서 전체를 통으로 넣은 게 아니라 조문 구조까지 쪼개서 Neo4j에 적재했다."
- "이제는 단순 텍스트 검색이 아니라 특정 조문에서 상위법, 참조 법령, 세부 항목까지 따라갈 수 있다."

## 10. 내규 2개 적재 확인

```cypher
MATCH (d:LegalDocument {kind:'internal_rule'})
RETURN d.document_id, d.title
ORDER BY d.document_id;
```

```cypher
MATCH (u:LegalUnit)
WHERE u.document_id STARTS WITH 'internal:'
RETURN count(u) AS internal_unit_count;
```

## 11. 내규와 상위법 후보 연결 확인

```cypher
MATCH (s:LegalDocument)-[:IMPLEMENTS_CANDIDATE_MANUAL]->(t:LegalDocument)
RETURN s.title AS source, t.title AS target
ORDER BY source, target;
```

### 설명 포인트

- `IMPLEMENTS_CANDIDATE_MANUAL`은 오늘 데모용으로 넣은 초기 문서 수준 후보 연결이다.
- 조문 단위 자동 매핑은 다음 단계 과제이고, 현재는 "내규 + 상위법을 함께 그래프에 올렸다"는 점을 보여주는 용도다.
