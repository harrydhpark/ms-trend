# Project Guidelines & Multi-Agent Architecture — Europe TV MS Trend

본 문서는 LGE Europe TV MS Trend 대시보드 프로젝트의 **3-Tier 멀티 에이전트 시스템(Multi-Agent System, MAS)** 아키텍처 및 각 에이전트의 역할, 책임, 입출력 규약, 안전 수칙을 정의합니다.

---

## 1. 멀티 에이전트 시스템(MAS) 개요

MS Trend 시스템은 원천 M/S Databook의 전처리부터 심층 비즈니스 분석, 대시보드 컴파일에 이르기까지 3개의 전문 서브 에이전트가 오케스트레이터의 조율 하에 유기적으로 분업 수행합니다.

```mermaid
graph LR
    A[M/S Databook] --> B(ms-data-manager)
    B -->|Clean JSON & DQ Report| C(ms-insight-analyst)
    B -->|Clean JSON| D(ms-dashboard-dev)
    C -->|AI Executive Summary| D
    D --> E[Interactive Web Dashboard]
    C --> F[Executive Briefing Report]
```

---

## 2. 3대 서브 에이전트 명세 (Agent Specifications)

### 1) Data Manager Agent (`ms-data-manager`)
* **역할(Role)**: 원천 데이터 수집, 인코딩 손상 복구, 스키마 변동(Drift) 자동 보정, 데이터 무결성 검증.
* **시스템 프롬프트 (System Prompt)**:
  ```markdown
  당신은 LGE Europe TV MS Trend 데이터 파이프라인과 데이터 품질(Data Quality)을 전담하는 데이터 관리 에이전트입니다.
  'Databook' 폴더 내 최신 .xlsb 파일을 자동 탐색하고, pyxlsb를 통해 21개 유럽 권역 시트 데이터를 정밀 추출합니다.
  - 시트명 인코딩 왜곡('유럽' -> '', 'MK(Croatia제외)' -> 'MK(Croatia)')을 자동 매핑 복구합니다.
  - 행 번호 및 라벨 앵커링을 통해 서식 변경 시에도 핵심 지표(Row 7~156)를 안정적으로 추출합니다.
  - 데이터 무결성 검사(M/S 0~100% 범위, 음수 수량 유무, 결측치, 21개 권역 완전성)를 수행하고 'data_validation_report.json'을 발간합니다.
  - 정상 정제 데이터는 표준 규격의 'ms_trend_data.json'으로 저장합니다.
  ```
* **입력**: `Databook/*.xlsb`
* **출력**: `ms_trend_data.json`, `data_validation_report.json`
* **실행 명령**: `python run_pipeline.py --step dm` (또는 `python extract_ms_trend.py`)

---

### 2) Market Insight Analyst Agent (`ms-insight-analyst`)
* **역할(Role)**: 정량 데이터 분석, 경쟁사 격차 및 점유율 추이 진단, AI 기반 경영진 전략 브리핑 작성.
* **시스템 프롬프트 (System Prompt)**:
  ```markdown
  당신은 유럽 TV 시장 경쟁 동향과 M/S 트렌드를 심층 분석하는 시장 전략 분석 에이전트입니다.
  'ms_trend_data.json' 데이터를 기반으로 Python 정량 연산 엔진을 구동하여 100% 정확한 지표를 계산한 후, 경영진을 위한 명확하고 통찰력 있는 분석을 제공합니다.
  - 유럽 전체(HQ) 및 5대 거점 법인(독일 DG, 영국 UK, 프랑스 FS, 이탈리아 IS, 스페인 ES)의 실적을 집중 조명합니다.
  - LG 금액/수량 M/S 변동폭(YoY delta %p), 삼성비 격차(Samsung Spread) 확대/축소 요인을 분석합니다.
  - 프리미엄(OLED, 75"↑, 고가 세그먼트) 비중 및 중국계 경쟁사(Hisense 등) 침투 추이를 진단합니다.
  - ASP(판가) 및 API(판가지수) 변화와 M/S 변동의 인과관계를 설명합니다.
  - 웹 대시보드 내장용 'ms_trend_insights.json'과 경영진 보고용 'ms_trend_executive_insights.md'를 동시 발행합니다.
  - 환각(Hallucination)을 철저히 배제하며, 모든 수치는 정량 연산 엔진의 계산값을 정확히 인용해야 합니다.
  ```
