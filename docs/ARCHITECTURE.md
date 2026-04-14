# Arquitetura - FogStripper

## Visao Geral

FogStripper e uma aplicacao desktop para remocao de fundos de imagens usando IA local.

```
+-------------------------------------------------------------+
|                        USUARIO                              |
|                           |                                 |
|  +---------------------------------------------------+      |
|  |                    GUI (PyQt6)                    |      |
|  |              src/gui/main_window.py               |      |
|  +---------------------+-----------------------------+      |
|                         |                                   |
|  +---------------------------------------------------+      |
|  |             ORQUESTRADOR (QThread)                |      |
|  |              src/core/processor.py                |      |
|  +------+----------+----------+--------------------+  |      |
|         |          |          |          |          |  |      |
|  +------+--+ +-----+---+ +---+-----+ +--+------+   |      |
|  | rembg   | | upscale | | effects | |  bg     |   |      |
|  | worker  | | worker  | | worker  | | worker  |   |      |
|  +---------+ +---------+ +---------+ +---------+   |      |
|                                                     |      |
|     Todos executados no mesmo venv unificado        |      |
|     ~/.local/share/fogstripper/venv/                |      |
+-----------------------------------------------------+------+
```

## Estrutura de Diretorios

```
FogStripper-Removedor-Background/
+-- src/
|   +-- main.py                  # Ponto de entrada
|   +-- core/
|   |   +-- processor.py         # Pipeline de processamento (QThread)
|   |   +-- config_loader.py     # Carregamento de configuracao
|   |   +-- constants.py         # Extensoes suportadas
|   |   +-- logger_config.py     # Sistema de logging
|   +-- gui/
|   |   +-- main_window.py       # Janela principal
|   |   +-- drop_area.py         # Componente de drag-and-drop
|   |   +-- dialogs.py           # Dialogos de opcoes e mensagens
|   |   +-- settings_panel.py    # Painel de configuracoes do modelo
|   |   +-- post_processing_panel.py  # Painel de pos-processamento
|   |   +-- widgets.py           # Alias de importacao dos paineis
|   |   +-- constants.py         # Constantes e descricoes de modelos
|   +-- utils/
|   |   +-- svg_utils.py         # Conversao raster para SVG
|   |   +-- icon_resizer.py      # Utilitario de geracao de icones
|   |   +-- image_processing.py  # Funcoes de pre/pos-processamento
|   +-- workers/
|   |   +-- worker_rembg.py      # Worker de remocao de fundo
|   |   +-- worker_upscale.py    # Worker de upscaling (RealESRGAN)
|   |   +-- worker_effects.py    # Worker de efeitos (sombra)
|   |   +-- worker_background.py # Worker de composicao de fundo
|   +-- tests/                   # Testes unitarios
+-- docs/                        # Documentacao tecnica
+-- assets/                      # Recursos visuais
+-- scripts/                     # Scripts de build e verificacao
+-- install.sh                   # Instalador para uso local
+-- uninstall.sh                 # Desinstalador
+-- requirements.txt             # Dependencias de producao
+-- requirements-ci.txt          # Ferramentas de CI/CD
+-- pyproject.toml               # Configuracao do projeto e ferramentas
```

## Venv Unificado

O projeto usa **um unico ambiente virtual** instalado em:

```
~/.local/share/fogstripper/venv/
```

Este venv contem todas as dependencias: PyQt6, rembg, onnxruntime, torch, torchvision,
basicsr, RealESRGAN, Pillow, imageio e demais utilidades.

A decisao de unificar os venvs (anteriormente eram 3 separados) foi tomada apos
verificar que as versoes pinadas de torch (2.0.1) e torchvision (0.15.2) sao
compatíveis tanto com rembg quanto com basicsr/RealESRGAN.

## Workers como Subprocessos

Cada worker e executado via `subprocess.run()` usando o Python do venv unificado.
Isso isola falhas: se o upscale crashar, a GUI continua responsiva.

O caminho do executavel Python e dos scripts e lido de `config.json`:

```json
{
    "PYTHON_REMBG":  "~/.local/share/fogstripper/venv/bin/python3",
    "PYTHON_UPSCALE": "~/.local/share/fogstripper/venv/bin/python3",
    "REMBG_SCRIPT":  "~/.local/share/fogstripper/src/workers/worker_rembg.py",
    "UPSCALE_SCRIPT": "~/.local/share/fogstripper/src/workers/worker_upscale.py",
    "EFFECTS_SCRIPT": "~/.local/share/fogstripper/src/workers/worker_effects.py",
    "BACKGROUND_SCRIPT": "~/.local/share/fogstripper/src/workers/worker_background.py",
    "U2NET_HOME": "~/.local/share/fogstripper/models/u2net"
}
```

## Pipeline de Processamento

```
Imagem Original
     |
     +-- Backup (.bak)
     |
[worker_rembg.py] -- Remocao de fundo (rembg + onnxruntime)
     |
[processor.py]   -- Fill holes / Noise removal (opencv)
     |
[processor.py]   -- Crop/Trim (opcional, Pillow)
     |
[worker_upscale.py] -- RealESRGAN (opcional, torch)
     |
[worker_effects.py] -- Sombra (opcional, Pillow)
     |
[worker_background.py] -- Composicao (opcional, Pillow)
     |
[svg_utils.py]   -- Vetorizacao (se formato SVG, vtracer)
     |
Imagem Final
```

## Modelos U2Net

Os modelos sao baixados automaticamente pelo rembg na primeira execucao.
O diretorio de cache e configurado via variavel de ambiente `U2NET_HOME`:

```
~/.local/share/fogstripper/models/u2net/
```

A variavel e definida em `worker_rembg.py` antes de importar o rembg,
garantindo que os modelos nao sejam salvos no cache global `~/.u2net/`.

## Logging

- Arquivo: `~/.local/share/fogstripper/app.log`
- Rotacao automatica ao atingir 1 MB
- Formato: `timestamp - level - [modulo:linha] - mensagem`

## Configuracao de Desenvolvimento

O script `dev_run.py` cria um venv em `.dev_venv/` e usa `config.dev.json`
(gerado dinamicamente, ignorado pelo git).

Ativar modo dev: `FOGSTRIPPER_DEV_MODE=1` via `dev_run.py`.
