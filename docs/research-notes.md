# 제거된 기능 및 미구현 항목

## graphify

- **상태**: 미도입 (이 레포에 코드 없음 — mini-data-catalog에서 자료조사만 완료)
- **확인일**: 2026-05-08

### 개요

Claude Code용 커뮤니티 오픈소스 지식 그래프 도구. Anthropic 공식 기능 아님.

- 코드베이스를 Tree-sitter 정적 분석 + LLM으로 **쿼리 가능한 지식 그래프**로 변환
- Claude가 파일을 직접 읽기 전에 그래프를 먼저 참조 → **토큰 49~70배 절감** (500개+ 파일 기준)
- `/graphify` 명령어로 설치, `CLAUDE.md`와 PreToolUse 훅 자동 설정
- 산출물: `graph.html`(인터랙티브 탐색), `GRAPH_REPORT.md`, `graph.json`
- 설치: `pip install "graphifyy[mcp]"` → Claude Code에서 `/graphify` 입력

### 이 레포에 도입하지 않은 이유

핵심 파일이 10개 내외(scripts/, catalog/, .claude/skills/)라 500개+ 파일 기준의 토큰 절감 효과가 미미함.
대신 graphify 개념을 `schema.yaml`의 `relationships` 섹션으로 응용 — `/analyze` 스킬이 이 관계 그래프를 보고 JOIN 경로를 자동 추론하는 방식으로 이미 구현됨.

### 재검토 조건

테이블 수가 대폭 늘어나거나 스키마가 복잡해질 경우 도입 고려.
