import logging
import pymysql
from typing import Any

logger = logging.getLogger(__name__)


async def fetch_one(query: str, params: tuple = ()) -> dict[str, Any] | None:
    from app.core.config import settings

    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
        )
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
        connection.close()
        return result
    except Exception as e:
        logger.error(f"fetch_one error: {e}")
        raise


async def fetch_all(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    from app.core.config import settings

    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
        )
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
        connection.close()
        return result
    except Exception as e:
        logger.error(f"fetch_all error: {e}")
        raise
