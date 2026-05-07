from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.schemas import TableResponse, TableDetailResponse, ColumnResponse, TableUpdateRequest
from backend.db.database import get_session
from backend.db.models import TableCatalog, ColumnCatalog

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/tables", response_model=list[TableResponse])
def list_tables(config_id: Optional[int] = None, session: Session = Depends(get_session)):
    query = session.query(TableCatalog)
    if config_id is not None:
        query = query.filter(TableCatalog.config_id == config_id)
    return query.all()


@router.get("/tables/{table_id}", response_model=TableDetailResponse)
def get_table(table_id: int, session: Session = Depends(get_session)):
    table = session.get(TableCatalog, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table


@router.put("/tables/{table_id}", response_model=TableDetailResponse)
def update_table(table_id: int, body: TableUpdateRequest, session: Session = Depends(get_session)):
    table = session.get(TableCatalog, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    if body.description is not None:
        table.description = body.description

    existing = {col.name: col for col in table.columns}
    for col_data in body.columns:
        if col_data.name in existing:
            existing[col_data.name].type = col_data.type
            existing[col_data.name].description = col_data.description
        else:
            session.add(ColumnCatalog(
                name=col_data.name,
                type=col_data.type,
                description=col_data.description,
                table_id=table_id,
            ))

    session.commit()
    session.refresh(table)
    return table


@router.get("/columns/{table_id}", response_model=list[ColumnResponse])
def list_columns(table_id: int, session: Session = Depends(get_session)):
    table = session.get(TableCatalog, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return session.query(ColumnCatalog).filter(ColumnCatalog.table_id == table_id).all()
