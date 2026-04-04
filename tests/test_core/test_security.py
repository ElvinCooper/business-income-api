from datetime import timedelta

import pytest

from app.core.security import create_access_token, decode_access_token


class TestCreateAccessToken:
    def test_create_access_token_basic(self):
        token = create_access_token(data={"sub": "1", "username": "test"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiration(self):
        token = create_access_token(data={"sub": "1"}, expires_delta=timedelta(hours=1))
        assert isinstance(token, str)

    def test_create_access_token_includes_jti(self):
        token = create_access_token(data={"sub": "1"})
        payload = decode_access_token(token)
        assert "jti" in payload
        assert payload["sub"] == "1"


class TestDecodeAccessToken:
    def test_decode_valid_token(self):
        token = create_access_token(data={"sub": "1", "username": "testuser"})
        payload = decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["username"] == "testuser"

    def test_decode_invalid_token(self):
        payload = decode_access_token("invalid.token.here")
        assert payload is None

    def test_decode_empty_token(self):
        payload = decode_access_token("")
        assert payload is None

    def test_decode_tampered_token(self):
        token = create_access_token(data={"sub": "1"})
        tampered = token[:-5] + "xxxxx"
        payload = decode_access_token(tampered)
        assert payload is None
