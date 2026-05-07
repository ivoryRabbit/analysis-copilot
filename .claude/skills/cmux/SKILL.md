# cmux SKILL — AI 에이전트 가이드

## 계층 구조
Window > Workspace(사이드바 탭) > Pane(분할 영역) > Surface(터미널/브라우저)

## 자동 환경변수
- `CMUX_WORKSPACE_ID` (현재 워크스페이스)
- `CMUX_SURFACE_ID` (현재 서피스)
- `--workspace` / `--surface` 생략 가능 (현재 컨텍스트 자동 사용)

## 핵심 명령어

### 탐색
```bash
cmux identify          # 현재 컨텍스트 (JSON)
cmux tree [--all]      # 전체 계층 구조
```

### 캡처 (AI 핵심)
```bash
cmux read-screen                              # 현재 출력
cmux read-screen --surface surface:2 --lines 30
cmux capture-pane --surface surface:2
```

### 전송
```bash
cmux send "npm run dev\n"
cmux send --surface surface:2 "test\n"
cmux send-key ctrl+c
```

### 분할
```bash
cmux new-split right
cmux new-split down
cmux new-workspace [--cwd /path]
cmux rename-workspace "이름"
```

### 브라우저
```bash
cmux browser snapshot -i                     # DOM 스냅샷
cmux browser click "button" --snapshot-after
cmux browser wait --text "Welcome" --timeout-ms 5000
cmux browser screenshot --out ./shot.png
```

## 주의
- cmux 명령어는 항상 `cmux <subcommand>` 형식 — tmux 명령어(`tmux split-window` 등)와 다르므로 혼용 금지
- SSH/CI 환경에서는 cmux를 사용할 수 없음
- `CMUX_WORKSPACE_ID` 없으면 cmux 터미널 밖에서 실행 중인 것
