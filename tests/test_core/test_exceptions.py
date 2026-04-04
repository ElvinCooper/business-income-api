from fastapi import HTTPException, Request, status
from unittest.mock import MagicMock

from app.core.exceptions import (
    _sanitize_header_value,
    generic_exception_handler,
    http_exception_handler,
)


class TestSanitizeHeaderValue:
    def test_sanitize_none(self):
        result = _sanitize_header_value(None)
        assert result is None

    def test_sanitize_bearer_token(self):
        result = _sanitize_header_value("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        assert result == "Bearer ***"

    def test_sanitize_bearer_lowercase(self):
        result = _sanitize_header_value("bearer token123")
        assert result == "Bearer ***"

    def test_sanitize_other_value(self):
        result = _sanitize_header_value("some-secret")
        assert result == "***"


class TestHTTPExceptionHandler:
    def test_http_exception_handler_returns_401(self):
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"

        exc = HTTPException(status_code=401, detail="Unauthorized")

        import asyncio

        result = asyncio.get_event_loop().run_until_complete(
            http_exception_handler(request, exc)
        )

        assert result.status_code == 401
        assert result.body == b'{"message":"Unauthorized"}'

    def test_http_exception_handler_returns_404(self):
        request = MagicMock(spec=Request)
        request.url.path = "/api/nonexistent"
        request.method = "POST"

        exc = HTTPException(status_code=404, detail="Not found")

        import asyncio

        result = asyncio.get_event_loop().run_until_complete(
            http_exception_handler(request, exc)
        )

        assert result.status_code == 404


class TestGenericExceptionHandler:
    def test_generic_exception_returns_500(self):
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"

        exc = ValueError("Something went wrong")

        import asyncio

        result = asyncio.get_event_loop().run_until_complete(
            generic_exception_handler(request, exc)
        )

        assert result.status_code == 500
        assert result.body == b'{"message":"Error interno del servidor"}'
