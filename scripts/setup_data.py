#!/usr/bin/env python3
"""
Trino memory connector에 샘플 데이터(MovieLens 스타일)를 로드합니다.
docker-compose up 후 한 번만 실행하면 됩니다.
"""
import random
import time
import trino

GENRES = ["Action", "Comedy", "Drama", "Thriller", "Romance", "Horror", "Sci-Fi", "Animation"]
TITLES = [
    "Inception", "The Dark Knight", "Interstellar", "Parasite", "Avengers",
    "La La Land", "Whiplash", "The Matrix", "Pulp Fiction", "Forrest Gump",
    "Schindler's List", "Goodfellas", "The Silence of the Lambs", "Fight Club",
    "The Shawshank Redemption", "12 Angry Men", "Spirited Away", "Your Name",
    "Oldboy", "Burning", "Train to Busan", "Snowpiercer", "Okja",
    "Minari", "Past Lives", "Decision to Leave", "The Wailing", "A Taxi Driver",
    "Memories of Murder", "Oasis",
]


def connect():
    return trino.dbapi.connect(
        host="localhost",
        port=8080,
        user="admin",
        catalog="memory",
        schema="default",
    )


def execute(cursor, sql: str):
    print(f"  → {sql[:80]}{'...' if len(sql) > 80 else ''}")
    cursor.execute(sql)
    cursor.fetchall()


def setup():
    conn = connect()
    cur = conn.cursor()

    print("테이블 생성 중...")
    execute(cur, "DROP TABLE IF EXISTS memory.default.ratings")
    execute(cur, "DROP TABLE IF EXISTS memory.default.movies")
    execute(cur, "DROP TABLE IF EXISTS memory.default.users")

    execute(cur, """
        CREATE TABLE memory.default.movies (
            id           bigint,
            title        varchar,
            genres       varchar,
            release_year integer
        )
    """)
    execute(cur, """
        CREATE TABLE memory.default.users (
            id         bigint,
            gender     varchar,
            age        integer,
            occupation integer
        )
    """)
    execute(cur, """
        CREATE TABLE memory.default.ratings (
            user_id  bigint,
            movie_id bigint,
            rating   double,
            rated_at timestamp(3)
        )
    """)

    print("영화 데이터 삽입 중...")
    random.seed(42)
    movie_rows = []
    for i, title in enumerate(TITLES, start=1):
        genre = "|".join(random.sample(GENRES, k=random.randint(1, 3)))
        year = random.randint(1990, 2024)
        safe_title = title.replace("'", "''")
        movie_rows.append(f"({i}, '{safe_title}', '{genre}', {year})")
    execute(cur, f"INSERT INTO memory.default.movies VALUES {', '.join(movie_rows)}")

    print("사용자 데이터 삽입 중...")
    user_rows = []
    for i in range(1, 51):
        gender = random.choice(["M", "F"])
        age = random.randint(18, 65)
        occ = random.randint(0, 20)
        user_rows.append(f"({i}, '{gender}', {age}, {occ})")
    execute(cur, f"INSERT INTO memory.default.users VALUES {', '.join(user_rows)}")

    print("평점 데이터 삽입 중...")
    rating_pairs = set()
    rating_rows = []
    while len(rating_rows) < 500:
        uid = random.randint(1, 50)
        mid = random.randint(1, len(TITLES))
        if (uid, mid) in rating_pairs:
            continue
        rating_pairs.add((uid, mid))
        rating = round(random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]), 1)
        days_ago = random.randint(0, 365)
        ts = f"2024-01-01 00:00:00.000"
        rating_rows.append(f"({uid}, {mid}, {rating}, TIMESTAMP '{ts}')")

    # 500개를 100개씩 나눠 삽입 (Trino INSERT 크기 제한 대비)
    chunk = 100
    for i in range(0, len(rating_rows), chunk):
        batch = rating_rows[i:i + chunk]
        execute(cur, f"INSERT INTO memory.default.ratings VALUES {', '.join(batch)}")

    print("\n샘플 데이터 로드 완료!")
    print(f"  movies : {len(TITLES)}개")
    print(f"  users  : 50개")
    print(f"  ratings: {len(rating_rows)}개")


if __name__ == "__main__":
    setup()
