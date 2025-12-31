import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core import config_loader


class TestConfigLoader:
    def test_load_paths_with_valid_config(self, temp_dir: Path) -> None:
        config_path: Path = temp_dir / "config.json"
        config_data: dict = {
            "venv_rembg": "/path/to/venv_rembg",
            "venv_upscale": "/path/to/venv_upscale",
        }
        config_path.write_text(json.dumps(config_data))

        with patch.object(config_loader, "CONFIG_PATH", str(config_path)):
            config_loader.PATHS = {}
            config_loader.load_paths()

            assert "venv_rembg" in config_loader.PATHS
            assert "venv_upscale" in config_loader.PATHS
            assert config_loader.PATHS["venv_rembg"] == "/path/to/venv_rembg"
            assert config_loader.PATHS["venv_upscale"] == "/path/to/venv_upscale"

    def test_load_paths_with_missing_config(self, temp_dir: Path) -> None:
        fake_config: str = str(temp_dir / "nonexistent.json")
        with patch.object(config_loader, "CONFIG_PATH", fake_config):
            config_loader.PATHS = {}
            config_loader.load_paths()

            assert config_loader.PATHS == {}

    def test_load_paths_with_malformed_config(self, temp_dir: Path) -> None:
        bad_config: Path = temp_dir / "bad_config.json"
        bad_config.write_text("this is not valid json {{{")

        with patch.object(config_loader, "CONFIG_PATH", str(bad_config)):
            config_loader.PATHS = {}
            config_loader.load_paths()

            assert config_loader.PATHS == {}

    def test_paths_is_dict(self) -> None:
        assert isinstance(config_loader.PATHS, dict)

    def test_config_path_is_absolute(self) -> None:
        assert os.path.isabs(config_loader.CONFIG_PATH)
