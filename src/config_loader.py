import json
import os
import logging

logger = logging.getLogger(__name__)

#2
# Verifica se estamos em modo de desenvolvimento
if os.getenv("FOGSTRIPPER_DEV_MODE"):
    logger.warning("MODO DE DESENVOLVIMENTO ATIVADO!")
    # Aponta para a raiz do projeto para encontrar o config.dev.json
    APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    CONFIG_PATH = os.path.join(APP_DIR, "config.dev.json")
else:
    APP_DIR = os.path.expanduser("~/.local/share/fogstripper")
    CONFIG_PATH = os.path.join(APP_DIR, "config.json")

PATHS = {}

def load_paths():
    global PATHS
    try:
        with open(CONFIG_PATH, 'r') as f:
            PATHS = json.load(f)
        logger.info(f"Mapa da Criação ({os.path.basename(CONFIG_PATH)}) carregado com sucesso.")
    except FileNotFoundError:
        logger.critical(f"CRÍTICO: O Mapa da Criação ({os.path.basename(CONFIG_PATH)}) não foi encontrado em {CONFIG_PATH}!")
        PATHS = {} # Deixa o dicionário vazio para falhar graciosamente
    except Exception as e:
        logger.critical(f"CRÍTICO: Falha ao ler o Mapa da Criação: {e}")
        PATHS = {}

# Carrega os caminhos na primeira vez que o módulo é importado
load_paths()
