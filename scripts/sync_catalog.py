#!/usr/bin/env python3
"""
Trino information_schema에서 테이블·컬럼 정보를 가져와
온톨로지 repo의 schema.yaml과 병합합니다.

- Trino가 소스 오브 트루스 (컬럼명, 타입)
- 기존 YAML의 description은 보존 (사람이 작성한 내용)
- 새 테이블·컬럼은 description 빈 채로 추가
- catalog/ontology_config.yaml에서 경로·Trino 연결 정보를 읽는다

사용법:
  python scripts/sync_catalog.py
  python scripts/sync_catalog.py --catalog <c> --schema <s>   # config보다 우선
  python scripts/sync_catalog.py --ontology-path /path/to/schema.yaml
  python scripts/sync_catalog.py --print-schema-path          # 스킬에서 경로 참조용
"""
import argparse
import sys
from pathlib import Path

import yaml

from trino_client import get_connection

ONTOLOGY_CONFIG_FILE = Path("catalog/ontology_config.yaml")


def load_ontology_config() -> dict:
    if not ONTOLOGY_CONFIG_FILE.exists():
        print(
            "오류: catalog/ontology_config.yaml이 없습니다.\n"
            "/sync를 실행해 온톨로지 repo를 먼저 설정하세요.",
            file=sys.stderr,
        )
        sys.exit(1)
    with open(ONTOLOGY_CONFIG_FILE) as f:
        return yaml.safe_load(f) or {}


def resolve_catalog_file(ontology_path: str | None, config: dict) -> Path:
    """온톨로지 경로 우선순위: CLI 인자 > ontology_config.yaml"""
    if ontology_path:
        return Path(ontology_path)
    local_path = config.get("local_path", "catalog/ontology")
    schema_file = config.get("schema_file", "schema.yaml")
    path = Path(local_path) / schema_file
    if not path.exists():
        print(
            f"오류: {path} 가 없습니다.\n"
            "git submodule이 초기화되지 않았습니다. /sync를 실행해 설정하세요.",
            file=sys.stderr,
        )
        sys.exit(1)
    return path


def fetch_schema(catalog: str, schema: str) -> dict:
    """Trino information_schema에서 컬럼 목록을 가져온다."""
    conn = get_connection()
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


def load_existing(catalog_file: Path) -> dict:
    if catalog_file.exists():
        with open(catalog_file) as f:
            return yaml.safe_load(f) or {}
    return {}


def merge(existing: dict, fetched: dict, catalog: str, schema: str) -> dict:
    """Trino에서 가져온 스키마를 기존 YAML과 병합한다. description은 보존."""
    result = existing.copy()

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


def save(data: dict, catalog_file: Path):
    catalog_file.parent.mkdir(parents=True, exist_ok=True)
    with open(catalog_file, "w") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default=None, help="Trino 카탈로그 (기본: ontology_config.yaml의 trino_catalog)")
    parser.add_argument("--schema", default=None, help="Trino 스키마 (기본: ontology_config.yaml의 trino_schema)")
    parser.add_argument("--ontology-path", default=None, help="온톨로지 schema.yaml 경로 (설정 파일보다 우선)")
    parser.add_argument("--print-schema-path", action="store_true", help="schema.yaml 경로만 출력하고 종료")
    args = parser.parse_args()

    config = load_ontology_config()
    catalog_file = resolve_catalog_file(args.ontology_path, config)

    if args.print_schema_path:
        print(catalog_file)
        return

    catalog = args.catalog or config.get("trino_catalog", "memory")
    schema = args.schema or config.get("trino_schema", "default")

    print(f"대상 파일: {catalog_file}")
    print(f"Trino에서 스키마 수집 중 ({catalog}.{schema})...")
    fetched = fetch_schema(catalog, schema)

    if not fetched:
        print("테이블이 없습니다. setup_data.py를 먼저 실행하세요.")
        return

    existing = load_existing(catalog_file)
    merged = merge(existing, fetched, catalog, schema)
    save(merged, catalog_file)

    print(f"{catalog_file} 업데이트 완료: {list(fetched.keys())}")
    print("\n※ description 필드를 직접 채워두면 SQL 생성 품질이 향상됩니다.")


if __name__ == "__main__":
    main()
