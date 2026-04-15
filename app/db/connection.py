import logging
import pymysql
from contextvars import ContextVar
from typing import Any

logger = logging.getLogger(__name__)

_db_name_context: ContextVar[str | None] = ContextVar("db_name", default=None)


def set_db_name(db_name: str | None) -> None:
    """Establece el nombre de BD para el contexto actual (request)."""
    _db_name_context.set(db_name)


def get_db_name() -> str | None:
    """Obtiene el nombre de BD del contexto actual."""
    return _db_name_context.get()


async def fetch_one(
    query: str, params: tuple = (), db_name: str | None = None
) -> dict[str, Any] | None:
    from app.core.config import settings

    target_db = db_name or _db_name_context.get() or settings.DB_NAME
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=target_db,
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


async def fetch_all(
    query: str, params: tuple = (), db_name: str | None = None
) -> list[dict[str, Any]]:
    from app.core.config import settings

    target_db = db_name or _db_name_context.get() or settings.DB_NAME
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=target_db,
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
