# /schema — 카탈로그 스키마 탐색

`catalog/schema.yaml`을 읽어 사용 가능한 테이블·컬럼·관계 정보를 보여준다.

## 사용법

```
/schema              # 전체 테이블 목록 + 관계 그래프
/schema <table>      # 특정 테이블의 컬럼 상세
/schema relationships  # 테이블 간 JOIN 경로 목록
```

## 실행 절차

### Step 1. schema.yaml 읽기

```bash
cat catalog/schema.yaml
```

### Step 2. 출력 형식

**전체 목록** (`/schema`):
```
카탈로그: memory
└─ 스키마: default
   ├─ movies    — 영화 정보 (MovieLens 기반 샘플 데이터)
   ├─ users     — 사용자 정보
   └─ ratings   — 사용자별 영화 평점

관계 그래프:
  ratings.user_id  →  users.id
  ratings.movie_id →  movies.id
```

**테이블 상세** (`/schema ratings`):

| 컬럼 | 타입 | 설명 |
|------|------|------|
| user_id | bigint | 사용자 ID (users.id 참조) |
| ... | ... | ... |

**관계 목록** (`/schema relationships`):

| 관계명 | FROM | TO | JOIN 스니펫 |
|--------|------|----|-------------|
| ratings_to_users | ratings.user_id | users.id | `ratings r JOIN users u ON r.user_id = u.id` |
| ratings_to_movies | ratings.movie_id | movies.id | `ratings r JOIN movies m ON r.movie_id = m.id` |
| ratings_to_users_movies | ratings.user_id, ratings.movie_id | users.id, movies.id | 3-way JOIN |

### Step 3. 추가 안내

스키마가 최신이 아닌 것 같으면 `/sync`를 먼저 실행하라고 안내한다.
새 테이블을 추가할 때는 `catalog/schema.yaml`의 `relationships` 섹션에도 FK 관계를 등록해야 한다고 안내한다.
