# Arquitetura - FogStripper

## Visao Geral

FogStripper e uma aplicacao desktop para remocao de fundos de imagens usando IA.

```
┌─────────────────────────────────────────────────────────────┐
│                        USUARIO                              │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    GUI (PyQt6)                       │   │
│  │                 src/gui/main_window.py               │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               ORQUESTRADOR (QThread)                 │   │
│  │                src/core/processor.py                 │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│           ┌─────────────┼─────────────┐                    │
│           │             │             │                    │
│           ▼             ▼             ▼                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │  REMBG    │ │  UPSCALE   │ │  EFFECTS   │              │
│  │ (venv_r)  │ │ (venv_u)   │ │ (venv_r)   │              │
│  └────────────┘ └────────────┘ └────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Estrutura de Diretorios

```
FogStripper-Removedor-Background/
├── src/
│   ├── main.py              # Entry point
│   ├── core/
│   │   ├── processor.py     # Pipeline de processamento
│   │   ├── config_loader.py # Carregamento de configuracao
│   │   └── logger_config.py # Sistema de logging
│   ├── gui/
│   │   └── main_window.py   # Interface PyQt6
│   ├── utils/
│   │   ├── svg_utils.py     # Conversao raster->SVG
│   │   └── icon_resizer.py  # Utilitario de icones
│   ├── tests/               # Testes unitarios
│   ├── worker_rembg.py      # Worker remocao fundo
│   ├── worker_background.py # Worker composicao
│   ├── worker_effects.py    # Worker efeitos
│   └── worker_upscale.py    # Worker upscaling
├── dev-journey/             # Documentacao de desenvolvimento
├── docs/                    # Documentacao tecnica
├── assets/                  # Recursos visuais
├── scripts/                 # Utilitarios shell
└── venv*, venv_rembg, venv_upscale  # Ambientes isolados
```

## Decisoes Arquiteturais

### Multi-Venv

O projeto usa 3 ambientes virtuais separados para evitar conflitos:

1. **venv/** - GUI e orquestracao
   - PyQt6, qdarkstyle, Pillow, imageio

2. **venv_rembg/** - Remocao de fundo
   - rembg, onnxruntime-gpu/cpu

3. **venv_upscale/** - Upscaling
   - torch, RealESRGAN

### Workers como Subprocessos

Cada worker e executado via `subprocess.run()` no seu venv especifico.
Isso permite isolamento de falhas e uso de diferentes versoes de libs.

### Pipeline de Processamento

```
Imagem Original
     │
     ├──▶ Backup (.bak)
     │
     ▼
[worker_rembg.py] ──▶ Remocao de fundo
     │
     ▼
[processor.py] ──▶ Fill holes / Noise removal
     │
     ▼
[processor.py] ──▶ Crop/Trim (opcional)
     │
     ▼
[worker_upscale.py] ──▶ RealESRGAN (opcional)
     │
     ▼
[worker_effects.py] ──▶ Sombra (opcional)
     │
     ▼
[worker_background.py] ──▶ Composicao (opcional)
     │
     ▼
[svg_utils.py] ──▶ Vetorizacao (se SVG)
     │
     ▼
Imagem Final
```

## Fluxo de Dados

1. Usuario arrasta imagem para GUI
2. GUI cria ProcessThread com parametros
3. ProcessThread executa pipeline em QThread separada
4. Cada etapa chama worker via subprocess
5. Resultado final emitido via pyqtSignal
6. GUI atualiza interface

## Configuracao

O arquivo `config.json` (ou `config.dev.json` em dev) mapeia:

```json
{
    "PYTHON_REMBG": "/path/to/venv_rembg/bin/python",
    "PYTHON_UPSCALE": "/path/to/venv_upscale/bin/python",
    "REMBG_SCRIPT": "/path/to/worker_rembg.py",
    "UPSCALE_SCRIPT": "/path/to/worker_upscale.py",
    "EFFECTS_SCRIPT": "/path/to/worker_effects.py",
    "BACKGROUND_SCRIPT": "/path/to/worker_background.py"
}
```

## Logging

- Arquivo: `~/.local/share/fogstripper/app.log`
- Rotacao automatica ao atingir 1MB
- Formato: timestamp - level - [module:line] - message
