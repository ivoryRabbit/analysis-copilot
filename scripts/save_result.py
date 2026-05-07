#!/usr/bin/env python3
"""
/tmp/last_result.json을 DuckDB scratch 테이블로 저장합니다.

사용법:
  python scripts/save_result.py <table_name>

예시:
  python scripts/save_result.py genre_ratings
  → DuckDB의 scratch.genre_ratings 테이블로 저장
"""
import sys
from pathlib import Path

import duckdb

SCRATCH_DB = Path("scratch/scratch.duckdb")
LAST_RESULT = Path("/tmp/last_result.json")


def save(name: str):
    if not LAST_RESULT.exists():
        print("저장할 결과가 없습니다. 먼저 /analyze를 실행해 주세요.")
        sys.exit(1)

    SCRATCH_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(SCRATCH_DB))

    conn.execute(f"""
        CREATE OR REPLACE TABLE scratch.{name} AS
        SELECT * FROM read_json_auto('{LAST_RESULT}')
    """)

    count = conn.execute(f"SELECT COUNT(*) FROM scratch.{name}").fetchone()[0]
    cols = [r[0] for r in conn.execute(f"DESCRIBE scratch.{name}").fetchall()]

    print(f"저장 완료: scratch.{name}")
    print(f"  rows   : {count}")
    print(f"  columns: {', '.join(cols)}")
    print(f"\n이후 쿼리 예시:")
    print(f"  SELECT * FROM scratch.{name} LIMIT 10")


def list_tables():
    if not SCRATCH_DB.exists():
        print("저장된 테이블이 없습니다.")
        return

    conn = duckdb.connect(str(SCRATCH_DB))
    rows = conn.execute("""
        SELECT table_name, estimated_size
        FROM duckdb_tables()
        WHERE schema_name = 'scratch'
        ORDER BY table_name
    """).fetchall()

    if not rows:
        print("저장된 테이블이 없습니다.")
        return

    print("scratch DB 테이블 목록:")
    for name, size in rows:
        print(f"  scratch.{name}  ({size} rows)")


if __name__ == "__main__":
    if not sys.argv[1:] or sys.argv[1] == "--list":
        list_tables()
    else:
        save(sys.argv[1])
