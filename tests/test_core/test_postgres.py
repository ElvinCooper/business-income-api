from unittest.mock import MagicMock, patch

import pytest

from app.db.postgres import _sanitize_headers


class TestSanitizeHeaders:
    def test_sanitize_none_headers(self):
        result = _sanitize_headers(None)
        assert result is None

    def test_sanitize_empty_headers(self):
        result = _sanitize_headers({})
        assert result is None or result == {}

    def test_sanitize_authorization_header(self):
        headers = {
            "Authorization": "Bearer token123",
            "Content-Type": "application/json",
        }
        result = _sanitize_headers(headers)
        assert result["Authorization"] == "***REDACTED***"
        assert result["Content-Type"] == "application/json"

    def test_sanitize_cookie_header(self):
        headers = {"Cookie": "session=abc123", "Accept": "*/*"}
        result = _sanitize_headers(headers)
        assert result["Cookie"] == "***REDACTED***"
        assert result["Accept"] == "*/*"

    def test_sanitize_case_insensitive(self):
        headers = {"AUTHORIZATION": "Bearer token", "authorization": "Bearer token2"}
        result = _sanitize_headers(headers)
        assert result["AUTHORIZATION"] == "***REDACTED***"
        assert result["authorization"] == "***REDACTED***"


class TestSaveErrorLog:
    def test_save_error_log_with_mock(self):
        with patch("app.db.postgres.get_pg_connection") as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1,)
            mock_conn.return_value.__enter__.return_value.cursor.return_value = (
                mock_cursor
            )

            from app.db.postgres import save_error_log

            result = save_error_log(
                endpoint="/api/test",
                method="GET",
                status_code=500,
                error_message="Test error",
                traceback="Traceback here",
            )

            assert result == 1
            mock_cursor.execute.assert_called_once()

    def test_save_error_log_connection_failure(self):
        from psycopg2 import OperationalError

        with patch("app.db.postgres.get_pg_connection") as mock_conn:
            mock_conn.return_value.__enter__.side_effect = OperationalError(
                "Connection failed"
            )

            from app.db.postgres import save_error_log

            result = save_error_log(
                endpoint="/api/test",
                method="GET",
                status_code=500,
                error_message="Test error",
                traceback="Traceback",
            )

            assert result is None


class TestCleanupOldErrorLogs:
    def test_cleanup_old_logs_success(self):
        with patch("app.db.postgres.get_pg_connection") as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.rowcount = 10
            mock_conn.return_value.__enter__.return_value.cursor.return_value = (
                mock_cursor
            )

            from app.db.postgres import cleanup_old_error_logs

            result = cleanup_old_error_logs(days=60)

            assert result == 10
            mock_cursor.execute.assert_called_once()

    def test_cleanup_old_logs_connection_failure(self):
        from psycopg2 import OperationalError

        with patch("app.db.postgres.get_pg_connection") as mock_conn:
            mock_conn.return_value.__enter__.side_effect = OperationalError(
                "Connection failed"
            )

            from app.db.postgres import cleanup_old_error_logs

            result = cleanup_old_error_logs(days=60)

            assert result == 0
