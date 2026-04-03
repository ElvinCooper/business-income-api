import pymysql
import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


async def execute_query(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    logger.info(f"Executing query on {settings.DB_HOST}")
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
            else:
                results = []
        connection.close()
        return results
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise


async def fetch_one(query: str, params: tuple = ()) -> dict[str, Any] | None:
    results = await execute_query(query, params)
    return results[0] if results else None


async def fetch_all(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    return await execute_query(query, params)
