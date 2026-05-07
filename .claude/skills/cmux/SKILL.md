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

## tmux → cmux 변환

| tmux | cmux |
|------|------|
| `tmux split-window -v` | `cmux new-split down` |
| `tmux send-keys -t %1 "cmd" C-m` | `cmux send --surface surface:1 "cmd\n"` |
| `tmux capture-pane -t %1 -p` | `cmux capture-pane --surface surface:1` |

## 주의
- SSH/CI에서 cmux 불가 → `command -v cmux >/dev/null || tmux ...` 폴백
- `CMUX_WORKSPACE_ID` 없으면 cmux 터미널 밖에서 실행 중인 것
