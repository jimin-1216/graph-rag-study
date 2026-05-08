# Graph Retrieval Eval

작성일: 2026-04-24

## Query 1

- 질문: `의심거래 보고 절차는 어떻게 되나`
- 의도: `procedure`
- 주체: `의심거래 `
- 키워드: `의심거래, 보고`

### 상위 내부규정 검색 결과

- `자금세탁방지업무 취급지침 원문-원본 / 제54조 / article` score=7.5 base=1 keywords=보고
  - features: article_type_bonus=1.0, procedure_pattern=1.0, enumeration_pattern=1.0
  - 제54조 (보고내용) 보고하여야 할 내용은 다음 각 호와 같다. - 1. 은행명 및 소재지 - 2. 보고대상 금융거래가 발생한 일자 및 장소 - 3. 보고대상 금융거래의 상대방 - 4. 보고대상 금융거래의 내용 - 5. 의심되는 합당한 근거
- `자금세탁방지업무 취급지침 원문-원본 / 제58조 / article` score=7.5 base=1 keywords=보고
  - features: article_type_bonus=1.0, procedure_pattern=1.0, enumeration_pattern=1.0
  - 제58조 (보고내용) 보고하여야 할 내용은 다음 각 호와 같다. - 1. 은행명 및 소재지 - 2. 현금의 지급 또는 영수가 이루어진 일자 및 장소 - 3. 현금의 지급 또는 영수의 상대방 - 4. 현금의 지급 또는 영수의 내용 - 5. 무통장 입금에 의한 송금시 수취인 계좌에 관한 정보
- `자금세탁방지업무 취급규정 원문-원본 / 제4조 / article` score=7.5 base=1 keywords=보고
  - features: article_type_bonus=1.0, procedure_pattern=1.0, enumeration_pattern=1.0
  - 제4조 (이사회) 자금세탁방지등 활동과 관련하여 이사회가 수행하여야 할 역할 및 책임은 다음 각 호와 같다.<개정 2025.5.22.> - 1. 「특정금융정보법」 제5조제1항제2호에 따른 절차 및 업무지침(이하 “업 무지침”이라 한다)인 이 규정의 제정·개정 및 폐지 - 2. 독립적 감사 결과 및 사후조치에 대한 검토와 승인 - 3. 은행장·준법감시인·보고책임자 등에게 내부통제체계(「독점규제 및 공 정거래에 관한 법률」제2조 
- `자금세탁방지업무 취급규정 원문-원본 / 제6조 / article` score=7.5 base=1 keywords=보고
  - features: article_type_bonus=1.0, procedure_pattern=1.0, enumeration_pattern=1.0
  - 제6조 (감사) 자금세탁방지등 활동과 관련하여 감사가 수행하여야 할 역할 및 책임은 다음 각 호와 같다. - 1. 감사는 경영진과 독립적인 입장에서 연1회 이상 자금세탁방지등 업무의 운영실태를 조사·점검·평가하여 이사회에 보고하여야 한다. - 2. 감사는 자금세탁방지등 업무의 운영에 관하여 시정의견이 있는 경우, 이 를 포함하여 이사회에 보고하고 문제점을 시정하게 하는 등 다음 각 목의 업무를 수행한다. - 가. 자금세탁방지등
- `자금세탁방지업무 취급규정 원문-원본 / 제15조 / article` score=6.5 base=1 keywords=보고
  - features: article_type_bonus=1.0, procedure_title=1.0
  - 제15조 (제도운용) 보고책임자는 직원알기제도의 이행과 관련된 절차와 방법을 수립하고 수립된 절차 등이 원활하게 운용될 수 있도록 적절한 조치를 취하 여야 한다.

### 상위 법령 확장

- `internal:aml_guideline:article:제54조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `금융실명거래 및 비밀보장에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률` (method=compact_title, score=1.0)
- `internal:aml_guideline:article:제58조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `금융실명거래 및 비밀보장에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률` (method=compact_title, score=1.0)
- `internal:aml_policy:article:제4조`
  - REFERS_TO_DOCUMENT `특정금융정보법` -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=source_text_alias, score=1.0)
- `internal:aml_policy:article:제6조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령` (method=override_alias, score=1.0)
  - IMPLEMENTS_RESOLVED -> `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` (method=exact_title, score=1.0)
- `internal:aml_policy:article:제15조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령` (method=override_alias, score=1.0)
  - IMPLEMENTS_RESOLVED -> `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` (method=exact_title, score=1.0)

### 관찰된 문제

- 뚜렷한 문제 없음

## Query 2

- 질문: `고액 현금거래 보고 기한은?`
- 의도: `deadline`
- 주체: `고액현금거래 `
- 키워드: `고액, 현금거래, 보고, 고액현금거래`

### 상위 내부규정 검색 결과

