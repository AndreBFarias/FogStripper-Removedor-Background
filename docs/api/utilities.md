# API - Utilitarios

## svg_utils

Conversao de imagens raster para SVG vetorial.

### raster_to_svg

```python
from src.utils.svg_utils import raster_to_svg

def raster_to_svg(
    input_path: str,
    output_path: str,
    num_colors: int = 16
) -> bool
```

#### Parametros

| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `input_path` | `str` | Caminho da imagem de entrada |
| `output_path` | `str` | Caminho do SVG de saida |
| `num_colors` | `int` | Numero de cores para quantizacao |

#### Retorno

- `True`: Conversao bem sucedida
- `False`: Erro na conversao

#### Exemplo

```python
from src.utils.svg_utils import raster_to_svg

success = raster_to_svg(
    input_path="imagem.png",
    output_path="imagem.svg",
    num_colors=8
)

if success:
    print("SVG criado com sucesso")
```

### Funcionamento

1. Carrega imagem com OpenCV
2. Aplica filtro bilateral para suavizar
3. Quantiza cores usando K-means
4. Encontra contornos para cada cor
5. Gera paths SVG com aproximacao poligonal

## icon_resizer

Redimensiona icones para multiplos tamanhos.

### resize_icon

```python
from src.utils.icon_resizer import resize_icon

def resize_icon(
    source_path: str,
    output_dir: str,
    sizes: list[int]
) -> None
```

#### Parametros

| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `source_path` | `str` | Caminho do icone original |
| `output_dir` | `str` | Diretorio de saida |
| `sizes` | `list[int]` | Lista de tamanhos |

#### Exemplo

```python
from src.utils.icon_resizer import resize_icon

resize_icon(
    source_path="assets/icon.png",
    output_dir="assets/generated_icons",
    sizes=[16, 32, 64, 128, 256]
)
```

## config_loader

Carregamento de configuracoes.

### Variaveis Globais

```python
from src.core.config_loader import PATHS, CONFIG_PATH
```

| Variavel | Tipo | Descricao |
|----------|------|-----------|
| `PATHS` | `dict` | Configuracoes carregadas |
| `CONFIG_PATH` | `str` | Caminho do config.json |

### load_paths

Recarrega configuracoes do arquivo.

```python
from src.core.config_loader import load_paths

load_paths()
```

## logger_config

Configuracao de logging.

### setup_logging

```python
from src.core.logger_config import setup_logging, get_log_path

setup_logging()
log_path = get_log_path()
```

### Variaveis

| Variavel | Valor |
|----------|-------|
| `LOG_DIR` | `~/.local/share/fogstripper` |
| `LOG_FILE` | `~/.local/share/fogstripper/app.log` |
