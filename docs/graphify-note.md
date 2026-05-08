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

**적용 대상: `catalog/ontology/` 디렉토리만**

```bash
# 올바른 사용법
graphify .   # ❌ 코드베이스 전체 — 의미 없음
graphify catalog/ontology   # ✅ 온톨로지만
```

코드 파일 수가 적어 코드베이스 전체에 적용하면 토큰 절감 효과가 없다.
대신 `catalog/ontology/schema.yaml`의 테이블·컬럼·FK 관계·비즈니스 컨텍스트를
지식 그래프로 시각화해 탐색하는 용도로 쓴다.

### 실행 전 체크리스트

1. Trino 기동 및 데이터 로드 확인
   ```bash
   docker compose up -d
   venv/bin/python3 scripts/setup_data.py   # 샘플 데이터
   ```
2. schema.yaml 최신화
   ```bash
   python3 scripts/sync_catalog.py   # Trino → schema.yaml 동기화
   ```
3. description 필드 채우기 (비어있으면 graphify 품질 저하)
4. graphify 실행
   ```bash
   graphify catalog/ontology
   # 또는 /graphify catalog/ontology
   ```

### 출력물 위치

```
graphify-out/
  graph.html       — 브라우저 인터랙티브 탐색
  GRAPH_REPORT.md  — God Nodes, Surprising Connections, Suggested Questions
  graph.json       — 쿼리용 원본 데이터
```

테이블·FK 관계가 늘어날수록, description이 풍부할수록 유용해진다.
