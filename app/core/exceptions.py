import traceback
from typing import Callable

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger
from app.db.postgres import save_error_log
from app.schemas.error import ErrorResponse

logger = get_logger()


def _sanitize_header_value(value: str | None) -> str | None:
    if value is None:
        return None
    if value.lower().startswith("bearer "):
        return "Bearer ***"
    return "***"


def _log_error_to_db(
    endpoint: str,
    method: str,
    status_code: int,
    error_message: str,
    traceback_str: str,
    user_id: int | None = None,
    request_data: dict | None = None,
) -> None:
    """Función helper para logging asíncrono a PostgreSQL"""
    log_id = save_error_log(
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        error_message=error_message,
        traceback=traceback_str,
        user_id=user_id,
        request_data=request_data,
    )
    if log_id:
        logger.info(f"Error log saved to DB with id: {log_id}")


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware que guarda errores en PostgreSQL de forma asíncrona"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            tb = traceback.format_exc()

            headers_dict = dict(request.headers) if request.headers else None
            user_id = getattr(request.state, "user_id", None)

            _log_error_to_db(
                endpoint=str(request.url.path),
                method=request.method,
                status_code=500,
                error_message=str(exc),
                traceback_str=tb,
                user_id=user_id,
                request_data=headers_dict,
            )

            raise


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(
        f"HTTP exception: {exc.detail}",
        extra={
            "endpoint": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=exc.detail).model_dump(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    tb = traceback.format_exc()

    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "endpoint": request.url.path,
            "method": request.method,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(message="Error interno del servidor").model_dump(),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_middleware(ErrorLoggingMiddleware)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
