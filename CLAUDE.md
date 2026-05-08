# analytics-copilot

데이터 분석가가 자연어로 질문하면 SQL 생성 → 실행 → 차트까지 대화형으로 처리하는 로컬 분석 환경.
API 서버 없이 **Trino + DuckDB + GitHub 온톨로지 repo(git submodule)**로 동작한다.

---

## 빠른 시작 (처음 한 번만)

```bash
# 1. 레포 클론 (온톨로지 submodule 포함)
git clone --recurse-submodules <repo-url>

# 2. 의존성 설치
pip install -r requirements.txt

# 3. Trino 컨테이너 실행
docker-compose up -d

# 4. 샘플 데이터 로드 (Trino 기동 후 ~30초 대기)
python scripts/setup_data.py

# 5. 카탈로그 동기화 (온톨로지 submodule 미등록 시 URL 입력 안내)
/sync
```

이후부터는 `/analyze`로 바로 분석 시작.

---

## 분석 세션 시작 (매번)

Trino memory connector는 재시작 시 초기화되므로 컨테이너 재시작 후에는 아래를 실행:

```bash
python scripts/setup_data.py   # 샘플 데이터 재로드
```

DuckDB scratch는 재시작해도 데이터가 유지된다 (`scratch/scratch.duckdb`).

---

## 스킬 사용법

| 스킬 | 설명 | 예시 |
|------|------|------|
| `/schema` | 테이블·컬럼·관계 탐색 | `/schema ratings` |
| `/sync` | Trino 스키마 → 온톨로지 repo 동기화 | `/sync` |
| `/analyze <질문>` | 자연어 → SQL → 결과 | `/analyze 장르별 평균 평점` |
| `/save <name>` | 마지막 결과를 DuckDB에 저장 | `/save genre_ratings` |
| `/chart <타입>` | 마지막 결과를 단일 차트로 시각화 | `/chart bar` `/chart pie` |
| `/dashboard` | 저장된 결과 여러 개를 HTML 대시보드로 | `/dashboard --title "월간 리포트"` |

### 전형적인 분석 흐름

```
/analyze 장르별 평균 평점            # Trino에서 원천 쿼리
/save genre_ratings                  # DuckDB scratch에 저장
/analyze scratch.genre_ratings에서
         평점 3.2 이상만 필터        # DuckDB에서 빠르게 후속 분석
/chart bar                           # 결과 시각화
```

---

## 엔진 라우팅

`run_query.py`가 SQL을 보고 자동으로 엔진을 선택한다.

| SQL 조건 | 엔진 |
|----------|------|
| `scratch.*` 테이블 참조 | DuckDB (로컬 scratch) |
| `memory.default.*` 또는 Trino 카탈로그 | Trino |
| `read_json_auto(...)` 포함 | DuckDB |

DuckDB에서 마지막 결과를 바로 쿼리하는 방법:
```sql
SELECT * FROM read_json_auto('/tmp/last_result.json') WHERE avg_rating > 3.2
```

---

## 아키텍처

```
catalog/
  ontology_config.yaml  # 온톨로지 repo URL·경로 설정
  ontology/             # 온톨로지 repo (git submodule, .gitmodules 참조)
    schema.yaml         # 테이블·컬럼 메타데이터 + 관계(FK) 정의
scratch/
  scratch.duckdb        # 중간 결과 저장소 (영속, git 제외)
scripts/
  setup_data.py         # Trino memory에 샘플 데이터 로드
  run_query.py          # SQL 실행 — Trino/DuckDB 자동 라우팅
  save_result.py        # 마지막 결과 → DuckDB named 테이블
  chart.py              # Plotly 차트 생성 → 브라우저 오픈
  sync_catalog.py       # Trino information_schema → 온톨로지 schema.yaml 동기화
trino/
  catalog/
    memory.properties   # Trino memory connector 설정
.claude/skills/
  analyze/              # /analyze    — 자연어 분석 진입점
  chart/                # /chart      — 단일 차트 시각화
  dashboard/            # /dashboard  — 멀티 차트 HTML 대시보드
  save/                 # /save       — DuckDB scratch 저장
  schema/               # /schema     — 스키마 탐색
  sync/                 # /sync       — 카탈로그 동기화
docker-compose.yaml     # Trino 컨테이너
```

---

## 기술 스택

| 레이어 | 기술 | 역할 |
|--------|------|------|
| 원천 쿼리 | Trino (memory connector) | 회사 데이터 소스 대체 |
| 중간 결과 | DuckDB | 빠른 로컬 후속 분석 |
| 온톨로지 | 별도 GitHub repo (`catalog/ontology/`) | JOIN 경로·컬럼 설명 (버전 관리) |
| 차트 | Plotly → HTML | 브라우저 인터랙티브 차트 |
| AI 인터페이스 | Claude Code 스킬 | 자연어 → SQL 변환 |
| 터미널 UX | cmux | 멀티패널 레이아웃 |

---

## schema.yaml 구조

테이블·컬럼 메타데이터 외에 `relationships` 섹션을 포함한다.
`/analyze` 스킬이 이 관계 그래프를 보고 JOIN 경로를 자동 추론한다.

