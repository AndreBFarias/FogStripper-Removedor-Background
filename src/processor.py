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
        self.is_animated = self.input_path.lower().endswith(('.gif', '.webm'))

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

        # --- FILL HOLES LOGIC ---
        if self.post_processing_opts.get("fill_holes"):
            try:
                import cv2
                
                # Load current result (with holes)
                img = cv2.imread(step_input_path, cv2.IMREAD_UNCHANGED)
                if img is None: raise ValueError("Erro ao ler imagem para fill holes")
                
                # Extract alpha
                if img.shape[2] == 4:
                    alpha = img[:, :, 3]
                else:
                    alpha = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8) # Should not happen

                # Find external contours
                contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Create a mask of the "filled" object (silhouette)
                filled_mask = np.zeros_like(alpha)
                cv2.drawContours(filled_mask, contours, -1, 255, -1)
                
                # Identify the "holes" (pixels that are in filled_mask but NOT in original alpha)
                # holes_mask = filled_mask - alpha (roughly)
                # We want to restore pixels where filled_mask is 255 but alpha is 0 (or low)
                
                # Load ORIGINAL image to get the colors for the holes
                # We use the backup if available, or the input path
                # Note: self.input_path might be the backup if we moved it.
                # Let's use the 'original_backup_path' logic from run() but we don't have access to it here easily.
                # However, step_input_path was derived from current_path which IS the original (or backup).
                # Wait, step_input_path is now rembg_output.
                # 'current_path' passed to this function IS the source image (RGB).
                
                original_img = cv2.imread(current_path, cv2.IMREAD_UNCHANGED)
                if original_img is None: raise ValueError("Erro ao ler imagem original para fill holes")
                
                # Resize original if needed (should match, but just in case)
                if original_img.shape[:2] != img.shape[:2]:
                    original_img = cv2.resize(original_img, (img.shape[1], img.shape[0]))

                # Ensure original has alpha
                if original_img.shape[2] == 3:
                    original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2BGRA)

                # Composite:
                # Final pixel = Original Pixel if filled_mask is 255
                #             = Transparent if filled_mask is 0
                
                # Actually, we want to keep the 'rembg' result for the edges (antialiasing), 
                # but force opacity in the middle.
                # So: New Alpha = max(Old Alpha, Filled Mask)
                # But if we just set alpha to 255, we might lose the color if rembg made it black/transparent.
                # So we must copy color from original where we are filling.
                
                # Where filled_mask is 255:
                #   If alpha was already high, keep it (rembg result).
                #   If alpha was low (hole), restore from original.
                
                # Let's define "Hole" as: filled_mask > 0 AND alpha < 255
                # But rembg has semi-transparent edges. We don't want to make edges hard.
                # We only want to fill "internal" holes.
                
                # A simple approach:
                # 1. Create a "Hole Mask": (filled_mask > 0) & (alpha == 0)
                # 2. Copy pixels from original to result where Hole Mask is true.
                
                # Better: Use the filled_mask as the alpha for the original image?
                # No, that would undo rembg's edge detection and just give a hard silhouette.
                
                # We want to fill *enclosed* transparent regions.
                # The 'filled_mask' represents the solid object.
                # If we use 'filled_mask' to copy from original, we get the solid object with original colors.
                # But we lose the soft edges from rembg?
                # No, because 'filled_mask' is binary (hard edges).
                
                # Strategy:
                # 1. Find holes explicitly.
                #    Holes are contours in the INVERTED alpha?
                #    Or just: filled_mask - alpha.
                
                # Let's use the simple composite:
                # Result = Rembg_Result + (Original masked by Holes)
                
                # Define Holes:
                # Pixels where filled_mask is 255 AND alpha is low (e.g. < 10).
                # We leave the semi-transparent edges alone.
                
                holes_mask = (filled_mask > 0) & (alpha < 10)
                
                # Update result image
                # Where holes_mask is true, set pixel to original_img pixel
                img[holes_mask] = original_img[holes_mask]
                
                # Save
                cv2.imwrite(step_input_path, img)
                logger.info("Buracos internos preenchidos com sucesso.")
                
            except Exception as e:
                logger.error(f"Falha ao preencher buracos: {e}")
        else:
            # --- KEEP LARGEST COMPONENT LOGIC (Remove External Noise) ---
            try:
                import cv2
                img = cv2.imread(step_input_path, cv2.IMREAD_UNCHANGED)
                if img is None: raise ValueError("Erro ao ler imagem para limpeza de ruído")
                
                if img.shape[2] == 4:
                    alpha = img[:, :, 3]
                    contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    if contours:
                        # Use morphological opening to separate weakly connected artifacts (like reflections)
                        # Threshold alpha to binary
                        _, binary = cv2.threshold(alpha, 10, 255, cv2.THRESH_BINARY)
                        
                        # Morphological Open (Erode -> Dilate)
                        # This removes small connections
                        kernel = np.ones((5,5), np.uint8)
                        opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
                        
                        # Find contours on the OPENED image
                        opened_contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        
                        if opened_contours:
                            # Find largest contour in the opened image
                            largest_opened_contour = max(opened_contours, key=cv2.contourArea)
                            
                            # Create a mask for the main object based on the opened contour
                            # We dilate it back slightly to ensure we cover the original object edges
                            # or we can just use it as a region of interest.
                            
                            # Better approach:
                            # 1. Create a mask from the largest opened contour.
                            # 2. Dilate this mask to cover the original object (undo erosion).
                            # 3. Use this mask to keep pixels from the original alpha.
                            
                            main_object_mask = np.zeros_like(alpha)
                            cv2.drawContours(main_object_mask, [largest_opened_contour], -1, 255, -1)
                            
                            # Dilate to recover edges lost during opening
                            # We use a slightly larger kernel than the opening one to be safe
                            dilate_kernel = np.ones((7,7), np.uint8)
                            main_object_mask = cv2.dilate(main_object_mask, dilate_kernel, iterations=1)
                            
                            # Apply this mask to the ORIGINAL alpha
                            # This keeps the main object (and its original edges) but removes
                            # anything that was separated by the opening and not part of the main blob.
                            
                            new_alpha = cv2.bitwise_and(alpha, main_object_mask)
                            
                            img[:, :, 3] = new_alpha
                            cv2.imwrite(step_input_path, img)
                            logger.info("Ruídos externos removidos com Morphological Opening.")
                        else:
                             # Fallback to standard contour if opening removed everything (unlikely)
                             largest_contour = max(contours, key=cv2.contourArea)
                             mask = np.zeros_like(alpha)
                             cv2.drawContours(mask, [largest_contour], -1, 255, -1)
                             new_alpha = cv2.bitwise_and(alpha, mask)
                             img[:, :, 3] = new_alpha
                             cv2.imwrite(step_input_path, img)
                             logger.info("Ruídos externos removidos (fallback padrão).")
                        

            except Exception as e:
                logger.error(f"Falha ao limpar ruídos externos: {e}")
        # -------------------------

        # --- TRIM / CROP LOGIC ---
        if self.post_processing_opts.get("crop_option") == 'trim':
            try:
                with Image.open(step_input_path) as img:
                    img = img.convert("RGBA")
                    # Use numpy to find bounding box with threshold
                    # This avoids noise (low alpha pixels) preventing a good crop
                    data = np.array(img)
                    alpha = data[:, :, 3]
                    # Threshold: pixels with alpha < 15 are considered transparent
                    rows = np.any(alpha > 15, axis=1)
                    cols = np.any(alpha > 15, axis=0)
                    
                    if rows.any() and cols.any():
                        ymin, ymax = np.where(rows)[0][[0, -1]]
                        xmin, xmax = np.where(cols)[0][[0, -1]]
                        
                        # Add a small padding (margin) if desired, e.g. 10px
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
        # -------------------------

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
                 # Fallback to PNG if SVG fails, or just error? 
                 # Let's fallback to moving the raster file but rename to .png?
                 # Or just fail. The logger handles the error.
                 # If it failed, maybe we should just save as PNG?
                 # For now, let's assume if it returns False it logged why.
                 # We can try to save as PNG as fallback if user really wants the file.
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
            else: # GIF
                imageio.mimsave(final_output_path, np_frames, fps=fps, loop=0, disposal=2)

            self.progress.emit(100)
            return final_output_path

