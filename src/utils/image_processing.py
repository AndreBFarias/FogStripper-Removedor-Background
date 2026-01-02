import logging
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

logger: logging.Logger = logging.getLogger(__name__)


def fill_internal_holes(processed_path: str, original_path: str) -> bool:
    try:
        img = cv2.imread(processed_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError("Erro ao ler imagem processada")

        if img.shape[2] == 4:
            alpha = img[:, :, 3]
        else:
            alpha = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)

        contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled_mask = np.zeros_like(alpha)
        cv2.drawContours(filled_mask, contours, -1, 255, -1)

        original_img = cv2.imread(original_path, cv2.IMREAD_UNCHANGED)
        if original_img is None:
            raise ValueError("Erro ao ler imagem original")

        if original_img.shape[:2] != img.shape[:2]:
            original_img = cv2.resize(original_img, (img.shape[1], img.shape[0]))

        if original_img.shape[2] == 3:
            original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2BGRA)

        holes_mask = (filled_mask > 0) & (alpha < 10)
        img[holes_mask] = original_img[holes_mask]
        cv2.imwrite(processed_path, img)
        logger.info("Buracos internos preenchidos com sucesso.")
        return True

    except Exception as e:
        logger.error(f"Falha ao preencher buracos: {e}")
        return False


def remove_external_noise(image_path: str) -> bool:
    try:
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError("Erro ao ler imagem")

        if img.shape[2] != 4:
            return True

        alpha = img[:, :, 3]
        contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return True

        _, binary = cv2.threshold(alpha, 10, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5, 5), np.uint8)
        opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        opened_contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if opened_contours:
            largest = max(opened_contours, key=cv2.contourArea)
            mask = np.zeros_like(alpha)
            cv2.drawContours(mask, [largest], -1, 255, -1)
            dilate_kernel = np.ones((7, 7), np.uint8)
            mask = cv2.dilate(mask, dilate_kernel, iterations=1)
        else:
            largest = max(contours, key=cv2.contourArea)
            mask = np.zeros_like(alpha)
            cv2.drawContours(mask, [largest], -1, 255, -1)

        img[:, :, 3] = cv2.bitwise_and(alpha, mask)
        cv2.imwrite(image_path, img)
        logger.info("Ruidos externos removidos.")
        return True

    except Exception as e:
        logger.error(f"Falha ao limpar ruidos: {e}")
        return False


def trim_to_content(image_path: str, threshold: int = 15) -> bool:
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            data = np.array(img)
            alpha = data[:, :, 3]

            rows = np.any(alpha > threshold, axis=1)
            cols = np.any(alpha > threshold, axis=0)

            if not (rows.any() and cols.any()):
                logger.warning("Imagem vazia ou totalmente transparente.")
                return False

            ymin, ymax = np.where(rows)[0][[0, -1]]
            xmin, xmax = np.where(cols)[0][[0, -1]]

            cropped = img.crop((xmin, ymin, xmax + 1, ymax + 1))
            cropped.save(image_path)
            logger.info(f"Imagem recortada. Novo tamanho: {cropped.size}")
            return True

    except Exception as e:
        logger.error(f"Falha ao recortar imagem: {e}")
        return False
