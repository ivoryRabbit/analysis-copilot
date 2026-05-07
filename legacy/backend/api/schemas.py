from typing import Optional
from pydantic import BaseModel, ConfigDict


class ConfigCreate(BaseModel):
    name: str
    type: str
    host: str
    port: int = 5432
    user: str
    password: str
    database: str
    sync_period: int = 5


class ConfigUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    sync_period: Optional[int] = None


class ConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    host: str
    port: int
    user: str
    database: str
    sync_period: int


class ColumnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    table_id: int
    name: str
    type: str
    description: Optional[str]


class TableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    config_id: int
    name: str
    description: Optional[str]


class TableDetailResponse(TableResponse):
    columns: list[ColumnResponse] = []


class ColumnUpsert(BaseModel):
    name: str
    type: str
    description: Optional[str] = None


class TableUpdateRequest(BaseModel):
    description: Optional[str] = None
    columns: list[ColumnUpsert] = []
