#!/usr/bin/env python3
"""
Trino information_schema에서 테이블·컬럼 정보를 가져와
catalog/schema.yaml과 병합합니다.

- Trino가 소스 오브 트루스 (컬럼명, 타입)
- 기존 YAML의 description은 보존 (사람이 작성한 내용)
- 새 테이블·컬럼은 description 빈 채로 추가

사용법:
  python scripts/sync_catalog.py [--catalog memory] [--schema default]
"""
import argparse
from pathlib import Path

import trino
import yaml

CATALOG_FILE = Path("catalog/schema.yaml")


def fetch_schema(catalog: str, schema: str) -> dict:
    """Trino information_schema에서 컬럼 목록을 가져온다."""
    conn = trino.dbapi.connect(
        host="localhost",
        port=8080,
        user="admin",
    )
    cur = conn.cursor()
    cur.execute(f"""
        SELECT
            table_name,
            column_name,
            data_type
        FROM {catalog}.information_schema.columns
        WHERE table_schema = '{schema}'
        ORDER BY table_name, ordinal_position
    """)
    rows = cur.fetchall()

    tables: dict = {}
    for table_name, column_name, data_type in rows:
        tables.setdefault(table_name, []).append({
            "name": column_name,
            "type": data_type,
        })
    return tables


def load_existing() -> dict:
    if CATALOG_FILE.exists():
        with open(CATALOG_FILE) as f:
            return yaml.safe_load(f) or {}
    return {}


def merge(existing: dict, fetched: dict, catalog: str, schema: str) -> dict:
    """Trino에서 가져온 스키마를 기존 YAML과 병합한다. description은 보존."""
    result = existing.copy()

    # 기존 테이블 description 맵 추출
    existing_tables: dict = (
        result
        .get("catalogs", {})
        .get(catalog, {})
        .get("schemas", {})
        .get(schema, {})
        .get("tables", {})
        or {}
    )

    merged_tables = {}
    for table_name, columns in fetched.items():
        existing_table = existing_tables.get(table_name, {})
        existing_cols = {
            c["name"]: c
            for c in existing_table.get("columns", [])
        }

        merged_columns = []
        for col in columns:
            existing_col = existing_cols.get(col["name"], {})
            merged_columns.append({
                "name": col["name"],
                "type": col["type"],
                "description": existing_col.get("description", ""),
            })

        merged_tables[table_name] = {
            "description": existing_table.get("description", ""),
            "columns": merged_columns,
        }

    result.setdefault("catalogs", {})
    result["catalogs"].setdefault(catalog, {})
    result["catalogs"][catalog].setdefault("schemas", {})
    result["catalogs"][catalog]["schemas"].setdefault(schema, {})
    result["catalogs"][catalog]["schemas"][schema]["tables"] = merged_tables
    return result


def save(data: dict):
    CATALOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CATALOG_FILE, "w") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="memory")
    parser.add_argument("--schema", default="default")
    args = parser.parse_args()

    print(f"Trino에서 스키마 수집 중 ({args.catalog}.{args.schema})...")
    fetched = fetch_schema(args.catalog, args.schema)

    if not fetched:
        print("테이블이 없습니다. setup_data.py를 먼저 실행하세요.")
        return

    existing = load_existing()
    merged = merge(existing, fetched, args.catalog, args.schema)
    save(merged)

    print(f"catalog/schema.yaml 업데이트 완료: {list(fetched.keys())}")
    print("\n※ description 필드를 직접 채워두면 SQL 생성 품질이 향상됩니다.")


if __name__ == "__main__":
    main()
