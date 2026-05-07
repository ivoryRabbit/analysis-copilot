# graphify

Claude Code용 커뮤니티 오픈소스 지식 그래프 도구. Anthropic 공식 기능 아님.

## 무엇을 하는가

코드베이스 전체를 Tree-sitter 정적 분석 + LLM 의미 추출로 **쿼리 가능한 지식 그래프**로 변환한다.
Claude가 파일을 직접 읽기 전에 이 그래프를 먼저 참조해 관련 컨텍스트를 빠르게 찾는다.

- 토큰 사용량 49~70배 절감 (500개+ 파일 기준)
- 산출물: `graph.html`(브라우저 인터랙티브 탐색), `GRAPH_REPORT.md`(주요 개념 요약), `graph.json`(쿼리용 데이터)

## 설치 및 사용법

```bash
pip install "graphifyy[mcp]"
```

이후 Claude Code 세션에서:

```
/graphify
```

대화형으로 설정이 진행되며, `CLAUDE.md`와 PreToolUse 훅이 자동으로 구성된다.
설정 완료 후 Claude는 파일 검색 전에 지식 그래프를 우선 참조한다.

### MCP 서버로 실행

```bash
graphifyy --mcp
```

## 이 레포에서 쓴다면

코드 파일 수가 적어 토큰 절감 효과는 작다.
대신 `schema.yaml`의 테이블 관계를 graphify로 시각화해 `graph.html`로 탐색하는 용도로 활용할 수 있다.
테이블·FK 관계가 늘어날수록 유용해진다.
