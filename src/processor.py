import os
import re
import logging
import subprocess
import tempfile
import shutil
import numpy as np
import imageio.v2 as imageio
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal
from config_loader import PATHS
import svg_utils
import imageio_ffmpeg

logger = logging.getLogger(__name__)

class ProcessThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, input_path, model_name, output_format, potencia, tile_size, post_processing_opts):
        super().__init__()
        self.input_path = input_path
        self.model_name = model_name
        self.output_format = output_format if output_format.startswith('.') else f".{output_format}"
        self.potencia = potencia
        self.tile_size = tile_size
        self.post_processing_opts = post_processing_opts
        self.temp_dir = tempfile.mkdtemp(prefix="fogstripper_")
        self.video_extensions = ('.mp4', '.mov', '.avi', '.wmv', '.mkv', '.avchd', '.flv', '.webm', '.m4v', '.divx', '.gif')
        self.is_animated = self.input_path.lower().endswith(self.video_extensions)

    def run_command(self, command):
        logger.info(f"Executando: {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            if result.stdout: logger.info(f"Saída do worker: {result.stdout.strip()}")
            if result.stderr: logger.warning(f"Avisos do worker: {result.stderr.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Worker falhou com código de saída {e.returncode}.")
            if e.stdout:
                logger.error(f"--- Saída Padrão (stdout) do Worker ---:\n{e.stdout.strip()}")
            if e.stderr:
                logger.error(f"--- Saída de Erro (stderr) do Worker ---:\n{e.stderr.strip()}")
            return False
        except FileNotFoundError as e:
            logger.error(f"Comando não encontrado: {e}")
            return False

    def cleanup(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        logger.info(f"Diretório temporário {self.temp_dir} limpo.")

    def run(self):
        final_path = ""
        original_backup_path = None

        base, _ = os.path.splitext(self.input_path)
        clean_base = re.sub(r'\.bak$', '', base)
        final_output_path = f"{clean_base}{self.output_format}"

        try:
            if not PATHS:
                raise RuntimeError("Mapa da Criação (config.json) não foi carregado.")

            input_is_original = not re.search(r'\.bak$', base)
            if input_is_original:
                 original_backup_path = f"{clean_base}.bak{os.path.splitext(self.input_path)[1]}"
                 shutil.move(self.input_path, original_backup_path)
                 logger.info(f"Backup do arquivo original criado em: {original_backup_path}")
                 processing_file = original_backup_path
            else:
                 processing_file = self.input_path

            if self.is_animated:
                final_path = self.process_animation(processing_file, final_output_path)
            else:
                final_path = self.process_static_image(processing_file, final_output_path)

            if final_path and (os.path.exists(final_path) or os.path.isdir(final_path)):
                self.finished.emit(final_path)
            else:
                raise RuntimeError("O artefato final (arquivo ou diretório) não foi gerado.")

        except Exception as e:
            logger.error(f"Erro no orquestrador: {e}", exc_info=True)
            if original_backup_path and os.path.exists(original_backup_path):
                shutil.move(original_backup_path, self.input_path)
                logger.warning(f"Erro detectado. Backup restaurado para: {self.input_path}")
            self.error.emit(str(e))
        finally:
            self.cleanup()

    def process_static_image(self, current_path, final_output_path):
        step_input_path = current_path

        self.progress.emit(10)
        rembg_output = os.path.join(self.temp_dir, "1_rembg_processed.png")
        rembg_cmd = [
            PATHS.get("PYTHON_REMBG"), PATHS.get("REMBG_SCRIPT"),
            "--input", step_input_path, "--output", rembg_output,
            "--model", self.model_name, "--potencia", str(self.potencia)
        ]
        if not self.run_command(rembg_cmd):
            raise RuntimeError("Falha no Reino do Desnudamento.")
        step_input_path = rembg_output
        step_input_path = rembg_output
        self.progress.emit(30)

        if self.post_processing_opts.get("fill_holes"):
            try:
                import cv2

                img = cv2.imread(step_input_path, cv2.IMREAD_UNCHANGED)
                if img is None: raise ValueError("Erro ao ler imagem para fill holes")

                if img.shape[2] == 4:
                    alpha = img[:, :, 3]
                else:
                    alpha = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8) 

                contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                filled_mask = np.zeros_like(alpha)
                cv2.drawContours(filled_mask, contours, -1, 255, -1)

                original_img = cv2.imread(current_path, cv2.IMREAD_UNCHANGED)
                if original_img is None: raise ValueError("Erro ao ler imagem original para fill holes")

                if original_img.shape[:2] != img.shape[:2]:
                    original_img = cv2.resize(original_img, (img.shape[1], img.shape[0]))

                if original_img.shape[2] == 3:
                    original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2BGRA)

                holes_mask = (filled_mask > 0) & (alpha < 10)

                img[holes_mask] = original_img[holes_mask]

                cv2.imwrite(step_input_path, img)
                logger.info("Buracos internos preenchidos com sucesso.")

            except Exception as e:
                logger.error(f"Falha ao preencher buracos: {e}")
        else:

            try:
                import cv2
                img = cv2.imread(step_input_path, cv2.IMREAD_UNCHANGED)
                if img is None: raise ValueError("Erro ao ler imagem para limpeza de ruído")

                if img.shape[2] == 4:
                    alpha = img[:, :, 3]
                    contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    if contours:

                        _, binary = cv2.threshold(alpha, 10, 255, cv2.THRESH_BINARY)

                        kernel = np.ones((5,5), np.uint8)
                        opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

                        opened_contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                        if opened_contours:

                            largest_opened_contour = max(opened_contours, key=cv2.contourArea)

                            main_object_mask = np.zeros_like(alpha)
                            cv2.drawContours(main_object_mask, [largest_opened_contour], -1, 255, -1)

                            dilate_kernel = np.ones((7,7), np.uint8)
                            main_object_mask = cv2.dilate(main_object_mask, dilate_kernel, iterations=1)

                            new_alpha = cv2.bitwise_and(alpha, main_object_mask)

                            img[:, :, 3] = new_alpha
                            cv2.imwrite(step_input_path, img)
                            logger.info("Ruídos externos removidos com Morphological Opening.")
                        else:

                             largest_contour = max(contours, key=cv2.contourArea)
                             mask = np.zeros_like(alpha)
                             cv2.drawContours(mask, [largest_contour], -1, 255, -1)
                             new_alpha = cv2.bitwise_and(alpha, mask)
                             img[:, :, 3] = new_alpha
                             cv2.imwrite(step_input_path, img)
                             logger.info("Ruídos externos removidos (fallback padrão).")

            except Exception as e:
                logger.error(f"Falha ao limpar ruídos externos: {e}")

        if self.post_processing_opts.get("crop_option") == 'trim':
            try:
                with Image.open(step_input_path) as img:
                    img = img.convert("RGBA")

                    data = np.array(img)
                    alpha = data[:, :, 3]

                    rows = np.any(alpha > 15, axis=1)
                    cols = np.any(alpha > 15, axis=0)

                    if rows.any() and cols.any():
                        ymin, ymax = np.where(rows)[0][[0, -1]]
                        xmin, xmax = np.where(cols)[0][[0, -1]]

                        margin = 0
                        ymin = max(0, ymin - margin)
                        ymax = min(img.height, ymax + 1 + margin)
                        xmin = max(0, xmin - margin)
                        xmax = min(img.width, xmax + 1 + margin)

                        cropped_img = img.crop((xmin, ymin, xmax, ymax))
                        cropped_img.save(step_input_path)
                        logger.info(f"Imagem recortada (Trim) com sucesso. Novo tamanho: {cropped_img.size}")
                    else:
                        logger.warning("Imagem vazia ou totalmente transparente após threshold.")
            except Exception as e:
                logger.error(f"Falha ao recortar imagem: {e}")

        upscale_factor = self.post_processing_opts.get("upscale_factor", 0)
        if upscale_factor > 0:
            upscale_output = os.path.join(self.temp_dir, "2_upscaled.png")
            upscale_cmd = [
                PATHS.get("PYTHON_UPSCALE"), PATHS.get("UPSCALE_SCRIPT"),
                "--input", step_input_path, "--output", upscale_output,
                "--tile", str(self.tile_size), "--outscale", str(upscale_factor)
            ]
            if not self.run_command(upscale_cmd):
                raise RuntimeError("Falha no Reino da Ampliação.")
            step_input_path = upscale_output
        self.progress.emit(50)

        if self.post_processing_opts.get("enabled"):
            if self.post_processing_opts.get("shadow_enabled"):
                shadow_output = os.path.join(self.temp_dir, "3_shadow_effect.png")
                effects_cmd = [
                    PATHS.get("PYTHON_REMBG"), PATHS.get("EFFECTS_SCRIPT"),
                    "--input", step_input_path,
                    "--output", shadow_output
                ]
                if not self.run_command(effects_cmd):
                    raise RuntimeError("Falha no Altar das Sombras.")
                step_input_path = shadow_output
            self.progress.emit(70)

            bg_type = self.post_processing_opts.get("background_type")
            bg_data = self.post_processing_opts.get("background_data")
            if bg_type and bg_data:
                background_output = os.path.join(self.temp_dir, f"4_background{self.output_format}")
                background_cmd = [
                    PATHS.get("PYTHON_REMBG"), PATHS.get("BACKGROUND_SCRIPT"),
                    "--input", step_input_path,
                    "--output", background_output,
                    "--bg-type", bg_type,
                    "--bg-data", bg_data,
                    "--resize-mode", self.post_processing_opts.get("background_resize_mode")
                ]
                if not self.run_command(background_cmd):
                    raise RuntimeError("Falha no Altar dos Fundos.")
                step_input_path = background_output
            self.progress.emit(90)

        if self.output_format == '.svg':
            if svg_utils.raster_to_svg(step_input_path, final_output_path):
                 self.progress.emit(100)
                 return final_output_path
            else:

                 logger.warning("SVG generation failed, saving as PNG instead.")
                 final_output_path = os.path.splitext(final_output_path)[0] + ".png"
                 shutil.move(step_input_path, final_output_path)
        else:
            shutil.move(step_input_path, final_output_path)

        self.progress.emit(100)
        return final_output_path

    def process_animation(self, current_path, final_output_path):
        logger.info("Invocando o Reino do Desnudamento para animação...")

        reader = imageio.get_reader(current_path)
        try:
            meta_data = reader.get_meta_data()
            fps = meta_data.get('fps', None)
            if fps is None:
                duration = meta_data.get('duration', 100) / 1000
                fps = 1 / duration if duration > 0 else 10
            frames = [frame for frame in reader]
        finally:
            reader.close()

        num_frames = len(frames)
        purified_frames = []

        for i, frame in enumerate(frames):
            frame_path = os.path.join(self.temp_dir, f"frame_{i:04d}.png")
            Image.fromarray(frame).convert("RGBA").save(frame_path)

            processed_frame_path = os.path.join(self.temp_dir, f"processed_frame_{i:04d}.png")
            rembg_cmd = [
                PATHS.get("PYTHON_REMBG"), PATHS.get("REMBG_SCRIPT"),
                "--input", frame_path, "--output", processed_frame_path,
                "--model", self.model_name, "--potencia", str(self.potencia)
            ]
            if not self.run_command(rembg_cmd):
                raise RuntimeError(f"Falha ao processar o quadro {i}.")

            with Image.open(processed_frame_path) as processed_img:
                processed_img = processed_img.convert("RGBA")
                purified_canvas = Image.new("RGBA", processed_img.size, (0, 0, 0, 0))
                purified_canvas.paste(processed_img, (0, 0), processed_img)
                purified_frames.append(purified_canvas)

            self.progress.emit(int((i + 1) / num_frames * 90))

        if self.output_format in ['.png', '.svg']:
            output_dir = os.path.splitext(final_output_path)[0]
            logger.info(f"Desmembrando animação em quadros estáticos em: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
            for i, p_frame in enumerate(purified_frames):
                temp_save_path = os.path.join(output_dir, f"frame_{i:04d}.png")
                p_frame.save(temp_save_path)

                final_frame_path = os.path.join(output_dir, f"frame_{i:04d}{self.output_format}")

                if temp_save_path != final_frame_path:
                    shutil.move(temp_save_path, final_frame_path)

            self.progress.emit(100)
            return output_dir
        else:
            logger.info(f"Reconstruindo animação em {final_output_path}")
            np_frames = [np.array(p_frame) for p_frame in purified_frames]

            if final_output_path.lower().endswith('.webm'):
                imageio.mimsave(final_output_path, np_frames, fps=fps, codec='libvpx-vp9', pixelformat='yuva420p', quality=8)
            else: 
                imageio.mimsave(final_output_path, np_frames, fps=fps, loop=0, disposal=2)

            self.progress.emit(100)
            return final_output_path
