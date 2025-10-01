import logging
import os
import sys

def setup_logging():
    log_dir = os.path.expanduser("~/.local/share/fogstripper")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')

    if os.path.exists(log_file):
        open(log_file, 'w').close()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("="*50)
    logging.info(f"Sistema de Log inicializado. Log salvo em: {log_file}")
    logging.info("="*50)
