<aside>

</aside>

## 법률·규제·정책 도메인 온톨로지 설계

### 목표

- 우리 서비스에 맞는 도메인 온톨로지 초안을 만들기

### 상세 아젠다

1. 문서 레벨 구조 정의
    - 법
    - 시행령
    - 시행규칙
    - 고시
    - 가이드라인
    - 내부정책
2. 조문 구조 정의
    - 장 / 절 / 조 / 항 / 호
3. 의미 구조 정의
    - 정의
    - 의무
    - 금지
    - 허용
    - 예외
    - 면제
    - 제재
4. 운영 구조 정의
    - 기관
    - 제출 의무
    - 보고 기한
    - 대상자
5. 시간 구조 정의
    - 제정일
    - 시행일
    - 개정일
    - 유효기간
6. 근거 및 출처 구조 정의
    - 참조
    - 인용
    - 해석례
    - FAQ
    - 내부통제 매핑

### 실습 과제

- 자사 핵심 도메인 1개 선택 → 내규 컴플라이언스 대상 실습
- 아래 표를 채우기
    - 개체명
    - 정의
    - 예시
    - 필수 속성
    - 관련 관계
- “반드시 모델링해야 하는 것 / 나중에 넣어도 되는 것” 구분

### 산출물

- 도메인 온톨로지 v0.2
- 용어사전
- 필수 개체-관계 목록
- 범위 제외 항목 목록

## Palantir Ontology

### 목표

- Ontology를 단순 분류체계가 아니라 운영 가능한 semantic layer로 이해
- 팔란티어 온톨로지는 개념 이해 수준으로 간략히만 짚고 넘어갈 예정

### 상세 아젠다

1. Palantir Ontology의 핵심 개념
    - object
    - link
    - action
2. 데이터 저장 구조와 의미 계층의 분리
3. “현실 세계의 업무 객체”를 시스템 상에서 어떻게 표현하는가
4. 우리 회사 서비스에 적용 시
    - object는 무엇인가
    - link는 무엇인가
    - action은 무엇인가
5. 내부 운영 시나리오 연결
    - 규제 변경 영향 분석
    - 정책 업데이트 추천
    - compliance checklist 생성

### 실습 과제 (생략 가능)

- 자사 도메인을 Palantir 스타일로 재정의
    - Object Type
    - Link Type
    - Action Type
- 예시 5개 이상 작성

예시:

- Object: Regulation, Provision, Agency, Obligation, Policy, Control
- Link: REFERS_TO, APPLIES_TO, EXEMPTS, ENFORCED_BY, IMPLEMENTED_BY
- Action: AssessImpact, GenerateChecklist, TraceChange, ReviewControl

### 산출물

- Object/Link/Action 정의서
- 운영형 ontology 관점 문서
- 내부 적용 시나리오 초안