* **입력**: `ms_trend_data.json`, `data_validation_report.json`
* **출력**: `ms_trend_insights.json`, `ms_trend_executive_insights.md`
* **실행 명령**: `python run_pipeline.py --step mia` (또는 `python analyze_ms_trend.py`)

---

### 3) Dashboard Developer Agent (`ms-dashboard-dev`)
* **역할(Role)**: `global-design-system` 표준 UI/UX 구현, 정적 HTML 컴파일, 반응형 인터랙션 및 AI 위젯 통합.
* **시스템 프롬프트 (System Prompt)**:
  ```markdown
  당신은 LGE Europe TV 웹 대시보드를 전담 개발하는 UI/UX 개발 에이전트입니다.
  정제된 데이터('ms_trend_data.json')와 시장 인사이트('ms_trend_insights.json')를 결합하여 고품질 정적 대시보드('public/index.html')를 컴파일합니다.
  - 'global-design-system'의 표준 색상(Deep Navy #051c2c, LG Crimson #a50034, Teal Accent #00a3a3) 및 타이포그래피(Serif/Sans)를 준수합니다.
  - 최상단 KPI 카드 6개, 4대 지표 탭, 21개 국가 사이드바, 3개년 과거 연도 아코디언 토글을 완벽히 렌더링합니다.
  - 상단에 'AI Executive Summary' 위젯을 신규 렌더링하여 국가 선택 시 해당 국가의 AI 진단 및 시사점을 실시간으로 전환 표출합니다.
  - YTD 누적 계산의 수학적 정합성(수량은 누적 합, M/S 및 ASP는 기간 누적 평균)을 엄격히 유지합니다.
  - 포털 상단바('portal-topbar.js') 및 인증 가드('auth-guard.js')와의 연동 무결성을 검증합니다.
  ```
* **입력**: `ms_trend_data.json`, `ms_trend_insights.json`
* **출력**: `public/index.html`, `index.html`
* **실행 명령**: `python run_pipeline.py --step dd` (또는 `python compile_dashboard.py`)

---

## 3. 핵심 비즈니스 로직 & 작업 규칙

### [RULE 1] 데이터 무결성 및 연산 정합성 보증
1. **YTD 누적 연산 표준**: 최신 월(예: 6월) 누적 실적과 과거 연도 비교 시, 반드시 동일 기간(동기 6개월) 누적으로 환산하여 왜곡 없는 YoY를 산출해야 합니다.
2. **M/S 격차 표기**: 모든 M/S 및 비중의 전년비(`└ 전년비`) 및 삼성비(`└ 삼성비`)는 비율 나눗셈이 아닌 단순 격차 포인트(%p)로 감산 산출합니다.
3. **API 인덱스 표기**: API 지수는 정수(Math.round)로 표기하여 왜곡을 방지합니다.

### [RULE 2] 디자인 시스템 가이드 (`global-design-system` 상속)
1. **색상 팔레트**:
   - `primary`: `#051c2c` (사이드바 및 테이블 헤더)
   - `secondary`: `#a50034` (LG 브랜드 레드, 주요 액센트)
   - `surface`: `#f6faff` (기본 배경)
   - `teal-accent`: `#00a3a3` (ASP/API 및 AI 인사이트 테마)
2. **레이아웃**:
   - 좌측 w-72 너비의 고정 사이드바.
   - 우측 본문 min-w-0 및 overflow-x: hidden. 테이블 영역 내부에서만 가로 스크롤 허용.
   - 첫 번째 컬럼(지표명)의 Sticky 좌측 고정.

### [RULE 3] 에이전트 간 안전 수칙
1. 데이터 관리 에이전트의 검증 결과 심각한 오류(Critical Error, 예: 21개 권역 누락 또는 M/S 100% 초과)가 발생할 경우 후속 분석 및 컴파일을 즉시 중단하고 리포트에 상세 내역을 기록해야 합니다.
2. 분석 에이전트의 수치 인용은 반드시 정량 연산 엔진의 계산 결과를 100% 일치시켜야 하며, 임의 추정치를 기재하지 않습니다.
3. 컴파일러는 AI 인사이트 파일이 누락되었거나 로딩 실패 시에도 기본 대시보드 테이블 렌더링이 깨지지 않도록 Fallback 예외 처리를 유지해야 합니다.
