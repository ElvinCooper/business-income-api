import json
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Optional

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


def save_error_log(
    endpoint: str,
    method: str,
    status_code: int,
    error_message: str,
    traceback: str,
    user_id: Optional[int] = None,
    request_data: Optional[dict[str, Any]] = None,
) -> Optional[int]:
    """Guarda un error log en PostgreSQL con sanitización de headers"""
    try:
        sanitized_data = _sanitize_headers(request_data)
        traceback_truncated = traceback[:10000] if traceback else None

        with get_pg_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO error_logs_control_acceso 
                (timestamp, endpoint, method, status_code, user_id, error_message, traceback, request_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    datetime.now(),
                    endpoint[:255],
                    method[:10],
                    status_code,
                    user_id,
                    error_message[:5000],
                    traceback_truncated,
                    json.dumps(sanitized_data) if sanitized_data else None,
                ),
            )
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            return result[0] if result else None
    except OperationalError as e:
        logger.error(f"Failed to save error log: {e}")
        return None


def cleanup_old_error_logs(days: int = 60) -> int:
    """Elimina logs de errores mayores a X días"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        with get_pg_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM error_logs_control_acceso WHERE timestamp < %s",
                (cutoff_date,),
            )
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            logger.info(f"Deleted {deleted_count} old error logs")
            return deleted_count
    except OperationalError as e:
        logger.error(f"Failed to cleanup old error logs: {e}")
        return 0


def _sanitize_headers(headers: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """Elimina headers sensibles antes de guardar"""
    if not headers:
        return None

    sensitive_keys = {
        "authorization",
        "cookie",
        "x-api-key",
        "x-auth-token",
        "password",
        "secret",
        "token",
    }

    sanitized = {}
    for key, value in headers.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        else:
            sanitized[key] = value

    return sanitized
