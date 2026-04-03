import pymysql
from typing import Any


async def fetch_one(query: str, params: tuple = ()) -> dict[str, Any] | None:
    from app.core.config import settings

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


async def fetch_all(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    from app.core.config import settings

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
