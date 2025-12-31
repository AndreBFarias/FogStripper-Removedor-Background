# API - Processador

## ProcessThread

Classe principal que executa o pipeline de processamento em uma thread separada.

### Importacao

```python
from src.core.processor import ProcessThread
```

### Construtor

```python
ProcessThread(
    input_path: str,
    model_name: str,
    output_format: str,
    potencia: int,
    tile_size: int,
    post_processing_opts: dict[str, Any]
)
```

#### Parametros

| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `input_path` | `str` | Caminho para arquivo de entrada |
| `model_name` | `str` | Nome do modelo rembg |
| `output_format` | `str` | Formato de saida (.png, .webp, .svg) |
| `potencia` | `int` | Forca da remocao (0-100) |
| `tile_size` | `int` | Tamanho do tile para upscale |
| `post_processing_opts` | `dict` | Opcoes de pos-processamento |

#### post_processing_opts

```python
{
    "upscale_factor": int,      # 0, 2 ou 4
    "apply_shadow": bool,       # Aplicar sombra
    "background_type": str,     # "color" ou "image"
    "background_data": str      # Cor hex ou caminho da imagem
}
```

### Sinais

| Sinal | Parametro | Descricao |
|-------|-----------|-----------|
| `progress` | `int` | Progresso 0-100 |
| `finished` | `str` | Caminho do arquivo final |
| `error` | `str` | Mensagem de erro |

### Exemplo

```python
from PyQt6.QtCore import QCoreApplication
from src.core.processor import ProcessThread

def on_finished(path: str) -> None:
    print(f"Processamento concluido: {path}")

def on_error(msg: str) -> None:
    print(f"Erro: {msg}")

thread = ProcessThread(
    input_path="/caminho/imagem.png",
    model_name="u2net",
    output_format=".png",
    potencia=75,
    tile_size=512,
    post_processing_opts={
        "upscale_factor": 0,
        "apply_shadow": False,
        "background_type": None,
        "background_data": None,
    }
)

thread.finished.connect(on_finished)
thread.error.connect(on_error)
thread.start()
```

## Metodos

### run_command

Executa um comando de worker em subprocess.

```python
def run_command(self, command: list[str | None]) -> bool
```

### cleanup

Remove arquivos temporarios.

```python
def cleanup(self) -> None
```

## Workers

Os workers sao scripts Python executados em ambientes virtuais separados:

| Worker | Ambiente | Funcao |
|--------|----------|--------|
| `worker_rembg.py` | venv_rembg | Remocao de fundo |
| `worker_upscale.py` | venv_upscale | Upscale com RealESRGAN |
| `worker_background.py` | venv | Aplicacao de fundo |
| `worker_effects.py` | venv | Efeitos (sombra) |
