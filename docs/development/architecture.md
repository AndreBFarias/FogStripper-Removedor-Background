# Arquitetura

## Visao Geral

```
FogStripper/
├── src/
│   ├── core/           # Logica de negocios
│   │   ├── processor.py
│   │   ├── config_loader.py
│   │   └── logger_config.py
│   ├── gui/            # Interface grafica
│   │   └── main_window.py
│   ├── utils/          # Utilitarios
│   │   ├── svg_utils.py
│   │   └── icon_resizer.py
│   ├── tests/          # Testes
│   ├── worker_*.py     # Workers de processamento
│   └── main.py         # Entry point
├── venv/               # Ambiente principal
├── venv_rembg/         # Ambiente rembg
└── venv_upscale/       # Ambiente upscale
```

## Multi-Venv

O projeto usa multiplos ambientes virtuais para isolar dependencias conflitantes:

```
┌─────────────────┐
│   venv (main)   │
│  PyQt6, Pillow  │
│  numpy, opencv  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌──────────┐
│venv_  │ │ venv_    │
│rembg  │ │ upscale  │
│       │ │          │
│rembg  │ │RealESRGAN│
│onnx   │ │ torch    │
└───────┘ └──────────┘
```

## Pipeline de Processamento

```
Entrada
   │
   ▼
┌──────────────────┐
│ 1. Backup        │
│    .bak          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. Remocao BG    │
│    worker_rembg  │
│    (venv_rembg)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. Upscale       │  (opcional)
│    worker_upscale│
│    (venv_upscale)│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. Sombra        │  (opcional)
│    worker_effects│
│    (venv)        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 5. Fundo         │  (opcional)
│    worker_backgr │
│    (venv)        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 6. Exportacao    │
│    PNG/WEBP/SVG  │
└──────────────────┘
```

## Comunicacao entre Processos

Os workers sao executados como subprocessos:

```python
subprocess.run([
    python_path,        # /path/to/venv_rembg/bin/python
    worker_script,      # src/worker_rembg.py
    "--input", input,
    "--output", output,
    "--model", model,
])
```

Isso permite:

1. Isolamento de dependencias
2. Melhor gerenciamento de memoria
3. Facil debug de workers individuais

## Threads

A GUI usa QThread para processamento assincrono:

```
┌─────────────────┐
│   Main Thread   │
│   (GUI/Qt)      │
└────────┬────────┘
         │ start()
         ▼
┌─────────────────┐
│  ProcessThread  │
│  (QThread)      │
│                 │
│  subprocess     │──► worker_rembg
│  subprocess     │──► worker_upscale
│  subprocess     │──► worker_effects
└────────┬────────┘
         │ signals
         ▼
┌─────────────────┐
│   Main Thread   │
│   (update GUI)  │
└─────────────────┘
```

## Sinais Qt

```python
class ProcessThread(QThread):
    progress = pyqtSignal(int)    # 0-100
    finished = pyqtSignal(str)    # path
    error = pyqtSignal(str)       # message
```

## Estrutura de Testes

```
src/tests/
├── conftest.py          # Fixtures compartilhadas
├── test_config_loader.py
├── test_logger_config.py
├── test_processor.py
├── test_svg_utils.py
├── test_icon_resizer.py
└── test_workers.py      # Testes de integracao
```
