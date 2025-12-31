import os
from pathlib import Path

import pytest
from PIL import Image

from src.utils.icon_resizer import resize_icon


class TestIconResizer:
    def test_resize_single_size(self, sample_image: Path, temp_dir: Path) -> None:
        output_dir: Path = temp_dir / "output"
        resize_icon(str(sample_image), str(output_dir), [32])

        output_file: Path = output_dir / "icon_32x32.png"
        assert output_file.exists()

        with Image.open(output_file) as img:
            assert img.size == (32, 32)

    def test_resize_multiple_sizes(self, sample_image: Path, temp_dir: Path) -> None:
        output_dir: Path = temp_dir / "output"
        sizes: list[int] = [16, 32, 64, 128]
        resize_icon(str(sample_image), str(output_dir), sizes)

        for size in sizes:
            output_file: Path = output_dir / f"icon_{size}x{size}.png"
            assert output_file.exists()

            with Image.open(output_file) as img:
                assert img.size == (size, size)

    def test_creates_output_directory(self, sample_image: Path, temp_dir: Path) -> None:
        output_dir: Path = temp_dir / "nested" / "output" / "dir"
        assert not output_dir.exists()

        resize_icon(str(sample_image), str(output_dir), [32])

        assert output_dir.exists()

    def test_preserves_rgba(self, sample_image_with_transparency: Path, temp_dir: Path) -> None:
        output_dir: Path = temp_dir / "output"
        resize_icon(str(sample_image_with_transparency), str(output_dir), [32])

        output_file: Path = output_dir / "icon_32x32.png"
        with Image.open(output_file) as img:
            assert img.mode == "RGBA"

    def test_invalid_source_path(self, temp_dir: Path) -> None:
        output_dir: Path = temp_dir / "output"
        with pytest.raises(SystemExit):
            resize_icon("/nonexistent/path.png", str(output_dir), [32])

    def test_empty_sizes_list(self, sample_image: Path, temp_dir: Path) -> None:
        output_dir: Path = temp_dir / "output"
        resize_icon(str(sample_image), str(output_dir), [])

        assert output_dir.exists()
        assert len(list(output_dir.iterdir())) == 0
