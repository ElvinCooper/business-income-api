import aiomysql
import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(self):
        self.pool: aiomysql.Pool | None = None

    async def connect(self) -> None:
        logger.info(
            f"Connecting to DB: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )
        try:
            self.pool = await aiomysql.create_pool(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                db=settings.DB_NAME,
                autocommit=True,
                minsize=5,
                maxsize=20,
            )
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    async def disconnect(self) -> None:
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def fetch_one(self, query: str, params: tuple = ()) -> dict[str, Any] | None:
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                return await cur.fetchone()

    async def fetch_all(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                return await cur.fetchall()

    async def execute(self, query: str, params: tuple = ()) -> int:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return cur.lastrowid


db_connection = DatabaseConnection()


async def get_db() -> DatabaseConnection:
    return db_connection
