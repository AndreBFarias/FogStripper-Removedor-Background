from pathlib import Path

import pytest
from PIL import Image

from src.utils.svg_utils import raster_to_svg


class TestRasterToSvg:
    def test_basic_conversion(self, sample_image: Path, temp_dir: Path) -> None:
        output_path: Path = temp_dir / "output.svg"
        result: bool = raster_to_svg(str(sample_image), str(output_path))

        assert result is True
        assert output_path.exists()
        content: str = output_path.read_text()
        assert "<svg" in content
        assert "</svg>" in content

    def test_svg_contains_dimensions(self, sample_image: Path, temp_dir: Path) -> None:
        output_path: Path = temp_dir / "output.svg"
        raster_to_svg(str(sample_image), str(output_path))

        content: str = output_path.read_text()
        assert 'width="100"' in content
        assert 'height="100"' in content

    def test_conversion_with_transparency(self, sample_image_with_transparency: Path, temp_dir: Path) -> None:
        output_path: Path = temp_dir / "output.svg"
        result: bool = raster_to_svg(str(sample_image_with_transparency), str(output_path))

        assert result is True
        assert output_path.exists()

    def test_custom_num_colors(self, sample_image: Path, temp_dir: Path) -> None:
        output_path: Path = temp_dir / "output.svg"
        result: bool = raster_to_svg(str(sample_image), str(output_path), num_colors=4)

        assert result is True
        assert output_path.exists()

    def test_invalid_input_path(self, temp_dir: Path) -> None:
        output_path: Path = temp_dir / "output.svg"
        result: bool = raster_to_svg("/nonexistent/image.png", str(output_path))

        assert result is False

    def test_rgb_image_without_alpha(self, temp_dir: Path) -> None:
        img_path: Path = temp_dir / "rgb_image.png"
        img: Image.Image = Image.new("RGB", (50, 50), (0, 255, 0))
        img.save(img_path)

        output_path: Path = temp_dir / "output.svg"
        result: bool = raster_to_svg(str(img_path), str(output_path))

        assert result is True
        assert output_path.exists()

    def test_svg_contains_paths(self, sample_image: Path, temp_dir: Path) -> None:
        output_path: Path = temp_dir / "output.svg"
        raster_to_svg(str(sample_image), str(output_path))

        content: str = output_path.read_text()
        assert "<path" in content
        assert 'fill="#' in content
