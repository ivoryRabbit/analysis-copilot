# cmux 설정 가이드

analytics-copilot에서 **cmux**를 사용하면 Claude Code 대화창, 터미널, 차트 브라우저를 한 화면에 배치해 분석 흐름을 끊김 없이 이어갈 수 있습니다.

---

## cmux란?

cmux는 Claude Code와 통합된 터미널 멀티플렉서입니다.
터미널 분할, 브라우저 내장, AI 에이전트 간 화면 공유를 지원합니다.

**계층 구조**

```
Window
└── Workspace (사이드바 탭)
    └── Pane (분할 영역)
        └── Surface (터미널 or 브라우저)
```

---

## 설치

macOS 전용 앱입니다.

1. [cmux 공식 사이트](https://cmux.app)에서 다운로드
2. `/Applications/cmux.app` 설치
3. 터미널에서 확인:

```bash
cmux --version
```

---

## 권장 레이아웃

analytics-copilot에 최적화된 3-패널 구성입니다.

```
┌──────────────────────┬───────────────────────┐
│                      │                       │
│   Claude Code        │   터미널              │
│   (대화 · 분석)      │   (Trino · 명령 실행) │
│                      │                       │
│                      ├───────────────────────┤
│                      │                       │
│                      │   차트 브라우저       │
│                      │   (/chart 결과)       │
└──────────────────────┴───────────────────────┘
```

### 레이아웃 설정 명령어

cmux 터미널 안에서 실행합니다:

```bash
# 오른쪽에 터미널 패널 추가
cmux new-split right

# 오른쪽 하단에 브라우저 패널 추가
cmux new-split down
```

또는 `/setup` 스킬을 실행하면 자동으로 구성됩니다:

```
/setup
```

---

## 핵심 명령어

### 현재 상태 확인

```bash
cmux identify        # 현재 workspace · surface 정보
cmux tree --all      # 전체 레이아웃 트리
```

### 패널 간 명령 전송

```bash
# surface:2 터미널에 명령 전송
cmux send --surface surface:2 "docker-compose up -d\n"

# 현재 패널에 전송
cmux send "python scripts/setup_data.py\n"
```

### 화면 읽기

```bash
# 특정 패널 출력 확인
cmux read-screen --surface surface:2 --lines 20
```

### 브라우저 패널

```bash
# 차트 HTML 스냅샷
cmux browser snapshot -i

# 특정 텍스트가 나타날 때까지 대기
cmux browser wait --text "완료" --timeout-ms 5000
```

---

## analytics-copilot 세션 시작 흐름

```bash
# 1. cmux에서 프로젝트 열기
cmux new-workspace --cwd ~/Side/analytics-copilot

# 2. Claude Code 실행 (surface:1)
claude

# 3. 레이아웃 구성 + 환경 초기화
/setup

# 4. 분석 시작
/analyze 장르별 평균 평점 보여줘

# 5. 차트 생성 → 브라우저 패널에 자동 표시
/chart bar
```

---

## 패널별 역할 정리

| Surface | 역할 | 실행 내용 |
|---------|------|-----------|
| surface:1 | Claude Code 대화 | `/analyze`, `/chart`, `/save` |
| surface:2 | 터미널 | `docker-compose`, `python scripts/` |
| surface:3+ | 브라우저 | Plotly 차트 HTML |

---

## 참고

- cmux는 `CMUX_WORKSPACE_ID`, `CMUX_SURFACE_ID` 환경변수를 자동 주입합니다.
- SSH·CI 환경에서는 cmux를 사용할 수 없습니다. 폴백으로 tmux를 사용하세요:

```bash
command -v cmux >/dev/null && cmux new-split right || tmux split-window -h
```
