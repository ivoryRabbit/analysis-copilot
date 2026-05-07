from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.endpoints import config, catalog, scheduler
from backend.db.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="mini-data-catalog",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(config.router, prefix="/api")
app.include_router(catalog.router, prefix="/api")
app.include_router(scheduler.router, prefix="/api")
