# /analyze — 자연어 데이터 분석

자연어 질문을 SQL로 변환하고, 실행 결과를 표시한다.
Trino(원천 데이터)와 DuckDB(중간 결과 scratch)를 자동으로 라우팅한다.
결과는 `/tmp/last_result.json`에 저장되어 `/chart`, `/save`에서 재사용된다.

## 사용법

```
/analyze <질문>
```

예시:
- `/analyze 장르별 평균 평점 보여줘`
- `/analyze 평점 4.5 이상 영화 목록`
- `/analyze 성별에 따른 평균 평점 차이`
- `/analyze 연도별 개봉 영화 수 추이`

## 실행 절차

### Step 1. 스키마 + 관계 그래프 파악

```bash
cat catalog/schema.yaml
```

`relationships` 섹션에서 테이블 간 FK 관계와 미리 정의된 JOIN 스니펫을 확인한다.

**JOIN 경로 추론 규칙**:
- 질문에 **한 테이블**만 필요 → 단순 SELECT
- 질문에 **두 테이블** 필요 → `relationships`에서 해당 쌍의 `join` 스니펫 사용
- 질문에 **세 테이블** 필요 → `from` 배열이 2개인 관계(`ratings_to_users_movies`)의 `join` 스니펫 사용
- `relationships`에 없는 경로 → 컬럼명으로 직접 추론 후 JOIN

예시 매핑:
| 필요 테이블 | 사용할 relationship |
|-------------|---------------------|
| ratings + users | ratings_to_users |
| ratings + movies | ratings_to_movies |
| ratings + users + movies | ratings_to_users_movies |

### Step 2. SQL 생성 규칙

- 테이블 전체 경로: `memory.default.<table>`
- `relationships[*].join` 스니펫의 alias(`r`, `u`, `m`)를 그대로 사용
- Trino ANSI SQL 사용
- 유용한 Trino 함수: `date_trunc`, `approx_distinct`, `array_join(array_agg(...), ', ')`
- LIMIT는 기본 100 (분석가가 명시하지 않으면)

예시 (장르별 평균 평점 — ratings + movies 필요):
```sql
SELECT
    m.genres,
    ROUND(AVG(r.rating), 2) AS avg_rating,
    COUNT(*) AS cnt
FROM memory.default.ratings r
JOIN memory.default.movies m ON r.movie_id = m.id
GROUP BY m.genres
ORDER BY avg_rating DESC
LIMIT 20
```

예시 (성별·장르 평점 — ratings + users + movies 필요):
```sql
SELECT
    u.gender,
    m.genres,
    ROUND(AVG(r.rating), 2) AS avg_rating
FROM memory.default.ratings r
JOIN memory.default.users u ON r.user_id = u.id
JOIN memory.default.movies m ON r.movie_id = m.id
GROUP BY u.gender, m.genres
ORDER BY avg_rating DESC
LIMIT 50
```

### Step 3. 엔진 라우팅 결정

SQL에 사용할 테이블을 파악한 후 엔진을 선택한다:

| 조건 | 엔진 | 이유 |
|------|------|------|
| `scratch.*` 테이블 참조 | DuckDB | 로컬 저장 결과 |
| `memory.default.*` 또는 Trino 카탈로그 | Trino | 원천 데이터 |
| 마지막 결과를 JSON으로 직접 쿼리 | DuckDB | `read_json_auto` 활용 |

**DuckDB에서 마지막 결과 바로 쿼리하는 방법:**
```sql
-- /tmp/last_result.json을 테이블처럼 사용
SELECT * FROM read_json_auto('/tmp/last_result.json') WHERE avg_rating > 3.2
```

### Step 4. 쿼리 실행

엔진은 자동 감지되므로 `--engine` 생략 가능:
```bash
# Trino (memory.default.* 테이블)
python scripts/run_query.py "<SQL>" json | tee /tmp/last_result.json

# DuckDB (scratch.* 또는 read_json_auto 포함 시 자동 라우팅)
python scripts/run_query.py "<SQL>" json | tee /tmp/last_result.json
```

마크다운 테이블 출력:
```bash
python scripts/run_query.py "<SQL>" table
```

### Step 5. 응답 형식

1. **엔진** — `[Trino]` 또는 `[DuckDB]` 중 어느 엔진을 사용했는지 한 줄
2. **생성한 SQL** (코드블록)
3. **실행 결과** (마크다운 테이블)
4. **인사이트** — 결과에서 눈에 띄는 점 1~3줄
5. 후속 액션 제안:
   - 시각화: `/chart bar` 또는 `/chart pie`
   - 중간 결과 저장: `/save <name>` (이후 `scratch.<name>`으로 재참조 가능)
