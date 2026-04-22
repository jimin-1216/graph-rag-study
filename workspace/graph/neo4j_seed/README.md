# Neo4j Load Guide

이 디렉터리의 CSV는 Neo4j 초기 적재용 시드 데이터다.

## 파일

- `legal_documents.csv`
- `legal_units.csv`
- `legal_relations.csv`
- `load_neo4j.cypher`

## 전제

- Neo4j Desktop 또는 로컬 Neo4j 서버가 실행 중이어야 한다.
- CSV 3개를 Neo4j `import` 디렉터리에 복사해야 한다.
- `load_neo4j.cypher`는 `cypher-shell` 또는 Neo4j Browser에서 실행한다.

## 권장 순서

1. 이 디렉터리의 CSV 3개를 Neo4j `import` 폴더로 복사
2. `load_neo4j.cypher` 실행
3. 적재 결과 확인

## 예시 확인 쿼리

```cypher
MATCH (d:LegalDocument) RETURN count(d);
```

```cypher
MATCH (u:LegalUnit) RETURN count(u);
```

```cypher
MATCH ()-[r]->() RETURN type(r), count(*) ORDER BY count(*) DESC;
```

## 참고

- `HAS_UNIT`, `HAS_CHILD`는 실제 노드 간 관계다.
- `REFERS_TO_LAW_NAME`, `CITES_ARTICLE_TEXT`, `IMPLEMENTS_CANDIDATE`는 아직 미해결 참조이므로 `LegalReference` 노드로 적재한다.
- 이후 단계에서 `LegalReference`를 실제 `LegalDocument` 또는 `LegalUnit`에 해소하는 정합화 작업이 필요하다.
