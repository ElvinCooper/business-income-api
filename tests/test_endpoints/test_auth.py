from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestLogin:
    def test_login_success(self, client):
        with patch(
            "app.api.v1.endpoints.auth.fetch_one", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = {
                "idusuario": 1,
                "usuario": "testuser",
                "clave": "password123",
                "fullname": "Test User",
                "cia": 1,
                "empresa": "Test Corp",
            }

            response = client.post(
                "/api/v1/auth/login",
                json={"usuario": "testuser", "clave": "password123"},
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["usuario"] == "testuser"
            assert data["token_type"] == "bearer"

    def test_login_user_not_found(self, client):
        with patch(
            "app.api.v1.endpoints.auth.fetch_one", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = None

            response = client.post(
                "/api/v1/auth/login",
                json={"usuario": "nonexistent", "clave": "password"},
            )

            assert response.status_code == 401
            assert "message" in response.json()

    def test_login_wrong_password(self, client):
        with patch(
            "app.api.v1.endpoints.auth.fetch_one", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = {
                "idusuario": 1,
                "usuario": "testuser",
                "clave": "correct_password",
                "fullname": "Test User",
                "cia": 1,
                "empresa": "Test Corp",
            }

            response = client.post(
                "/api/v1/auth/login",
                json={"usuario": "testuser", "clave": "wrong_password"},
            )

            assert response.status_code == 401


class TestGetCurrentUserInfo:
    def test_get_me_success(self, client, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "idusuario" in data
        assert "usuario" in data

    def test_get_me_no_token(self, client):
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401


class TestLogout:
    def test_logout_success(self, client, auth_headers):
        with patch("app.api.v1.endpoints.auth.add_token_to_blocklist"):
            response = client.post("/api/v1/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        assert "Sesión cerrada" in response.json()["message"]

    def test_logout_no_token(self, client):
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401
