import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing")


@pytest.fixture
def mock_settings():
    with patch.dict(os.environ, {"JWT_SECRET_KEY": "test-secret-key-for-testing"}):
        from app.core.config import Settings

        yield Settings()


@pytest.fixture
def mock_postgres():
    with patch("app.db.postgres.get_db_pool") as mock_pool:
        mock_pool.return_value = MagicMock()
        yield mock_pool


@pytest.fixture
def mock_fetch_one():
    with patch("app.db.connection.fetch_one") as mock:
        yield mock


@pytest.fixture
def mock_fetch_all():
    with patch("app.db.connection.fetch_all") as mock:
        yield mock


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def auth_headers():
    from datetime import timedelta
    from app.core.security import create_access_token

    token = create_access_token(
        data={
            "sub": "1",
            "username": "testuser",
            "fullname": "Test User",
            "cia": 1,
            "empresa": "Test Corp",
            "jti": "test-jti",
        },
        expires_delta=timedelta(minutes=30),
    )
    return {"Authorization": f"Bearer {token}"}