- `자금세탁방지업무 취급지침 원문-원본 / 제57조 / article` score=23.5 base=3 keywords=고액,현금거래,보고
  - features: article_type_bonus=1.0, deadline_term=1.0, deadline_title=3.0, report_title=1.0
  - 제57조 (보고시기 및 방법) ① 보고책임자는 보고대상거래를 전산으로 추출하여 금융거래 발생후 30일 이내에 금융정보분석원장에게 보고하여야 한다.<개정 2024.3.18.> - ② 고액 현금거래 보고방법은 제53조제2항제2호의 규정을 준용한다. - ③ 이 경우 담당책임자는 재검토 결과를 자금세탁방지시스템에 등록하여야 한다.<개정 2025.5.22.>
- `자금세탁방지업무 취급지침 원문-원본 / 제56조 / article` score=14.5 base=4 keywords=고액,현금거래,보고,고액현금거래
  - features: subject_in_lead=1.0, subject_in_text=2, article_type_bonus=1.0, deadline_term=1.0, report_title=1.0
  - 제56조 (보고대상) ① 고액현금거래 보고(CTR)대상(외화 제외)은 다음 각 호와 같다. 다만, 금융회사(카지노사업자, 가상자산사업자, 자금세탁행위와 공중협 박자금조달행위에 이용될 위험성이 높은 자로서 금융정보분석원장이 고시하 는 자 제외), 국가, 지방자치단체와의 현금의 지급 또는 영수는 제외한다.<개 정 2014.4.18., 2019.6.27., 2021.3.23.> - 1. 은행이 1거래일 동안 동일인에게 지급한 현금거
- `자금세탁방지업무 취급규정 원문-원본 / 제26조 / article` score=14.0 base=3 keywords=고액,현금거래,보고
  - features: article_type_bonus=1.0, deadline_term=1.0, report_title=2.0
  - 제26조 (고액 현금거래 보고) 보고책임자는 보고대상 고액 현금거래를 추출하여 동거래 발생후 30일 이내에 금융정보분석원장에게 보고하여야 한다.<개정 2025.5.22.> - 제26조의2(모니터링 체계 등) 은행은 자금세탁등을 예방하기 위하여 고객과의 금융거래 등에 대한 지속적인 모니터링체계를 수립하여 운영하여야 한다. [본조신설 2025.5.22.]
- `자금세탁방지업무 취급지침 원문-원본 / 제50조 / article` score=11.5 base=3 keywords=고액,현금거래,보고
  - features: article_type_bonus=1.0, deadline_term=1.0, report_title=1.0
  - 제50조 (보고대상) ① 다음 각 호의 경우에는 의심되는 거래 보고(STR)를 하여 야 한다.<개정 2013.11.12., 2021.3.23.> - 1. 금융거래등과 관련하여 수수한 재산이 불법재산이라고 의심되는 합당한 근거가 있거나, 금융거래등의 상대방이 자금세탁등의 행위를 하고 있다고 의심되는 합당한 근거가 있는 경우 - 2. 삭제<2013.11.12.> - 3. 고액 현금거래 보고를 회피할 목적으로 금액을 분할하여 현금거
- `자금세탁방지업무 취급지침 원문-원본 / ② / paragraph` score=10.5 base=4 keywords=고액,현금거래,보고,고액현금거래
  - features: subject_in_lead=1.0, subject_in_text=1, paragraph_type_bonus=1.0, deadline_term=1.0
  - ② 담당책임자와 보고책임자는 고액현금거래보고에서 오류가 발견된 경우 해당 오보고를 신속하게 수정 또는 취소한다. -

### 상위 법령 확장

