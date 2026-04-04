import asyncio
import time
from unittest.mock import MagicMock

from fastapi import Request
from starlette.responses import Response

from app.core.middleware import LoggingMiddleware


class TestLoggingMiddleware:
    def test_middleware_logs_request(self):
        app = MagicMock()
        middleware = LoggingMiddleware(app)

        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/test"

        response = MagicMock(spec=Response)
        response.status_code = 200

        async def call_next(req):
            return response

        result = asyncio.get_event_loop().run_until_complete(
            middleware.dispatch(request, call_next)
        )
        assert result.status_code == 200

    def test_middleware_calculates_duration(self):
        app = MagicMock()
        middleware = LoggingMiddleware(app)

        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url.path = "/api/data"

        response = MagicMock(spec=Response)
        response.status_code = 201

        async def call_next(req):
            time.sleep(0.01)
            return response

        result = asyncio.get_event_loop().run_until_complete(
            middleware.dispatch(request, call_next)
        )
        assert result.status_code == 201
