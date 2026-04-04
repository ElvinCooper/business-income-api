import pytest


class TestErrorEndpoints:
    def test_error_endpoints_are_routes(self, client):
        from starlette.routing import Route

        api_routes = []
        for route in client.app.routes:
            if hasattr(route, "path"):
                api_routes.append(route.path)

        assert "/api/v1/test-errors/{endpoint}" in api_routes or any(
            "test-errors" in r for r in api_routes
        )
