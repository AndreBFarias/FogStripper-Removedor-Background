import os
import logging
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal
from config_loader import PATHS

logger = logging.getLogger(__name__)

class ProcessThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, input_path, apply_upscale, model_name, output_format, potencia):
        super().__init__()
        self.input_path = input_path
        self.apply_upscale = apply_upscale
        self.model_name = model_name
        self.output_format = output_format.lower()
        self.potencia = potencia

    def run_command(self, command):
        logger.info(f"Executando: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if result.stdout: logger.info(f"Saída do worker: {result.stdout.strip()}")
        if result.stderr: logger.warning(f"Avisos do worker: {result.stderr.strip()}")

    def run(self):
        renamed_original_path = None
        try:
            if not PATHS:
                raise RuntimeError("Caminhos para os workers não foram carregados. A instalação pode estar corrompida.")

            base_name, original_ext = os.path.splitext(self.input_path)
            renamed_original_path = f"{base_name}_original{original_ext}"
            
            if os.path.exists(renamed_original_path):
                renamed_original_path = f"{base_name}_original_{os.urandom(4).hex()}{original_ext}"
            os.rename(self.input_path, renamed_original_path)

            path_after_rembg = f"{base_name}_temp_rembg.png"
            
            self.progress.emit(10)
            logger.info("Invocando o Reino do Desnudamento...")
            rembg_command = [
                PATHS["PYTHON_REMBG"], PATHS["REMBG_SCRIPT"],
                "--input", renamed_original_path,
                "--output", path_after_rembg,
                "--model", self.model_name,
                "--potencia", str(self.potencia)
            ]
            self.run_command(rembg_command)
            self.progress.emit(50)
            
            final_path = path_after_rembg
            if self.apply_upscale:
                path_after_upscale = f"{base_name}_despido.{self.output_format}"
                logger.info("Invocando o Reino da Ampliação...")
                self.progress.emit(60)
                upscale_command = [
                    PATHS["PYTHON_UPSCALE"], PATHS["UPSCALE_SCRIPT"],
                    "--input", path_after_rembg,
                    "--output", path_after_upscale
                ]
                self.run_command(upscale_command)
                final_path = path_after_upscale
                os.remove(path_after_rembg)
            else:
                 final_path = f"{base_name}_despido.{self.output_format}"
                 os.rename(path_after_rembg, final_path)

            self.progress.emit(100)
            self.finished.emit(final_path)

        except (subprocess.CalledProcessError, RuntimeError) as e:
            error_message = e.stderr if isinstance(e, subprocess.CalledProcessError) else str(e)
            logger.error(f"Um dos reinos falhou ou o mapa está corrompido.\nErro: {error_message}")
            if renamed_original_path and os.path.exists(renamed_original_path):
                 os.rename(renamed_original_path, self.input_path)
            self.finished.emit("")
        except Exception as e:
            logger.error(f"Erro no orquestrador: {e}", exc_info=True)
            if renamed_original_path and os.path.exists(renamed_original_path):
                 os.rename(renamed_original_path, self.input_path)
            self.finished.emit("")