```yaml
catalogs:
  memory:
    schemas:
      default:
        relationships:
          - name: ratings_to_users
            from: ratings.user_id
            to: users.id
            join: "ratings r JOIN users u ON r.user_id = u.id"
          - name: ratings_to_movies
            from: ratings.movie_id
            to: movies.id
            join: "ratings r JOIN movies m ON r.movie_id = m.id"
          - name: ratings_to_users_movies
            from: [ratings.user_id, ratings.movie_id]
            to: [users.id, movies.id]
            join: "ratings r JOIN users u ON r.user_id = u.id JOIN movies m ON r.movie_id = m.id"
        tables:
          movies:
            description: ...
            columns: [...]
```

새 테이블 추가 시 `tables`와 `relationships` 모두 업데이트하고 `/sync` 실행.

---

## 온톨로지 repo 설정

온톨로지 repo는 git submodule로 관리된다. 팀 전체가 동일한 URL을 공유하며, `.gitmodules`에 한 번 커밋하면 이후 신규 분석가는 아래 한 줄로 환경이 완성된다:

```bash
git clone --recurse-submodules <analytics-copilot-url>
```

처음 submodule을 등록할 때는 `/sync`를 실행하면 URL을 물어보고 자동으로 설정한다.

### 온톨로지 변경 워크플로 (권한 구분)

| 역할 | 권한 | 행동 |
|------|------|------|
| 분석가 | push (브랜치) | `/sync` 실행 → `sync/YYYYMMDD` 브랜치 push → PR 생성 |
| 온톨로지 담당자 | main 머지 | PR 리뷰 후 머지 |

분석가는 온톨로지 repo의 main 브랜치에 직접 push하지 않는다.
PR 머지 후 analytics-copilot의 submodule 참조를 `git submodule update --remote`로 갱신한다.

---

## Trino 환경 전환

로컬 샘플(memory connector) 대신 다른 Trino 환경으로 전환하는 방법:

1. `scripts/run_query.py`의 `host`/`port`를 대상 Trino 엔드포인트로 변경
2. 온톨로지 repo를 해당 환경 것으로 교체 (`git submodule set-url catalog/ontology <new-url>`) 후 `/sync`
3. DuckDB scratch는 환경에 무관하게 그대로 사용 가능

---

## 실행 환경

이 프로젝트는 `venv/`에 Python 가상환경을 사용한다.
**모든 `python` 명령은 `venv/bin/python3`로 실행한다.**

```bash
venv/bin/python3 scripts/run_query.py "<SQL>"
venv/bin/python3 scripts/setup_data.py
```

venv가 없으면 `/setup`을 먼저 실행한다.

---

## 코드 컨벤션

- Python 타입 힌트 사용
- 스크립트는 단독 실행 가능하도록 `if __name__ == "__main__"` 포함
- `scratch/scratch.duckdb`는 `.gitignore`에 추가 권장

---

## 변경 이력

### 2026-05-09 — 온톨로지 repo 분리 및 대시보드 스킬 추가

**온톨로지 repo 분리 (git submodule)**
- `catalog/schema.yaml` 제거 — 온톨로지를 별도 GitHub repo로 분리
- `catalog/ontology_config.yaml` 추가 — `local_path`, `schema_file`, `github_repo`, `trino_catalog`, `trino_schema` 설정
- `catalog/ontology/` (git submodule) 위치에 온톨로지 repo 클론
- 신규 분석가 온보딩: `git clone --recurse-submodules <repo-url>` 한 줄로 완료

**`/sync` 스킬 개선**
- submodule 미등록 시 URL과 GitHub repo 슬러그를 사용자에게 입력 받아 자동 설정
- `sync/YYYYMMDD` 브랜치에 커밋 후 `gh pr create`로 PR 생성 (직접 push 금지)
- PR 머지 후 analytics-copilot의 submodule 참조 갱신 안내

**온톨로지 변경 권한 구분**
- 분석가: 브랜치 push + PR 생성 가능
- 온톨로지 담당자: main 머지 권한

**`sync_catalog.py` 개선**
- `catalog/schema.yaml` 폴백 제거 — submodule 미설정 시 명확한 오류 메시지 출력
- `--catalog`/`--schema` 미지정 시 `ontology_config.yaml`의 `trino_catalog`/`trino_schema` 자동 참조
- `--print-schema-path` 옵션 추가 — 다른 스킬이 schema 경로를 동적으로 참조할 때 사용

**`/analyze`, `/schema` 스킬 개선**
- `cat catalog/schema.yaml` 하드코딩 → `cat $(python scripts/sync_catalog.py --print-schema-path)` 으로 교체
- SQL 테이블 경로를 `memory.default.*` 고정에서 `ontology_config.yaml`의 `trino_catalog`/`trino_schema` 동적 참조로 변경

**`/setup` 스킬 개선**
- venv 생성·패키지 설치 단계 추가 (최초 1회)
- 이후 실행 시 `pip install -r requirements.txt --quiet`로 최신화만 수행

**`/dashboard` 스킬 전면 개편**
- 고정 Python 템플릿 방식 제거
- Claude가 자연어 요청을 받아 HTML을 직접 생성하는 방식으로 변경
- `scripts/dashboard.py`는 scratch 테이블 데이터를 JSON으로 출력하는 유틸로 단순화
- 분석가별로 완전히 다른 레이아웃·스타일의 대시보드 생성 가능
