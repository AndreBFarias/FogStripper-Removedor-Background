import logging
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core import logger_config


class TestLoggerConfig:
    def test_log_dir_is_absolute(self) -> None:
        assert os.path.isabs(logger_config.LOG_DIR)

    def test_log_file_is_in_log_dir(self) -> None:
        assert logger_config.LOG_FILE.startswith(logger_config.LOG_DIR)

    def test_get_log_path_returns_log_file(self) -> None:
        result: str = logger_config.get_log_path()
        assert result == logger_config.LOG_FILE

    def test_setup_logging_configures_root_logger(self, temp_dir: Path) -> None:
        test_log_dir: str = str(temp_dir / "logs")
        test_log_file: str = str(temp_dir / "logs" / "test.log")

        with patch.object(logger_config, "LOG_DIR", test_log_dir):
            with patch.object(logger_config, "LOG_FILE", test_log_file):
                logger_config.setup_logging()

                root_logger: logging.Logger = logging.getLogger()
                assert root_logger.level == logging.INFO

    def test_log_directory_created(self, temp_dir: Path) -> None:
        test_log_dir: str = str(temp_dir / "new_logs")
        test_log_file: str = str(temp_dir / "new_logs" / "app.log")

        with patch.object(logger_config, "LOG_DIR", test_log_dir):
            with patch.object(logger_config, "LOG_FILE", test_log_file):
                logger_config.setup_logging()

                assert os.path.exists(test_log_dir)

    def test_logger_has_file_handler(self, temp_dir: Path) -> None:
        test_log_dir: str = str(temp_dir / "handler_test")
        test_log_file: str = str(temp_dir / "handler_test" / "app.log")

        with patch.object(logger_config, "LOG_DIR", test_log_dir):
            with patch.object(logger_config, "LOG_FILE", test_log_file):
                logger_config.setup_logging()

                root_logger: logging.Logger = logging.getLogger()
                handler_types = [type(h).__name__ for h in root_logger.handlers]
                assert any("File" in t or "Rotating" in t for t in handler_types)
