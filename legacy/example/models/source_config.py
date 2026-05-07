from pydantic import BaseModel


class SourceConfig(BaseModel):
    source_type: str
    name: str
    host: str = "localhost"
    port: int = 5432
    user: str = ""
    password: str = ""
    database: str = "default"
