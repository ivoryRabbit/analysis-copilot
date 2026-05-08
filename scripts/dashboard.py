#!/usr/bin/env python3
"""
scratch 테이블 데이터를 JSON으로 출력합니다.
/dashboard 스킬이 HTML 생성 전 데이터를 읽을 때 사용합니다.

사용법:
  python scripts/dashboard.py --table <table_name>
  python scripts/dashboard.py --table <table_name> --limit 500
"""
import argparse
import json
from pathlib import Path

import duckdb

SCRATCH_DB = Path("scratch/scratch.duckdb")


def read_table(table: str, limit: int) -> list[dict]:
    if not SCRATCH_DB.exists():
        raise FileNotFoundError("scratch/scratch.duckdb 가 없습니다. /save로 결과를 먼저 저장하세요.")
    conn = duckdb.connect(str(SCRATCH_DB))
    return conn.execute(f"SELECT * FROM scratch.{table} LIMIT {limit}").df().to_dict("records")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", required=True, help="scratch 테이블 이름")
    parser.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()

    records = read_table(args.table, args.limit)
    print(json.dumps(records, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
