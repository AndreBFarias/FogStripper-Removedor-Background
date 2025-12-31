# Contribuindo

Obrigado pelo interesse em contribuir com o FogStripper.

## Configuracao do Ambiente

### 1. Fork e Clone

```bash
git clone https://github.com/SEU_USUARIO/FogStripper-Removedor-Background.git
cd FogStripper-Removedor-Background
```

### 2. Instalacao para Desenvolvimento

```bash
chmod +x install.sh
./install.sh

source venv/bin/activate
pip install pre-commit
pre-commit install
```

### 3. Verificar Instalacao

```bash
./scripts/health_check.sh
pytest src/tests/
```

## Fluxo de Trabalho

### Branch

```bash
git checkout -b feature/minha-feature
# ou
git checkout -b fix/meu-bugfix
```

### Commits

Use mensagens claras em portugues:

```bash
git commit -m "Adiciona suporte a formato AVIF"
git commit -m "Corrige erro de memoria no upscale"
```

### Pre-commit

O pre-commit roda automaticamente:

- Ruff (lint + format)
- MyPy (type check)
- Bandit (seguranca)
- pytest (testes)

### Pull Request

1. Push para seu fork
2. Abra PR para `main`
3. Preencha o template
4. Aguarde review

## Padroes de Codigo

### Type Hints

Todos os parametros e retornos devem ter type hints:

```python
def process_image(
    input_path: str,
    output_path: str,
    options: dict[str, Any]
) -> bool:
    ...
```

### Imports

Ordem de imports:

1. Biblioteca padrao
2. Terceiros
3. Locais

```python
import os
import sys

import numpy as np
from PIL import Image

from src.core.processor import ProcessThread
```

### Docstrings

Use docstrings apenas quando necessario para documentacao publica.
Codigo interno deve ser auto-explicativo.

### Logging

Use logging em vez de print:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Processamento iniciado")
logger.error(f"Erro: {e}")
```

## Testes

### Executar Testes

```bash
# Todos os testes
pytest src/tests/ -v

# Com cobertura
pytest src/tests/ --cov=src --cov-report=term-missing

# Testes especificos
pytest src/tests/test_processor.py -v
```

### Escrever Testes

```python
import pytest
from src.utils.svg_utils import raster_to_svg

class TestRasterToSvg:
    def test_basic_conversion(self, sample_image, temp_dir):
        output = temp_dir / "output.svg"
        result = raster_to_svg(str(sample_image), str(output))
        assert result is True
        assert output.exists()
```

### Fixtures

Use as fixtures do `conftest.py`:

- `temp_dir`: Diretorio temporario
- `sample_image`: Imagem PNG 100x100
- `sample_image_with_transparency`: Imagem com transparencia
- `background_image`: Imagem de fundo 200x200

## Reportar Bugs

Use o template de issue no GitHub:

1. Descricao clara do bug
2. Passos para reproduzir
3. Comportamento esperado
4. Sistema operacional e versao Python
5. Logs de erro

## Sugerir Features

1. Verifique se ja existe uma issue similar
2. Descreva o problema que resolve
3. Proponha uma solucao
4. Indique se pode contribuir com PR
