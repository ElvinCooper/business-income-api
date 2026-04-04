import json
import logging
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.core.logging import JSONFormatter, get_logger, setup_logging


class TestJSONFormatter:
    def test_format_basic_log(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        data = json.loads(result)

        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert data["logger"] == "test"
        assert "timestamp" in data

    def test_format_with_extra_fields(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test",
            args=(),
            exc_info=None,
        )
        record.endpoint = "/api/test"
        record.method = "GET"
        record.status_code = 200
        record.duration_ms = 15.5

        result = formatter.format(record)
        data = json.loads(result)

        assert data["endpoint"] == "/api/test"
        assert data["method"] == "GET"
        assert data["status_code"] == 200
        assert data["duration_ms"] == 15.5

    def test_format_with_exception(self):
        formatter = JSONFormatter()
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error",
            args=(),
            exc_info=exc_info,
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert "exc_info" in data
        assert "Traceback" in data["exc_info"]


class TestSetupLogging:
    def test_setup_logging_info_level(self):
        logger = setup_logging("INFO")
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1

    def test_setup_logging_debug_level(self):
        logger = setup_logging("DEBUG")
        assert logger.level == logging.DEBUG

    def test_setup_logging_invalid_level_defaults_to_info(self):
        logger = setup_logging("INVALID")
        assert logger.level == logging.INFO

    def test_setup_logging_returns_same_logger(self):
        logger1 = setup_logging("INFO")
        logger2 = setup_logging("INFO")
        assert logger1 is logger2


class TestGetLogger:
    def test_get_logger_returns_app_logger(self):
        logger = get_logger()
        assert logger.name == "app"

    def test_get_logger_is_singleton(self):
        logger1 = get_logger()
        logger2 = get_logger()
        assert logger1 is logger2


import sys
