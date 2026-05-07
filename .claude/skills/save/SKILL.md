# /save — 결과를 DuckDB scratch 테이블로 저장

`/analyze`의 마지막 결과를 DuckDB에 named 테이블로 저장한다.
저장 후 `/analyze`에서 `scratch.<name>`으로 직접 참조해 후속 분석을 이어갈 수 있다.

## 사용법

```
/save <name>     # 마지막 결과를 scratch.<name>으로 저장
/save --list     # 저장된 scratch 테이블 목록 확인
```

예시:
- `/save genre_ratings`   → `scratch.genre_ratings` 테이블 생성
- `/save top_movies`      → `scratch.top_movies` 테이블 생성
- `/save --list`          → 저장된 테이블 목록

## 실행 절차

### Step 1. 저장

```bash
python scripts/save_result.py <name>
```

### Step 2. 목록 확인 (--list)

```bash
python scripts/save_result.py --list
```

### Step 3. 저장 완료 후 안내

저장 후 활용 예시를 보여준다:

```
scratch.genre_ratings 저장 완료 (8 rows)

이어서 분석하려면:
  /analyze scratch.genre_ratings에서 평점 3.2 이상인 장르만
  /analyze scratch.genre_ratings과 users를 조인해서 성별별 선호 장르
```

## 참고

- scratch DB 파일: `scratch/scratch.duckdb` (로컬 영속, 재시작해도 유지)
- Trino memory connector와 달리 DuckDB scratch는 재시작해도 데이터가 남음
- `CREATE OR REPLACE`로 동일 이름 저장 시 덮어씀
