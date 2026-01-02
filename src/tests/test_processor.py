import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.constants import VIDEO_EXTENSIONS
from src.core.processor import ProcessThread


class TestProcessThread:
    @pytest.fixture
    def processor(self, sample_image: Path) -> ProcessThread:
        return ProcessThread(
            input_path=str(sample_image),
            model_name="u2net",
            output_format=".png",
            potencia=75,
            tile_size=512,
            post_processing_opts={
                "upscale_factor": 0,
                "apply_shadow": False,
                "background_type": None,
                "background_data": None,
            },
        )

    def test_init_creates_temp_dir(self, processor: ProcessThread) -> None:
        assert processor.temp_dir is not None
        assert os.path.exists(processor.temp_dir)

    def test_init_normalizes_output_format(self, sample_image: Path) -> None:
        proc1: ProcessThread = ProcessThread(
            input_path=str(sample_image),
            model_name="u2net",
            output_format="png",
            potencia=75,
            tile_size=512,
            post_processing_opts={},
        )
        assert proc1.output_format == ".png"

        proc2: ProcessThread = ProcessThread(
            input_path=str(sample_image),
            model_name="u2net",
            output_format=".png",
            potencia=75,
            tile_size=512,
            post_processing_opts={},
        )
        assert proc2.output_format == ".png"

    def test_is_animated_detection_gif(self, temp_dir: Path) -> None:
        gif_path: Path = temp_dir / "test.gif"
        gif_path.touch()

        proc: ProcessThread = ProcessThread(
            input_path=str(gif_path),
            model_name="u2net",
            output_format=".gif",
            potencia=75,
            tile_size=512,
            post_processing_opts={},
        )
        assert proc.is_animated is True

    def test_is_animated_detection_mp4(self, temp_dir: Path) -> None:
        mp4_path: Path = temp_dir / "test.mp4"
        mp4_path.touch()

        proc: ProcessThread = ProcessThread(
            input_path=str(mp4_path),
            model_name="u2net",
            output_format=".mp4",
            potencia=75,
            tile_size=512,
            post_processing_opts={},
        )
        assert proc.is_animated is True

    def test_is_animated_detection_static(self, sample_image: Path) -> None:
        proc: ProcessThread = ProcessThread(
            input_path=str(sample_image),
            model_name="u2net",
            output_format=".png",
            potencia=75,
            tile_size=512,
            post_processing_opts={},
        )
        assert proc.is_animated is False

    def test_cleanup_removes_temp_dir(self, processor: ProcessThread) -> None:
        temp_dir: str = processor.temp_dir
        assert os.path.exists(temp_dir)

        processor.cleanup()
        assert not os.path.exists(temp_dir)

    def test_run_command_success(self, processor: ProcessThread) -> None:
        result: bool = processor.run_command(["echo", "test"])
        assert result is True

    def test_run_command_failure(self, processor: ProcessThread) -> None:
        result: bool = processor.run_command(["false"])
        assert result is False

    def test_run_command_not_found(self, processor: ProcessThread) -> None:
        result: bool = processor.run_command(["nonexistent_command_12345"])
        assert result is False

    def test_run_command_filters_none(self, processor: ProcessThread) -> None:
        result: bool = processor.run_command(["echo", None, "test", None])
        assert result is True

    def test_video_extensions_tuple(self, processor: ProcessThread) -> None:
        assert isinstance(VIDEO_EXTENSIONS, tuple)
        assert ".gif" in VIDEO_EXTENSIONS
        assert ".mp4" in VIDEO_EXTENSIONS
        assert ".mov" in VIDEO_EXTENSIONS

    def test_post_processing_opts_stored(self, processor: ProcessThread) -> None:
        assert processor.post_processing_opts["upscale_factor"] == 0
        assert processor.post_processing_opts["apply_shadow"] is False

    def test_potencia_stored(self, processor: ProcessThread) -> None:
        assert processor.potencia == 75

    def test_tile_size_stored(self, processor: ProcessThread) -> None:
        assert processor.tile_size == 512

    def test_model_name_stored(self, processor: ProcessThread) -> None:
        assert processor.model_name == "u2net"
