import json
import os
import logging

logger = logging.getLogger(__name__)

APP_DIR = os.path.expanduser("~/.local/share/fogstripper")
CONFIG_PATH = os.path.join(APP_DIR, "config.json")

PATHS = {}

def load_paths():
    global PATHS
    try:
        with open(CONFIG_PATH, 'r') as f:
            PATHS = json.load(f)
        logger.info("Mapa da Criação (config.json) carregado com sucesso.")
    except FileNotFoundError:
        logger.critical(f"CRÍTICO: O Mapa da Criação (config.json) não foi encontrado em {CONFIG_PATH}!")
        PATHS = {} # Deixa o dicionário vazio para falhar graciosamente
    except Exception as e:
        logger.critical(f"CRÍTICO: Falha ao ler o Mapa da Criação: {e}")
        PATHS = {}

# Carrega os caminhos na primeira vez que o módulo é importado
load_paths()
