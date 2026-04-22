# graph-rag-study

이 저장소는 지식그래프, 온톨로지, Graph RAG 스터디와 AML 규정 PoC 작업을 함께 관리한다.

## 구조

- `study/`
  - 스터디 기록과 주차별 자료
  - `notion/`: 당초 계획 문서
  - `260415/`: 지난주 실제 스터디 자료
  - `260422/`: 이번 주 기록과 결과
- `data/`
  - `raw/`: 원본 문서
  - `processed/`: 전처리 결과물
- `workspace/`
  - `scripts/`: 추출, 적재, 실험 스크립트
  - `extracted/`: 문서 파싱 및 추출 결과
  - `graph/`: 그래프 스키마, 적재 파일, 샘플 데이터
  - `queries/`: Cypher 및 질의 예시

## 이번 주 작업 원칙

- 원본 PDF는 `data/raw/`에 유지한다.
- 전처리 산출물은 `data/processed/` 또는 `workspace/extracted/`에 둔다.
- Neo4j 적재용 데이터와 그래프 스키마는 `workspace/graph/`에 둔다.
- 실습 기록과 의사결정 메모는 `study/260422/`에 남긴다.
