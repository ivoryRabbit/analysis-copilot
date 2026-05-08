#!/usr/bin/env python3
"""
SQL을 실행하고 결과를 출력합니다. Trino / DuckDB 자동 라우팅.

라우팅 규칙:
  - SQL에 'scratch.' 포함 → DuckDB (scratch/scratch.duckdb)
  - 그 외                 → Trino (localhost:8080)
  - --engine 으로 명시 가능

사용법:
  python scripts/run_query.py "SELECT ..." [table|json] [--engine trino|duckdb]
  echo "SELECT ..." | python scripts/run_query.py - [table|json]
"""
import json
import re
import sys
from pathlib import Path

import duckdb
from tabulate import tabulate

from trino_client import get_connection

SCRATCH_DB = Path("scratch/scratch.duckdb")


def detect_engine(sql: str) -> str:
    if re.search(r'\bscratch\b', sql, re.IGNORECASE):
        return "duckdb"
    return "trino"


def run_trino(sql: str) -> tuple[list[str], list]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    return columns, rows


def run_duckdb(sql: str) -> tuple[list[str], list]:
    SCRATCH_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(SCRATCH_DB))
    result = conn.execute(sql)
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()
    return columns, rows


def run(sql: str, fmt: str = "table", engine: str = "auto") -> list[dict]:
    if engine == "auto":
        engine = detect_engine(sql)

    if engine == "duckdb":
        columns, rows = run_duckdb(sql)
    else:
        columns, rows = run_trino(sql)

    records = [dict(zip(columns, row)) for row in rows]

    if fmt == "json":
        print(json.dumps(records, ensure_ascii=False, default=str))
    else:
        print(tabulate(rows, headers=columns, tablefmt="github"))
        print(f"\n{len(rows)} rows  [{engine}]")

    return records


if __name__ == "__main__":
    args = sys.argv[1:]

    engine_arg = "auto"
    if "--engine" in args:
        idx = args.index("--engine")
        engine_arg = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    sql_arg = args[0] if args else "-"
    fmt_arg = args[1] if len(args) > 1 else "table"

    sql = sys.stdin.read().strip() if sql_arg == "-" else sql_arg
    run(sql, fmt_arg, engine_arg)
