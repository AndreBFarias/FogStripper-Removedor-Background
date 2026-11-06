import os
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image


class TestWorkerBackground:
    def test_color_background(self, sample_image_with_transparency: Path, temp_dir: Path) -> None:
        output_path: Path = temp_dir / "output.png"
        worker_path: str = str(Path(__file__).parent.parent / "workers" / "worker_background.py")

        result = subprocess.run(
            [
                sys.executable,
                worker_path,
                "--input",
                str(sample_image_with_transparency),
                "--output",
                str(output_path),
                "--bg-type",
                "color",
                "--bg-data",
                "#FF0000",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output_path.exists()

        with Image.open(output_path) as img:
            assert img.size == (100, 100)

    def test_image_background_fit_bg_to_fg(
        self,
        sample_image_with_transparency: Path,
        background_image: Path,
        temp_dir: Path,
    ) -> None:
        output_path: Path = temp_dir / "output.png"
        worker_path: str = str(Path(__file__).parent.parent / "workers" / "worker_background.py")

        result = subprocess.run(
            [
                sys.executable,
                worker_path,
                "--input",
                str(sample_image_with_transparency),
                "--output",
                str(output_path),
                "--bg-type",
                "image",
                "--bg-data",
                str(background_image),
                "--resize-mode",
                "fit-bg-to-fg",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output_path.exists()


class TestWorkerEffects:
    def test_shadow_effect(self, sample_image_with_transparency: Path, temp_dir: Path) -> None:
        output_path: Path = temp_dir / "output.png"
        worker_path: str = str(Path(__file__).parent.parent / "workers" / "worker_effects.py")

        result = subprocess.run(
            [
                sys.executable,
                worker_path,
                "--input",
                str(sample_image_with_transparency),
                "--output",
                str(output_path),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output_path.exists()

        with Image.open(output_path) as img:
            assert img.width > 100
            assert img.height > 100


class TestWorkerRembg:
    @pytest.mark.slow
    def test_background_removal(self, sample_image: Path, temp_dir: Path) -> None:
        output_path: Path = temp_dir / "output.png"
        worker_path: str = str(Path(__file__).parent.parent / "workers" / "worker_rembg.py")

        result = subprocess.run(
            [
                sys.executable,
                worker_path,
                "--input",
                str(sample_image),
                "--output",
                str(output_path),
                "--model",
                "u2net",
                "--potencia",
                "75",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            assert output_path.exists()


class TestWorkerUpscale:
    @pytest.mark.slow
    def test_upscale(self, sample_image: Path, temp_dir: Path) -> None:
        output_path: Path = temp_dir / "output.png"
        worker_path: str = str(Path(__file__).parent.parent / "workers" / "worker_upscale.py")

        result = subprocess.run(
            [
                sys.executable,
                worker_path,
                "--input",
                str(sample_image),
                "--output",
                str(output_path),
                "--tile",
                "256",
                "--outscale",
                "2",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            assert output_path.exists()
            with Image.open(output_path) as img:
                assert img.width == 200
                assert img.height == 200


class TestRembgModelsDir:
    def test_default_models_dir_is_inside_project(self) -> None:
        project_root: Path = Path(__file__).resolve().parents[2]
        check: str = (
            "import runpy, sys; sys.modules['rembg'] = __import__('types').SimpleNamespace(new_session=None, remove=None); "
            "m = runpy.run_path('src/workers/worker_rembg.py', run_name='prova'); print(m['_MODELS_DIR'])"
        )
        env: dict[str, str] = {k: v for k, v in os.environ.items() if k != "U2NET_HOME"}
        result = subprocess.run(
            [sys.executable, "-c", check], capture_output=True, text=True, check=True, cwd=project_root, env=env
        )
        assert Path(result.stdout.strip()) == project_root / "models" / "u2net"
