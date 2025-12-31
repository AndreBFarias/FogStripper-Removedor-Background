import json
import logging
import os
from typing import Any

logger: logging.Logger = logging.getLogger(__name__)

if os.getenv("FOGSTRIPPER_DEV_MODE"):
    logger.warning("MODO DE DESENVOLVIMENTO ATIVADO!")
    APP_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    CONFIG_PATH: str = os.path.join(APP_DIR, "config.dev.json")
else:
    APP_DIR: str = os.path.expanduser("~/.local/share/fogstripper")
    CONFIG_PATH: str = os.path.join(APP_DIR, "config.json")

PATHS: dict[str, Any] = {}


def load_paths() -> None:
    global PATHS
    try:
        with open(CONFIG_PATH, "r") as f:
            PATHS = json.load(f)
        logger.info(f"Configuracao ({os.path.basename(CONFIG_PATH)}) carregada.")
    except FileNotFoundError:
        logger.critical(
            f"CRITICO: Arquivo de configuracao nao encontrado em {CONFIG_PATH}!"
        )
        PATHS = {}
    except Exception as e:
        logger.critical(f"CRITICO: Falha ao ler configuracao: {e}")
        PATHS = {}


load_paths()
