from unittest.mock import MagicMock, patch

import pytest

from app.core.dependencies import CurrentUser, get_current_user


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_no_credentials_raises_401(self):
        with patch("app.core.dependencies.security") as mock_security:
            from fastapi import HTTPException, status

            mock_credentials = None
            mock_dep = MagicMock()
            mock_dep.return_value = mock_credentials

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(None)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Token no proporcionado" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self):
        from fastapi import HTTPException, status

        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid-token"

        with patch("app.core.dependencies.decode_access_token", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Token inválido o expirado" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_revoked_token_raises_401(self):
        from fastapi import HTTPException, status

        mock_credentials = MagicMock()
        mock_credentials.credentials = "some-token"

        payload = {
            "sub": "1",
            "username": "test",
            "db_name": "test_db",
            "jti": "revoked-jti",
        }

        with patch("app.core.dependencies.decode_access_token", return_value=payload):
            with patch("app.core.dependencies.is_token_revoked", return_value=True):
                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_credentials)

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "Token ha sido revocado" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_valid_token_returns_current_user(self):
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid-token"

        payload = {
            "sub": "1",
            "username": "testuser",
            "fullname": "Test User",
            "cia": 1,
            "empresa": "Test Corp",
            "db_name": "test_db",
            "jti": "valid-jti",
        }

        with patch("app.core.dependencies.decode_access_token", return_value=payload):
            with patch("app.core.dependencies.is_token_revoked", return_value=False):
                result = await get_current_user(mock_credentials)

                assert isinstance(result, CurrentUser)
                assert result.user_id == 1
                assert result.username == "testuser"
                assert result.cia == 1

    @pytest.mark.asyncio
    async def test_token_missing_sub_raises_401(self):
        from fastapi import HTTPException, status

        mock_credentials = MagicMock()
        mock_credentials.credentials = "token-without-sub"

        payload = {"username": "test"}

        with patch("app.core.dependencies.decode_access_token", return_value=payload):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