- `internal:aml_guideline:article:제57조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `금융실명거래 및 비밀보장에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률` (method=compact_title, score=1.0)
- `internal:aml_guideline:article:제56조`
  - REFERS_TO_DOCUMENT `금융실명법` -> `금융실명거래 및 비밀보장에 관한 법률` (method=source_text_alias, score=1.0)
- `internal:aml_policy:article:제26조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령` (method=override_alias, score=1.0)
  - IMPLEMENTS_RESOLVED -> `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` (method=exact_title, score=1.0)
- `internal:aml_guideline:article:제50조`
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
- 의도: `role`
- 주체: `보고책임자 `
- 키워드: `보고책임자`

### 상위 내부규정 검색 결과

- `자금세탁방지업무 취급규정 원문-원본 / 제7조 / article` score=41.5 base=1 keywords=보고책임자
  - features: subject_in_title=1.0, subject_in_lead=1.0, subject_in_text=3, article_type_bonus=1.0, role_term_in_title=1.0, role_term_in_text=3.0, role_pattern_in_text=3.0, enumeration_pattern=1.0, negative_text=1.0
  - 제7조 (보고책임자) ① 보고책임자는 AML보고책임자로 하며, 타 업무를 겸임할 수 있다.<개정 2014.10.23., 2025.1.16.> - ② 보고책임자의 역할 및 책임은 다음 각 호와 같다.<개정 2014.10.23., 2019.6.27., 2025.5.22.> - 1. 의심되는 거래 및 고액 현금거래의 금융정보분석원장 앞 보고 - 2. 금융거래시 고객확인 이행관련 업무 총괄 - 3. 다음 각 목의 자금세탁방지등을 위한
- `자금세탁방지업무 취급지침 원문-원본 / 제7조 / article` score=21.5 base=1 keywords=보고책임자
  - features: subject_in_lead=1.0, subject_in_text=3, article_type_bonus=1.0, role_term_in_text=2.0, role_pattern_in_text=1.0
  - 제7조 (위험식별 및 내부통제) ① 보고책임자는 임직원이 관련된 금융사고 분석 등을 통해 임직원의 자금세탁 위험을 식별하고 분석한다.<개정 2025.5.22.> - ② 보고책임자는 제1항에서 확인한 자금세탁방지 취약점을 소관업무 부서장 에게 통보하고 이의 개선을 요구한다.<개정 2025.5.22.> - ③ 제2항의 개선요구를 접수한 소관업무 부서장은 업무절차, 시스템 개선 등 의 개선계획을 수립하고 그에 따른 조치결과를 보고책
- `자금세탁방지업무 취급지침 원문-원본 / 제12조 / article` score=21.5 base=1 keywords=보고책임자
  - features: subject_in_lead=1.0, subject_in_text=3, article_type_bonus=1.0, role_term_in_text=2.0, role_pattern_in_text=1.0
  - 제12조 (해외지점 등) ① 해외지점 등은 자금세탁방지등에 관한 국내·외 법규 를 준수하여야 하며, 보고책임자는 이의 이행 여부를 관리하여야 한다. 다만, 현지법규의 기준이 국내기준과 다른 경우 자금세탁위험을 관리·경감할 수 있는 조치를 취하고 그 사실을 보고책임자에게 보고하여야 한다.<개정 2014.10.2., 2019.6.27., 2025.5.22.> - ② 보고책임자는 국제자금세탁방지기구(이하 "FATF"이라 한다) 권고
- `자금세탁방지업무 취급규정 원문-원본 / 제5조 / article` score=20.5 base=1 keywords=보고책임자
  - features: subject_in_text=3, article_type_bonus=1.0, role_term_in_text=3.0, role_pattern_in_text=3.0, enumeration_pattern=1.0, wrong_subject_title=1.0, wrong_subject_lead=1.0
  - 제5조 (은행장) 자금세탁방지등 활동과 관련하여 은행장이 수행하여야 할 역할 및 책임은 다음 각 호와 같다.<개정 2019.6.27., 2025.5.22.> - 1. 자금세탁방지등을 위한 내부통제체계의 총괄적 구축·운영 - 2. 업무지침인 이 규정의 제정·개정·폐지 안건의 이사회 상정(법규 개정에 따른 용어변경, 자구수정 등 업무지침인 이 규정의 내용의 실질적인 변화 를 수반하지 않는 개정의 경우에는 은행장이 이를 승인할 수 
- `자금세탁방지업무 취급지침 원문-원본 / 제6조 / article` score=17.5 base=1 keywords=보고책임자
  - features: subject_in_lead=1.0, subject_in_text=3, article_type_bonus=1.0, role_term_in_text=1.0, enumeration_pattern=1.0
  - 제6조 (지속적인 직원확인) ① 보고책임자는 임직원 명부 등을 제공받아 다음 각 호와 같이 임직원이 외국의 정치적 주요인물이나 금융거래등제한대상자 등 요주의 인물인지 여부를 확인한다.<개정 2024.6.28., 2025.5.22., 2026.1.16.> - 1. 신규채용 임직원 : 매 신규채용 시 채용 전에 확인 - 2. 재직 임직원 : 전년말 현재 재직 임직원은 매년 1월중 확인 - ② 보고책임자는 임직원이 관련된 금융사고,

### 상위 법령 확장

- `internal:aml_policy:article:제7조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령` (method=override_alias, score=1.0)
  - IMPLEMENTS_RESOLVED -> `자금세탁방지 및 공중협박자금조달금지에 관한 업무규정` (method=exact_title, score=1.0)
- `internal:aml_guideline:article:제7조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `금융실명거래 및 비밀보장에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률` (method=compact_title, score=1.0)
- `internal:aml_guideline:article:제12조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `금융실명거래 및 비밀보장에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률` (method=compact_title, score=1.0)
- `internal:aml_policy:article:제5조`
  - REFERS_TO_DOCUMENT `특정금융정보법` -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=source_text_alias, score=1.0)
  - REFERS_TO_DOCUMENT `특정금융정보법 시행령` -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령` (method=override_alias, score=1.0)
  - REFERS_TO_DOCUMENT `금융회사의 지 배구조에 관한 법률 시행령` -> `금융회사의 지배구조에 관한 법률 시행령` (method=compact_title, score=1.0)
- `internal:aml_guideline:article:제6조`
  - IMPLEMENTS_RESOLVED -> `특정 금융거래정보의 보고 및 이용 등에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `금융실명거래 및 비밀보장에 관한 법률` (method=compact_title, score=1.0)
  - IMPLEMENTS_RESOLVED -> `공중 등 협박목적 및 대량살상무기확산을 위한 자금조달행위의 금지에 관한 법률` (method=compact_title, score=1.0)

### 관찰된 문제

- 뚜렷한 문제 없음
