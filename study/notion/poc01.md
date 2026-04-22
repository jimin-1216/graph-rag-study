## 기술 스택 검토 및 아키텍처 설계

### 목표

- 실제 PoC에 사용할 기술 스택을 확정

### 상세 아젠다

1. 기존 RAG 아키텍처 재점검
2. Graph DB 선택 기준
    - learning curve
    - query expressiveness
    - 운영성
    - 생태계
3. 후보 스택 비교
    - Neo4j
    - RDF/SPARQL 계열
    - 기존 vector DB 병행 여부
4. 데이터 파이프라인 설계
    - ingest
    - parsing
    - chunking
    - entity extraction
    - relation extraction
    - graph loading
5. 서비스 연결 방식
    - 기존 RAG 옆에 보조 retrieval 추가
    - graph-first
    - hybrid retrieval
6. 운영 아키텍처 초안

### 실습 과제

- 기술 스택 비교표 작성
    - 도입 난이도
    - 구현 속도
    - 질의 표현력
    - 유지보수 난이도
    - PoC 적합성
- 자사 환경 기준으로 1안/2안 작성

### 산출물

- 기술 스택 선정안
- 시스템 아키텍처 초안
- 데이터 흐름도
- PoC 구현 범위 확정안