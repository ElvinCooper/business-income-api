import logging
from contextlib import contextmanager
from datetime import datetime

import psycopg2
from psycopg2 import OperationalError

from app.core.config import settings

logger = logging.getLogger(__name__)


@contextmanager
def get_pg_connection():
    """Conexión a PostgreSQL para blocklist de tokens"""
    try:
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            connect_timeout=5,
        )
        try:
            yield conn
        finally:
            conn.close()
    except OperationalError as e:
        logger.error(f"PostgreSQL connection error: {e}")
        raise


def is_token_revoked(jti: str) -> bool:
    """Verifica si un token ha sido revocado"""
    try:
        with get_pg_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM blocklist_control_acceso WHERE jti = %s", (jti,)
            )
            result = cursor.fetchone()
            cursor.close()
            return result is not None
    except OperationalError:
        logger.warning(
            f"Could not verify token revocation for jti={jti}, assuming not revoked"
        )
        return False


def add_token_to_blocklist(jti: str, idusuario: int) -> None:
    """Agrega un token a la blocklist"""
    try:
        with get_pg_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO blocklist_control_acceso (jti, idusuario, fecha_creacion) VALUES (%s, %s, %s)",
                (jti, idusuario, datetime.now()),
            )
            conn.commit()
            cursor.close()
    except OperationalError as e:
        logger.error(f"Failed to add token to blocklist: {e}")
        raise
