# /dashboard — HTML 대시보드 생성

DuckDB scratch에 저장된 데이터를 읽고, 분석가가 원하는 레이아웃·스타일을 자연어로 받아
Claude가 HTML 파일을 직접 생성한다. 매번 분석가의 요청에 맞는 맞춤형 대시보드가 만들어진다.

## 사용법

```
/dashboard
/dashboard --title "월간 분석 리포트"
```

---

## 실행 절차

### Step 1. scratch 테이블 목록 확인

```bash
venv/bin/python3 scripts/save_result.py --list
```

저장된 테이블이 없으면 `/analyze` → `/save`를 먼저 실행하도록 안내하고 종료한다.

---

### Step 2. 포함할 테이블과 데이터 확인

사용자에게 묻는다:
> 어떤 테이블을 대시보드에 포함할까요? (전체 또는 특정 테이블 선택)

선택한 테이블의 데이터를 읽는다:

```bash
venv/bin/python3 scripts/dashboard.py --table <table_name>
```

각 테이블의 컬럼명·타입·샘플 데이터를 파악해둔다.

---

### Step 3. 레이아웃·스타일 요청

사용자에게 묻는다:
> 어떤 차트 구성과 스타일을 원하시나요?
> (예: "2열 바차트", "다크 테마 파이차트", "깔끔한 라인차트 + 요약 수치")
>
> 자유롭게 말씀해 주세요. 예시:
> - "장르별 평점은 가로 바차트, 성별 비율은 도넛 차트로, 다크 테마"
> - "한 화면에 3개 차트, 밝은 색으로, 제목 크게"
> - "데이터 테이블도 같이 보여줘"

---

### Step 4. HTML 생성

사용자 요청을 반영해 HTML 파일을 직접 작성한다.

**반드시 지켜야 할 규칙:**
- Plotly.js는 CDN(`https://cdn.plot.ly/plotly-2.27.0.min.js`)으로 로드
- 데이터는 JS 변수로 HTML 안에 인라인 삽입 (외부 API 호출 없음)
- 단일 `.html` 파일로 완결 (CSS·JS 모두 인라인)
- 파일 저장 경로: `/tmp/dashboard_<YYYYMMDD_HHMMSS>.html`

**기본 품질 기준** (사용자가 별도 요청하지 않은 경우):
- 반응형 레이아웃 (CSS grid 또는 flexbox)
- 헤더에 대시보드 제목 + 생성 시각
- 각 차트에 제목, 소스 테이블명 표시
- 호버 시 값 표시
- 깔끔한 타이포그래피

Write 도구로 파일을 작성한다.

---

### Step 5. 브라우저에서 열기

```bash
open /tmp/dashboard_<YYYYMMDD_HHMMSS>.html
```

파일 경로를 사용자에게 알려준다.
수정 요청이 있으면 HTML을 직접 수정해 다시 저장·오픈한다.
