from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.database import Base


class Config(Base):
    __tablename__ = "configs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False, default=5432)
    user = Column(String, nullable=False)
    password = Column(String, nullable=False)
    database = Column(String, nullable=False)
    sync_period = Column(Integer, nullable=False, default=5)

    table_catalogs = relationship("TableCatalog", back_populates="config", cascade="all, delete-orphan")


class TableCatalog(Base):
    __tablename__ = "table_catalogs"
    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("configs.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    config = relationship("Config", back_populates="table_catalogs")
    columns = relationship("ColumnCatalog", back_populates="table", cascade="all, delete-orphan")


class ColumnCatalog(Base):
    __tablename__ = "column_catalogs"
    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("table_catalogs.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    table = relationship("TableCatalog", back_populates="columns")
