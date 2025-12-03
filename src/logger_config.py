import logging
import os
import sys

LOG_DIR = os.path.expanduser("~/.local/share/fogstripper")
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

def get_log_path():
    """Retorna o caminho completo para o arquivo de log."""
    return LOG_FILE

def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)

    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 1 * 1024 * 1024:
        try:
            os.rename(LOG_FILE, LOG_FILE + ".old")
        except OSError as e:
            print(f"Não foi possível rotacionar o arquivo de log: {e}")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )
    logging.info("="*50)
    logging.info(f"Sistema de Log inicializado. Log salvo em: {LOG_FILE}")
    logging.info("="*50)
