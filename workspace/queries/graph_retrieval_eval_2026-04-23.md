# Graph Retrieval Eval

작성일: 2026-04-23

## Query 1

- 질문: `의심거래 보고 절차는 어떻게 되나`
- 키워드: `의심거래, 보고`

### 상위 내부규정 검색 결과

- `자금세탁방지업무 취급규정 원문-원본 / 제15조 / article` score=1 keywords=보고
  - 제15조 (제도운용) 보고책임자는 직원알기제도의 이행과 관련된 절차와 방법을 수립하고 수립된 절차 등이 원활하게 운용될 수 있도록 적절한 조치를 취하 여야 한다.
- `자금세탁방지업무 취급규정 원문-원본 / 제1조 / article` score=1 keywords=보고
  - 제1조 (시행일) 이 규정은 2014년 10월 23일부터 시행한다. 다만 제3조제2항의 불법 차명금융거래 관련 의심되는 거래 보고는 2014년 11월 29일부터 시행 한다.
- `자금세탁방지업무 취급지침 원문-원본 / 제54조 / article` score=1 keywords=보고
  - 제54조 (보고내용) 보고하여야 할 내용은 다음 각 호와 같다. - 1. 은행명 및 소재지 - 2. 보고대상 금융거래가 발생한 일자 및 장소 - 3. 보고대상 금융거래의 상대방 - 4. 보고대상 금융거래의 내용 - 5. 의심되는 합당한 근거
- `자금세탁방지업무 취급지침 원문-원본 / 제58조 / article` score=1 keywords=보고
  - 제58조 (보고내용) 보고하여야 할 내용은 다음 각 호와 같다. - 1. 은행명 및 소재지 - 2. 현금의 지급 또는 영수가 이루어진 일자 및 장소 - 3. 현금의 지급 또는 영수의 상대방 - 4. 현금의 지급 또는 영수의 내용 - 5. 무통장 입금에 의한 송금시 수취인 계좌에 관한 정보
- `자금세탁방지업무 취급규정 원문-원본 / 제27조 / article` score=1 keywords=보고
  - 제27조 (자료의 보존) 보고책임자는 고객확인 및 검증자료, 금융거래기록, 의심 되는 거래 보고서 등을 포함한 내·외부 보고서 및 관련 자료 등을 관계 법 령 등에서 정하는 바에 따라 보존하여야 한다.<개정 2014.10.23.> [제28조에서 이동, 종전 제27조는 제28조로 이동 2025.5.22.]

### 상위 법령 확장

- `internal:aml_policy:article:제15조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령` (method=override_alias, score=1.0)
  - IMPLEMENTS_RESOLVED -> `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` (method=exact_title, score=1.0)
- `internal:aml_policy:article:제1조`
  - REFERS_TO_DOCUMENT `특정금융정보법` -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=source_text_alias, score=1.0)
  - REFERS_TO_DOCUMENT `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` -> `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` (method=exact_title, score=1.0)
- `internal:aml_guideline:article:제54조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `금융실명거래 및 비밀보장에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률` (method=compact_title, score=1.0)
- `internal:aml_guideline:article:제58조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `금융실명거래 및 비밀보장에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률` (method=compact_title, score=1.0)
- `internal:aml_policy:article:제27조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령` (method=override_alias, score=1.0)
  - IMPLEMENTS_RESOLVED -> `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` (method=exact_title, score=1.0)

### 관찰된 문제

- 상위 검색 결과의 키워드 일치 수가 낮아 질의 의도와의 정합성이 약함

## Query 2

- 질문: `고액 현금거래 보고 기한은?`
- 키워드: `고액, 현금거래, 보고, 고액현금거래`

### 상위 내부규정 검색 결과

