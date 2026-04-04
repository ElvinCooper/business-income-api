import psycopg2
from contextlib import contextmanager
from datetime import datetime

from app.core.config import settings


@contextmanager
def get_pg_connection():
    """Conexión a PostgreSQL para blocklist de tokens"""
    conn = psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
    )
    try:
        yield conn
    finally:
        conn.close()


def is_token_revoked(jti: str) -> bool:
    """Verifica si un token ha sidorevocado"""
    with get_pg_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM blocklist_control_acceso WHERE jti = %s", (jti,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None


def add_token_to_blocklist(jti: str, idusuario: int) -> None:
    """Agrega un token a la blocklist"""
    with get_pg_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO blocklist_control_acceso (jti, idusuario, fecha_creacion) VALUES (%s, %s, %s)",
            (jti, idusuario, datetime.now()),
        )
        conn.commit()
        cursor.close()
