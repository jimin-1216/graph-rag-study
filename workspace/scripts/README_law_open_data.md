# LAW OPEN DATA 수집 스켈레톤

법제처 국가법령정보 공동활용 Open API 기준 스켈레톤이다.

기준일: 2026-04-22
가이드: https://open.law.go.kr/LSO/openApi/guideList.do

## 준비

PowerShell에서 OC 키를 환경변수로 넣는다.

```powershell
$env:LAW_OPEN_OC="발급받은_OC_키"
```

## 실행

```powershell
python .\workspace\scripts\collect_law_open_data.py
```

## 저장 위치

- 원문 응답: `data/legal/raw/`
- 수집 매니페스트: `data/legal/processed/law_open_data_manifest.json`

## 현재 포함 대상

- 특정 금융거래정보의 보고 및 이용 등에 관한 법률
- 특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령
- 자금세탁방지 및 공중협박자금조달금지에 관한 업무규정
- 범죄수익은닉의 규제 및 처벌 등에 관한 법률
- 금융실명거래 및 비밀보장에 관한 법률
- 금융실명거래 및 비밀보장에 관한 법률 시행령

## 주의

- 이 스크립트는 API 가이드 기준의 초기 골격이다.
- 실제 응답 필드명은 OC 키로 첫 호출 후 확인해서 후처리 스키마를 보정해야 한다.
- 행정규칙 API의 세부 파라미터는 첫 응답 검증 후 조정할 수 있다.