- `자금세탁방지업무 취급지침 원문-원본 / 제63조 / article` score=4 keywords=고액,현금거래,보고,고액현금거래
  - 제63조 (보존대상) ① 고객확인 및 검증과 관련하여 보존하여야 할 자료는 다음 각 호와 같다.<개정 2019.6.27.> - 1. 고객(대리인, 실제 소유자 포함)에 대한 고객거래확인서, 실명확인증표 사 본, 고객 신원정보 확인 및 검증을 위해 확보한 자료 - 2. 고객 신원정보 이외에 금융거래의 목적 및 성격을 파악하기 위해 추가로 확인한 자료 - 3. 고객확인을 위한 내부승인 관련 자료 - 4. 계좌개설 일시, 계좌개설 
- `자금세탁방지업무 취급규정 원문-원본 / 제7조 / article` score=4 keywords=고액,현금거래,보고,고액현금거래
  - 제7조 (보고책임자) ① 보고책임자는 AML보고책임자로 하며, 타 업무를 겸임할 수 있다.<개정 2014.10.23., 2025.1.16.> - ② 보고책임자의 역할 및 책임은 다음 각 호와 같다.<개정 2014.10.23., 2019.6.27., 2025.5.22.> - 1. 의심되는 거래 및 고액 현금거래의 금융정보분석원장 앞 보고 - 2. 금융거래시 고객확인 이행관련 업무 총괄 - 3. 다음 각 목의 자금세탁방지등을 위한
- `자금세탁방지업무 취급지침 원문-원본 / 제56조 / article` score=4 keywords=고액,현금거래,보고,고액현금거래
  - 제56조 (보고대상) ① 고액현금거래 보고(CTR)대상(외화 제외)은 다음 각 호와 같다. 다만, 금융회사(카지노사업자, 가상자산사업자, 자금세탁행위와 공중협 박자금조달행위에 이용될 위험성이 높은 자로서 금융정보분석원장이 고시하 는 자 제외), 국가, 지방자치단체와의 현금의 지급 또는 영수는 제외한다.<개 정 2014.4.18., 2019.6.27., 2021.3.23.> - 1. 은행이 1거래일 동안 동일인에게 지급한 현금거
- `자금세탁방지업무 취급지침 원문-원본 / 제67조 / article` score=4 keywords=고액,현금거래,보고,고액현금거래
  - 제67조 (기타) 이 지침에서 정하지 아니한 사항 중 자금세탁방지등 업무 수행에 필요한 세부사항은 보고책임자가 따로 정할 수 있다. - [제65조에서 이동 2024.11.4.] 부 칙<2001.11.28.> - 이 지침은 2001년 11월 28일부터 시행한다. - 부 칙<2002.11.11.> - 이 지침은 2002년 11월 11일부터 시행한다. 부 칙<2004.1.20.> 이 지침은 2004년 1월 20일부터 시행한다. 부 
- `자금세탁방지업무 취급지침 원문-원본 / ② / paragraph` score=4 keywords=고액,현금거래,보고,고액현금거래
  - ② 담당책임자와 보고책임자는 고액현금거래보고에서 오류가 발견된 경우 해당 오보고를 신속하게 수정 또는 취소한다. -

### 상위 법령 확장

- `internal:aml_guideline:article:제63조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `금융실명거래 및 비밀보장에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률` (method=compact_title, score=1.0)
- `internal:aml_policy:article:제7조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령` (method=override_alias, score=1.0)
  - IMPLEMENTS_RESOLVED -> `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` (method=exact_title, score=1.0)
- `internal:aml_guideline:article:제56조`
  - REFERS_TO_DOCUMENT `금융실명법` -> `금융실명거래 및 비밀보장에 관한 법률` (method=source_text_alias, score=1.0)
- `internal:aml_guideline:article:제67조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `금융실명거래 및 비밀보장에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률` (method=compact_title, score=1.0)
- `internal:aml_guideline:paragraph:제56조_8`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `금융실명거래 및 비밀보장에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률` (method=compact_title, score=1.0)

### 관찰된 문제

- 뚜렷한 문제 없음

## Query 3

- 질문: `보고책임자의 역할은 무엇인가`
- 키워드: `보고책임자, 무엇`

