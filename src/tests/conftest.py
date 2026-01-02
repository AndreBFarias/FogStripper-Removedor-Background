import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    dirpath: Path = Path(tempfile.mkdtemp())
    yield dirpath
    shutil.rmtree(dirpath, ignore_errors=True)


@pytest.fixture
def sample_image(temp_dir: Path) -> Path:
    img_path: Path = temp_dir / "sample.png"
    img: Image.Image = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_image_with_transparency(temp_dir: Path) -> Path:
    img_path: Path = temp_dir / "transparent.png"
    img: Image.Image = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    for x in range(25, 75):
        for y in range(25, 75):
            img.putpixel((x, y), (255, 0, 0, 255))
    img.save(img_path)
    return img_path


@pytest.fixture
def background_image(temp_dir: Path) -> Path:
    img_path: Path = temp_dir / "background.png"
    img: Image.Image = Image.new("RGBA", (200, 200), (0, 0, 255, 255))
    img.save(img_path)
    return img_path


@pytest.fixture(autouse=True)
def change_to_temp_dir(temp_dir: Path) -> Generator[None, None, None]:
    original_dir: str = os.getcwd()
    yield
    os.chdir(original_dir)
