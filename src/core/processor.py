import logging
import os
import re
import shutil
import subprocess
import tempfile
from typing import Any

import imageio.v2 as imageio
import numpy as np
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal

from src.core.config_loader import PATHS
from src.core.constants import VIDEO_EXTENSIONS
from src.utils import svg_utils
from src.utils.image_processing import fill_internal_holes, remove_external_noise, trim_to_content

logger: logging.Logger = logging.getLogger(__name__)


class ProcessThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(
        self,
        input_path: str,
        model_name: str,
        output_format: str,
        potencia: int,
        tile_size: int,
        post_processing_opts: dict[str, Any],
    ) -> None:
        super().__init__()
        self.input_path: str = input_path
        self.model_name: str = model_name
        self.output_format: str = output_format if output_format.startswith(".") else f".{output_format}"
        self.potencia: int = potencia
        self.tile_size: int = tile_size
        self.post_processing_opts: dict[str, Any] = post_processing_opts
        self.temp_dir: str = tempfile.mkdtemp(prefix="fogstripper_")
        self.is_animated: bool = self.input_path.lower().endswith(VIDEO_EXTENSIONS)

    def run_command(self, command: list[str | None]) -> bool:
        cmd: list[str] = [c for c in command if c is not None]
        logger.info(f"Executando: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding="utf-8")
            if result.stdout:
                logger.info(f"Saida do worker: {result.stdout.strip()}")
            if result.stderr:
                logger.warning(f"Avisos do worker: {result.stderr.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Worker falhou com codigo {e.returncode}.")
            if e.stdout:
                logger.error(f"stdout: {e.stdout.strip()}")
            if e.stderr:
                logger.error(f"stderr: {e.stderr.strip()}")
            return False
        except FileNotFoundError as e:
            logger.error(f"Comando nao encontrado: {e}")
            return False

    def cleanup(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        logger.info(f"Diretorio temporario {self.temp_dir} limpo.")

    def run(self) -> None:
        final_path: str = ""
        original_backup_path: str | None = None

        base, _ = os.path.splitext(self.input_path)
        clean_base: str = re.sub(r"\.bak$", "", base)
        final_output_path: str = f"{clean_base}{self.output_format}"

        try:
            if not PATHS:
                raise RuntimeError("Arquivo de configuracao (config.json) nao foi carregado.")

            input_is_original: bool = not re.search(r"\.bak$", base)
            if input_is_original:
                original_backup_path = f"{clean_base}.bak{os.path.splitext(self.input_path)[1]}"
                shutil.move(self.input_path, original_backup_path)
                logger.info(f"Backup criado: {original_backup_path}")
                processing_file: str = original_backup_path
            else:
                processing_file = self.input_path

            if self.is_animated:
                final_path = self._process_animation(processing_file, final_output_path)
            else:
                final_path = self._process_static_image(processing_file, final_output_path)

            if final_path and (os.path.exists(final_path) or os.path.isdir(final_path)):
                self.finished.emit(final_path)
            else:
                raise RuntimeError("Artefato final nao gerado.")

        except Exception as e:
            logger.error(f"Erro no orquestrador: {e}", exc_info=True)
            if original_backup_path and os.path.exists(original_backup_path):
                shutil.move(original_backup_path, self.input_path)
                logger.warning(f"Backup restaurado: {self.input_path}")
            self.error.emit(str(e))
        finally:
            self.cleanup()

    def _run_rembg(self, input_path: str, output_path: str) -> bool:
        cmd: list[str | None] = [
            PATHS.get("PYTHON_REMBG"),
            PATHS.get("REMBG_SCRIPT"),
            "--input",
            input_path,
            "--output",
            output_path,
            "--model",
            self.model_name,
            "--potencia",
            str(self.potencia),
        ]
        return self.run_command(cmd)

    def _run_upscale(self, input_path: str, output_path: str, factor: int) -> bool:
        cmd: list[str | None] = [
            PATHS.get("PYTHON_UPSCALE"),
            PATHS.get("UPSCALE_SCRIPT"),
            "--input",
            input_path,
            "--output",
            output_path,
            "--tile",
            str(self.tile_size),
            "--outscale",
            str(factor),
        ]
        return self.run_command(cmd)

    def _run_effects(self, input_path: str, output_path: str) -> bool:
        cmd: list[str | None] = [
            PATHS.get("PYTHON_REMBG"),
            PATHS.get("EFFECTS_SCRIPT"),
            "--input",
            input_path,
            "--output",
            output_path,
        ]
        return self.run_command(cmd)

    def _run_background(self, input_path: str, output_path: str) -> bool:
        cmd: list[str | None] = [
            PATHS.get("PYTHON_REMBG"),
            PATHS.get("BACKGROUND_SCRIPT"),
            "--input",
            input_path,
            "--output",
            output_path,
            "--bg-type",
            self.post_processing_opts.get("background_type"),
            "--bg-data",
            self.post_processing_opts.get("background_data"),
            "--resize-mode",
            self.post_processing_opts.get("background_resize_mode"),
        ]
        return self.run_command(cmd)

    def _process_static_image(self, current_path: str, final_output_path: str) -> str:
        step_path: str = current_path

        self.progress.emit(10)
        rembg_output: str = os.path.join(self.temp_dir, "1_rembg.png")
        if not self._run_rembg(step_path, rembg_output):
            raise RuntimeError("Falha na remocao de fundo.")
        step_path = rembg_output
        self.progress.emit(30)

        if self.post_processing_opts.get("fill_holes"):
            fill_internal_holes(step_path, current_path)
        else:
            remove_external_noise(step_path)

        if self.post_processing_opts.get("crop_option") == "trim":
            trim_to_content(step_path)

        upscale_factor: int = self.post_processing_opts.get("upscale_factor", 0)
        if upscale_factor > 0:
            upscale_output: str = os.path.join(self.temp_dir, "2_upscaled.png")
            if not self._run_upscale(step_path, upscale_output, upscale_factor):
                raise RuntimeError("Falha no upscale.")
            step_path = upscale_output
        self.progress.emit(50)

        if self.post_processing_opts.get("enabled"):
            if self.post_processing_opts.get("shadow_enabled"):
                shadow_output: str = os.path.join(self.temp_dir, "3_shadow.png")
                if not self._run_effects(step_path, shadow_output):
                    raise RuntimeError("Falha ao aplicar sombra.")
                step_path = shadow_output
            self.progress.emit(70)

            bg_type = self.post_processing_opts.get("background_type")
            bg_data = self.post_processing_opts.get("background_data")
            if bg_type and bg_data:
                bg_output: str = os.path.join(self.temp_dir, f"4_background{self.output_format}")
                if not self._run_background(step_path, bg_output):
                    raise RuntimeError("Falha ao aplicar fundo.")
                step_path = bg_output
            self.progress.emit(90)

        if self.output_format == ".svg":
            if svg_utils.raster_to_svg(step_path, final_output_path):
                self.progress.emit(100)
                return final_output_path
            else:
                logger.warning("SVG falhou, salvando como PNG.")
                final_output_path = os.path.splitext(final_output_path)[0] + ".png"

        shutil.move(step_path, final_output_path)
        self.progress.emit(100)
        return final_output_path

    def _process_animation(self, current_path: str, final_output_path: str) -> str:
        logger.info("Processando animacao...")

        reader = imageio.get_reader(current_path)
        try:
            meta: dict[str, Any] = reader.get_meta_data()
            fps: float = meta.get("fps") or (1000 / meta.get("duration", 100))
            frames: list[np.ndarray] = list(reader)
        finally:
            reader.close()

        num_frames: int = len(frames)
        processed_frames: list[Image.Image] = []

        for i, frame in enumerate(frames):
            frame_path: str = os.path.join(self.temp_dir, f"frame_{i:04d}.png")
            Image.fromarray(frame).convert("RGBA").save(frame_path)

            out_path: str = os.path.join(self.temp_dir, f"proc_{i:04d}.png")
            if not self._run_rembg(frame_path, out_path):
                raise RuntimeError(f"Falha no quadro {i}.")

            with Image.open(out_path) as img:
                canvas = Image.new("RGBA", img.size, (0, 0, 0, 0))
                canvas.paste(img.convert("RGBA"), (0, 0), img.convert("RGBA"))
                processed_frames.append(canvas)

            self.progress.emit(int((i + 1) / num_frames * 90))

        if self.output_format in [".png", ".svg"]:
            output_dir: str = os.path.splitext(final_output_path)[0]
            os.makedirs(output_dir, exist_ok=True)
            for i, pf in enumerate(processed_frames):
                pf.save(os.path.join(output_dir, f"frame_{i:04d}{self.output_format}"))
            self.progress.emit(100)
            return output_dir

        np_frames = [np.array(pf) for pf in processed_frames]
        if final_output_path.lower().endswith(".webm"):
            imageio.mimsave(
                final_output_path, np_frames, fps=fps, codec="libvpx-vp9", pixelformat="yuva420p", quality=8
            )
        else:
            imageio.mimsave(final_output_path, np_frames, fps=fps, loop=0, disposal=2)

        self.progress.emit(100)
        return final_output_path
