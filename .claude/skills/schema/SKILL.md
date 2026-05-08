# /schema — 카탈로그 스키마 탐색

온톨로지 repo의 `schema.yaml`을 읽어 사용 가능한 테이블·컬럼·관계 정보를 보여준다.

## 사용법

```
/schema              # 전체 테이블 목록 + 관계 그래프
/schema <table>      # 특정 테이블의 컬럼 상세
/schema relationships  # 테이블 간 JOIN 경로 목록
```

## 실행 절차

### Step 1. schema.yaml 읽기

```bash
cat $(python scripts/sync_catalog.py --print-schema-path)
```

### Step 2. 출력 형식

**전체 목록** (`/schema`):
```
카탈로그: memory
└─ 스키마: default
   ├─ movies    — 영화 정보 (MovieLens 기반 샘플 데이터)
   ├─ users     — 사용자 정보
   └─ ratings   — 사용자별 영화 평점

JOIN 경로:
  ratings ←→ users          ratings r JOIN users u ON r.user_id = u.id
  ratings ←→ movies         ratings r JOIN movies m ON r.movie_id = m.id
  ratings ←→ users + movies ratings r JOIN users u ON r.user_id = u.id JOIN movies m ON r.movie_id = m.id
```

이어서 스키마의 테이블·컬럼·관계를 바탕으로 분석 가능한 질문을 3~5개 제안한다:

```
💡 분석 제안 (바로 /analyze로 실행 가능):
  • 장르별 평균 평점과 평점 수
  • 성별·나이대별 선호 장르
  • 개봉 연도별 평점 트렌드
  • 평점 상위 20개 영화 (최소 50개 평점 이상)
  • 직업 코드별 평균 평점 분포
```

제안 질문은 실제 컬럼(genres, gender, age, occupation, release_year 등)과 relationships를 기반으로 생성한다. 단순 단일 테이블 질문보다 JOIN이 필요한 흥미로운 질문을 우선한다.

**테이블 상세** (`/schema ratings`):

| 컬럼 | 타입 | 설명 |
|------|------|------|
| user_id | bigint | 사용자 ID (users.id 참조) |
| ... | ... | ... |

테이블 상세 출력 후에도 이 테이블과 JOIN 가능한 경로와 관련 분석 제안 2~3개를 덧붙인다.

**관계 목록** (`/schema relationships`):

| 관계명 | FROM | TO | JOIN 스니펫 |
|--------|------|----|-------------|
| ratings_to_users | ratings.user_id | users.id | `ratings r JOIN users u ON r.user_id = u.id` |
| ratings_to_movies | ratings.movie_id | movies.id | `ratings r JOIN movies m ON r.movie_id = m.id` |
| ratings_to_users_movies | ratings.user_id, ratings.movie_id | users.id, movies.id | 3-way JOIN |

### Step 3. 추가 안내

스키마가 최신이 아닌 것 같으면 `/sync`를 먼저 실행하라고 안내한다.
새 테이블을 추가할 때는 온톨로지 repo `schema.yaml`의 `relationships` 섹션에도 FK 관계를 등록하고, `/sync`로 커밋해야 한다고 안내한다.