### 상위 내부규정 검색 결과

- `자금세탁방지업무 취급규정 원문-원본 / 제15조 / article` score=1 keywords=보고책임자
  - 제15조 (제도운용) 보고책임자는 직원알기제도의 이행과 관련된 절차와 방법을 수립하고 수립된 절차 등이 원활하게 운용될 수 있도록 적절한 조치를 취하 여야 한다.
- `자금세탁방지업무 취급규정 원문-원본 / 제27조 / article` score=1 keywords=보고책임자
  - 제27조 (자료의 보존) 보고책임자는 고객확인 및 검증자료, 금융거래기록, 의심 되는 거래 보고서 등을 포함한 내·외부 보고서 및 관련 자료 등을 관계 법 령 등에서 정하는 바에 따라 보존하여야 한다.<개정 2014.10.23.> [제28조에서 이동, 종전 제27조는 제28조로 이동 2025.5.22.]
- `자금세탁방지업무 취급지침 원문-원본 / 제57조 / article` score=1 keywords=보고책임자
  - 제57조 (보고시기 및 방법) ① 보고책임자는 보고대상거래를 전산으로 추출하여 금융거래 발생후 30일 이내에 금융정보분석원장에게 보고하여야 한다.<개정 2024.3.18.> - ② 고액 현금거래 보고방법은 제53조제2항제2호의 규정을 준용한다. - ③ 이 경우 담당책임자는 재검토 결과를 자금세탁방지시스템에 등록하여야 한다.<개정 2025.5.22.>
- `자금세탁방지업무 취급규정 원문-원본 / 제26조 / article` score=1 keywords=보고책임자
  - 제26조 (고액 현금거래 보고) 보고책임자는 보고대상 고액 현금거래를 추출하여 동거래 발생후 30일 이내에 금융정보분석원장에게 보고하여야 한다.<개정 2025.5.22.> - 제26조의2(모니터링 체계 등) 은행은 자금세탁등을 예방하기 위하여 고객과의 금융거래 등에 대한 지속적인 모니터링체계를 수립하여 운영하여야 한다. [본조신설 2025.5.22.]
- `자금세탁방지업무 취급규정 원문-원본 / 제12조 / article` score=1 keywords=보고책임자
  - 제12조 (교육 및 연수) ① 보고책임자는 자금세탁방지제도에 대한 임직원의 이 해와 관심도 제고를 위한 교육 및 연수프로그램을 수립하고 연1회 이상 교 육을 실시하여야 한다. - ② 교육 및 연수는 직위 또는 담당업무 등 교육대상에 따라 적절하게 구분 하여 실시하되, 집합, 전달, 화상 등 다양한 방법으로 실시할 수 있다. - ③ 교육 및 연수를 실시한 후에는 그 일자, 대상, 내용 등 교육 관련사항을 기록· 보존하여야 한다.

### 상위 법령 확장

- `internal:aml_policy:article:제15조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령` (method=override_alias, score=1.0)
  - IMPLEMENTS_RESOLVED -> `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` (method=exact_title, score=1.0)
- `internal:aml_policy:article:제27조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령` (method=override_alias, score=1.0)
  - IMPLEMENTS_RESOLVED -> `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` (method=exact_title, score=1.0)
- `internal:aml_guideline:article:제57조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `금융실명거래 및 비밀보장에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률` (method=compact_title, score=1.0)
- `internal:aml_policy:article:제26조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령` (method=override_alias, score=1.0)
  - IMPLEMENTS_RESOLVED -> `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` (method=exact_title, score=1.0)
- `internal:aml_policy:article:제12조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령` (method=override_alias, score=1.0)
  - IMPLEMENTS_RESOLVED -> `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` (method=exact_title, score=1.0)

### 관찰된 문제

- 상위 검색 결과의 키워드 일치 수가 낮아 질의 의도와의 정합성이 약함
- 조문 직접 참조 없이 문서 수준 연결만 보여 상위법 근거가 넓게 제시됨
