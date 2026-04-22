<aside>

</aside>

## Graph RAG 설계

### 목표

- 그래프를 검색에 어떻게 결합할지 설계한다.

### 상세 아젠다

1. 기존 RAG의 retrieval 한계
2. Graph RAG 개념
    - entity 중심 retrieval
    - graph traversal
    - hybrid retrieval
    - subgraph grounding
3. 질의 유형별 처리 전략
    - 단일 조문 확인형
    - 정의/적용 대상 확인형
    - 예외/제재 연결형
    - 개정 이력 비교형
    - 다중 문서 탐색형
4. 응답 생성 단계 설계
    - 근거 chunk
    - 그래프 경로
    - 출처 표시
5. hallucination 억제 전략
    - 그래프에 없는 관계는 추론 금지
    - provenance 없는 노드는 답변에서 제외

### 실습 과제

- 대표 질문 / 보고서 작성요청 예시를 골라 질의 흐름 설계
    - 질의에서 엔티티 추출
    - 엔티티 정규화
    - 관련 노드 검색
    - 주변 그래프 탐색
    - 관련 chunk 회수
    - 최종 답변 생성
- baseline RAG와 graph-enhanced RAG를 비교하는 플로우차트 작성

### 산출물

- Graph RAG 설계 문서
- 질의 처리 플로우
- 대표 질의별 retrieval 전략표

## 데이터 파이프라인 구축과 품질 관리

### 목표

- 문서로부터 그래프를 만드는 데이터 파이프라인을 설계한다.

### 상세 아젠다

1. 문서 수집 범위 확정
2. 문서 정규화
    - 문서 단위
    - 조문 단위
    - 개정판 분리
3. chunking 전략
    - 조문 중심
    - 문단 중심
    - 정의/예외 단위 분리
4. entity extraction 전략
    - 룰 기반
    - LLM 기반
    - hybrid
5. relation extraction 전략
6. entity resolution / canonicalization
7. provenance 저장 방식
8. temporal/version 모델링
9. 데이터 품질 검수 방법

### 실습 과제

- 샘플 문서 10여개에 대해 아래 설계 적용
    - 입력 형식
    - 파싱 방식
    - 추출 항목
    - 오류 유형
- relation extraction validation sheet 작성

### 산출물

- 데이터 파이프라인 설계서
- extraction rule/prompt 초안
- 품질 검수 체크리스트
- 에러 유형 정의서