from temporalio import activity, workflow

from backend.db.database import SessionMaker
from backend.db.models import Config, TableCatalog, ColumnCatalog


# @activity.defn
async def sync_configs():
    session = SessionMaker()
    try:
        configs = session.query(Config).all()
        return configs
    finally:
        session.close()


# @activity.defn
async def sync_tables(config):
    # Simulate fetching tables from external database (e.g., Trino or Postgres)
    example_tables = [
        {"name": "orders", "description": "Order data"},
        {"name": "customers", "description": "Customer data"}
    ]
    session = SessionMaker()
    try:
        for table in example_tables:
            existing_table = session.query(TableCatalog).filter_by(name=table["name"]).first()
            if existing_table:
                existing_table.description = table["description"]
            else:
                new_table = TableCatalog(name=table["name"], description=table["description"])
                session.add(new_table)
        session.commit()
    finally:
        session.close()
