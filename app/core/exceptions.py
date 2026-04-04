import traceback
from typing import Callable

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.schemas.error import ErrorResponse

logger = get_logger()


def _sanitize_header_value(value: str | None) -> str | None:
    if value is None:
        return None
    if value.lower().startswith("bearer "):
        return "Bearer ***"
    return "***"


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
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
