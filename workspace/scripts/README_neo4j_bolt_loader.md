# Neo4j Bolt Loader

법제처 정규화 결과를 Neo4j에 직접 적재하는 Python 로더다.

## 입력 파일

- `data/legal/processed/legal_documents.json`
- `data/legal/processed/legal_units.json`
- `data/legal/processed/legal_relations.json`

## 필요한 환경변수

`workspace/.env`에 아래 값을 넣는다.

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j
```

`LAW_OPEN_OC`는 그대로 두어도 된다.

## 실행

```powershell
python .\workspace\scripts\load_legal_to_neo4j.py
```

## 현재 적재 대상

- `LegalDocument`
- `LegalUnit`
- `LegalReference`
- 관계
  - `HAS_UNIT`
  - `HAS_CHILD`
  - `BELONGS_TO`
  - `LEGAL_REFERENCE`

## 참고

- `LEGAL_REFERENCE`의 세부 의미는 관계 속성 `relation_type`에 저장한다.
- 아직 해소되지 않은 참조 텍스트는 `LegalReference` 노드로 유지한다.
- 이후 단계에서 `LegalReference -> LegalDocument/LegalUnit` 해소 작업이 필요하다.
