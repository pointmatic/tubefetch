# Copyright (c) 2026 Pointmatic
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for tubefetch.core.logging."""

import json
import logging

from tubefetch.core.logging import (
    JsonlFormatter,
    get_logger,
    log_event,
    setup_logging,
)


class TestSetupLogging:
    def test_returns_logger(self):
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "tubefetch"

    def test_info_level_by_default(self):
        logger = setup_logging(verbose=False)
        assert logger.level == logging.INFO

    def test_debug_level_when_verbose(self):
        logger = setup_logging(verbose=True)
        assert logger.level == logging.DEBUG

    def test_clears_existing_handlers(self):
        logger = setup_logging()
        count1 = len(logger.handlers)
        setup_logging()
        count2 = len(logger.handlers)
        assert count1 == count2

    def test_jsonl_handler_added(self, tmp_path):
        path = tmp_path / "logs" / "test.jsonl"
        logger = setup_logging(jsonl_path=path)
        handler_types = [type(h).__name__ for h in logger.handlers]
        assert "JsonlFileHandler" in handler_types

    def test_jsonl_file_created(self, tmp_path):
        path = tmp_path / "test.jsonl"
        setup_logging(jsonl_path=path)
        logger = get_logger()
        logger.info("test message")
        assert path.exists()
        content = path.read_text().strip()
        record = json.loads(content)
        assert record["message"] == "test message"
        assert record["level"] == "INFO"


class TestJsonlFormatter:
    def test_format_basic(self):
        formatter = JsonlFormatter()
        record = logging.LogRecord(
            name="yt_fetch",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="hello",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert data["message"] == "hello"
        assert data["level"] == "INFO"
        assert "timestamp" in data

    def test_format_with_extras(self):
        formatter = JsonlFormatter()
        record = logging.LogRecord(
            name="yt_fetch",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="fail",
            args=(),
            exc_info=None,
        )
        record.video_id = "abc12345678"
        record.event = "metadata_fetch"
        record.details = "some detail"
        record.error = "timeout"
        output = formatter.format(record)
        data = json.loads(output)
        assert data["video_id"] == "abc12345678"
        assert data["event"] == "metadata_fetch"
        assert data["details"] == "some detail"
        assert data["error"] == "timeout"


class TestGetLogger:
    def test_returns_same_logger(self):
        setup_logging()
        logger = get_logger()
        assert logger.name == "tubefetch"


class TestLogEvent:
    def test_log_event(self, tmp_path):
        path = tmp_path / "events.jsonl"
        setup_logging(jsonl_path=path)
        log_event(
            logging.INFO,
            "fetched",
            video_id="abc12345678",
            event="metadata_ok",
        )
        content = path.read_text().strip()
        data = json.loads(content)
        assert data["message"] == "fetched"
        assert data["video_id"] == "abc12345678"
        assert data["event"] == "metadata_ok"
