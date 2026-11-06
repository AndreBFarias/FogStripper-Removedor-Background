import logging
import os
import sys

_PROJECT_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Flatpak e AppImage rodam de um diretório somente leitura.
LOG_DIR: str = _PROJECT_DIR if os.access(_PROJECT_DIR, os.W_OK) else os.path.expanduser("~/.local/share/fogstripper")
LOG_FILE: str = os.path.join(LOG_DIR, "app.log")


def get_log_path() -> str:
    return LOG_FILE


def setup_logging() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)

    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 1 * 1024 * 1024:
        try:
            os.rename(LOG_FILE, LOG_FILE + ".old")
        except OSError as e:
            print(f"Não foi possível rotacionar o arquivo de log: {e}")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(message)s",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
        force=True,
    )
    logging.info("=" * 50)
    logging.info(f"Sistema de Log inicializado. Log salvo em: {LOG_FILE}")
    logging.info("=" * 50)
