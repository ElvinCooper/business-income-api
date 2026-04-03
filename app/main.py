from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.db.connection import db_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_connection.connect()
    yield
    await db_connection.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(api_v1_router, prefix="/api")
