# mini-data-catalog

데이터 분석가가 자연어로 질문하면 SQL 생성 → 실행 → 차트까지 대화형으로 처리하는 로컬 분석 환경.
API 서버 없이 **Trino + DuckDB + 로컬 YAML 온톨로지**로 동작한다.

---

## 빠른 시작 (처음 한 번만)

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. Trino 컨테이너 실행
docker-compose up -d

# 3. 샘플 데이터 로드 (Trino 기동 후 ~30초 대기)
python scripts/setup_data.py

# 4. 카탈로그 동기화
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
| `/sync` | Trino 스키마 → schema.yaml 동기화 | `/sync` |
| `/analyze <질문>` | 자연어 → SQL → 결과 | `/analyze 장르별 평균 평점` |
| `/save <name>` | 마지막 결과를 DuckDB에 저장 | `/save genre_ratings` |
| `/chart <타입>` | 마지막 결과를 차트로 시각화 | `/chart bar` `/chart pie` |

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
  schema.yaml         # 테이블·컬럼 메타데이터 + 관계(FK) 정의
scratch/
  scratch.duckdb      # 중간 결과 저장소 (영속, git 제외)
scripts/
  setup_data.py       # Trino memory에 샘플 데이터 로드
  run_query.py        # SQL 실행 — Trino/DuckDB 자동 라우팅
  save_result.py      # 마지막 결과 → DuckDB named 테이블
  chart.py            # Plotly 차트 생성 → 브라우저 오픈
  sync_catalog.py     # Trino information_schema → schema.yaml 동기화
trino/
  catalog/
    memory.properties # Trino memory connector 설정
.claude/skills/
  analyze/            # /analyze — 자연어 분석 진입점
  chart/              # /chart   — 차트 시각화
  save/               # /save    — DuckDB scratch 저장
  schema/             # /schema  — 스키마 탐색
  sync/               # /sync    — 카탈로그 동기화
docker-compose.yaml   # Trino 컨테이너
```

---

## 기술 스택

| 레이어 | 기술 | 역할 |
|--------|------|------|
| 원천 쿼리 | Trino (memory connector) | 회사 데이터 소스 대체 |
| 중간 결과 | DuckDB | 빠른 로컬 후속 분석 |
| 온톨로지 | `catalog/schema.yaml` | JOIN 경로·컬럼 설명 |
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

## 회사 Trino 전환

1. `scripts/run_query.py`의 `host`/`port`를 실제 Trino 엔드포인트로 변경
2. `catalog/schema.yaml`을 실제 스키마 + 관계 정의로 교체 (또는 `/sync`로 자동 생성)
3. DuckDB scratch는 그대로 사용 가능

---

## 코드 컨벤션

- Python 타입 힌트 사용
- 스크립트는 단독 실행 가능하도록 `if __name__ == "__main__"` 포함
- `scratch/scratch.duckdb`는 `.gitignore`에 추가 권장
