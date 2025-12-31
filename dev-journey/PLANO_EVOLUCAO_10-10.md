# Plano de Evolucao FogStripper - Meta 10/10

**Data:** 2025-12-31
**Baseline:** Scorecard 68/100 (B-)
**Meta:** 95/100 (A)
---

## Resumo Executivo

Este plano transforma um projeto funcional em um projeto de excelencia.

```
ANTES (68/100)                    DEPOIS (95/100)
├── src/ (flat)                   ├── src/
│   ├── main.py                   │   ├── core/
│   ├── gui.py                    │   ├── workers/
│   └── workers...                │   ├── gui/
│                                 │   ├── utils/
├── tools/                        │   └── tests/
│   └── icon_resizer.py           │
│                                 ├── scripts/
├── docs/ (vazio)                 │   ├── health_check.sh
│                                 │   └── validate.sh
│                                 │
└── (sem CI/CD)                   ├── dev-journey/
                                  │   ├── 01-getting-started/
                                  │   ├── 02-changelog/
                                  │   └── templates/
                                  │
                                  ├── .github/workflows/
                                  │   ├── ci.yml
                                  │   └── pr-check.yml
                                  │
                                  ├── pyproject.toml
                                  └── .pre-commit-config.yaml
```

---

## Fase 1: Fundacao (68 -> 78)

### 1.1 Criar pyproject.toml

Configuracao moderna Python com ruff e mypy.

```toml
[project]
name = "fogstripper"
version = "1.0.0"
description = "Removedor de fundo de imagens"
readme = "README.md"
license = {text = "GPL-3.0"}
requires-python = ">=3.10"
keywords = ["image", "background-removal", "rembg", "upscale", "realesrgan"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: X11 Applications :: Qt",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Multimedia :: Graphics :: Editors",
]

[tool.ruff]
target-version = "py310"
line-length = 120
exclude = ["venv", "venv_*", ".git", "__pycache__"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B"]
ignore = ["E501", "E722", "F401", "F841"]

[tool.mypy]
python_version = "3.10"
ignore_missing_imports = true
warn_return_any = false
show_error_codes = true
exclude = ["venv", "venv_*", "tests"]

[tool.pytest.ini_options]
testpaths = ["src/tests"]
python_files = ["test_*.py"]
```

**Impacto:** +3 pontos (DevOps, Manutenibilidade)

---

### 1.2 Reorganizar src/

**Estrutura atual:**
```
src/
├── main.py
├── gui.py
├── processor.py
├── config_loader.py
├── logger_config.py
├── svg_utils.py
├── worker_rembg.py
├── worker_background.py
├── worker_effects.py
├── worker_upscale.py
└── requirements_*.txt
```

**Estrutura proposta:**
```
src/
├── __init__.py
├── main.py                    # Entry point (manter na raiz src/)
├── core/
│   ├── __init__.py
│   ├── processor.py           # Pipeline principal
│   ├── config_loader.py
│   └── logger_config.py
├── workers/
│   ├── __init__.py
│   ├── rembg.py               # worker_rembg.py
│   ├── background.py          # worker_background.py
│   ├── effects.py             # worker_effects.py
│   └── upscale.py             # worker_upscale.py
├── gui/
│   ├── __init__.py
│   └── main_window.py         # gui.py
├── utils/
│   ├── __init__.py
│   ├── svg_utils.py
│   └── icon_resizer.py        # de tools/
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_rembg.py
    ├── test_background.py
    ├── test_effects.py
    └── test_upscale.py
```

**Migracao de imports:**
```python
# ANTES
from processor import ProcessThread
from gui import DesnudadorWindow

# DEPOIS
from src.core.processor import ProcessThread
from src.gui.main_window import DesnudadorWindow
```

**Impacto:** +5 pontos (Arquitetura, Manutenibilidade)

---

### 1.3 Criar dev-journey/

Estrutura de documentacao organizada.

```
dev-journey/
├── 01-getting-started/
│   └── QUICK_START.md
├── 02-changelog/
│   └── CHANGELOG.md
├── 03-architecture/
│   └── ARCHITECTURE.md
├── 04-roadmap/
│   └── ROADMAP.md
├── templates/
│   ├── BUG_REPORT.md
│   └── FEATURE_REQUEST.md
└── 2025-12-31_Session_Summary.md
```

**Impacto:** +5 pontos (Documentacao)

---

### 1.4 Deletar pasta tools/

Mover `icon_resizer.py` para `src/utils/` e remover pasta.

**Impacto:** +1 ponto (Arquitetura)

---

## Fase 2: Qualidade (78 -> 88)

### 2.1 Adicionar Type Hints

Todos os arquivos Python devem ter type hints.

**Exemplo worker_rembg.py:**
```python
# ANTES
def remove_background(input_path, output_path, model, potencia):
    ...

# DEPOIS
def remove_background(
    input_path: str,
    output_path: str,
    model: str,
    potencia: int
) -> bool:
    ...
```

**Arquivos prioritarios:**
1. src/core/processor.py (345 linhas)
2. src/gui/main_window.py (375 linhas)
3. src/workers/*.py (4 arquivos)
4. src/utils/*.py (2 arquivos)
5. src/core/config_loader.py
6. src/core/logger_config.py

**Impacto:** +10 pontos (Codigo, Manutenibilidade)

---

### 2.2 Criar Testes Unitarios

**Estrutura de testes:**
```python
# src/tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    path = tmp_path / "test.png"
    img.save(path)
    return path

@pytest.fixture
def output_path(tmp_path: Path) -> Path:
    return tmp_path / "output.png"
```

```python
# src/tests/test_background.py
import pytest
from src.workers.background import apply_background

def test_solid_color_background(sample_image, output_path):
    result = apply_background(
        str(sample_image),
        str(output_path),
        "#FF0000",
        None,
        "fit-bg-to-fg"
    )
    assert result is True
    assert output_path.exists()
```

**Cobertura minima:** 60%

**Impacto:** +15 pontos (Testes)

---

### 2.3 Criar .pre-commit-config.yaml

```yaml
repos:
  - repo: local
    hooks:
      - id: check-file-size
        name: "[1/5] God Mode Prevention (max 400 linhas)"
        language: system
        entry: bash scripts/check_file_size.sh
        pass_filenames: false
        always_run: true

      - id: check-logger-usage
        name: "[2/5] Logger obrigatorio"
        language: system
        entry: bash scripts/check_logger.sh
        pass_filenames: false
        always_run: true

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        name: "[3/5] Ruff lint"
        args: ["--fix", "--exit-non-zero-on-fix"]
      - id: ruff-format
        name: "[4/5] Ruff format"

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
        name: "[5/5] Trailing whitespace"
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
```

**Impacto:** +3 pontos (DevOps)

---

## Fase 3: Automacao (88 -> 95)

### 3.1 Criar .github/workflows/ci.yml

```yaml
name: CI FogStripper

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]

permissions:
  contents: read

jobs:
  quality-gates:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4

      - name: Check file sizes (max 400 lines)
        run: |
          MAX_LINES=400
          ERRORS=0
          for file in $(find src -name "*.py" -type f ! -path "*/tests/*" ! -name "__init__.py"); do
            lines=$(wc -l < "$file")
            if [ "$lines" -gt $MAX_LINES ]; then
              echo "ERRO: $file tem $lines linhas (max: $MAX_LINES)"
              ERRORS=$((ERRORS + 1))
            fi
          done
          if [ "$ERRORS" -gt 0 ]; then
            exit 1
          fi

  lint:
    runs-on: ubuntu-latest
    needs: quality-gates
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install ruff
      - run: ruff check src/ --output-format=github

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install pytest Pillow numpy
      - run: pytest src/tests/ -v --tb=short
```

**Impacto:** +5 pontos (DevOps, Testes)

---

### 3.2 Criar scripts/

```
scripts/
├── health_check.sh      # Verificacao de ambiente
├── check_file_size.sh   # God Mode Prevention
├── check_logger.sh      # Logger obrigatorio
└── validate.sh          # Validacao completa
```

**health_check.sh:**
```bash
#!/bin/bash
# Verificacao de saude do ambiente FogStripper

echo "================================"
echo "  FOGSTRIPPER HEALTH CHECK"
echo "================================"

# 1. Verificar venvs
for venv in venv venv_rembg venv_upscale; do
    if [ -d "$venv" ]; then
        echo "[OK] $venv existe"
    else
        echo "[WARN] $venv nao encontrado"
    fi
done

# 2. Verificar arquivos criticos
for f in main.py requirements.txt install.sh; do
    if [ -f "$f" ]; then
        echo "[OK] $f"
    else
        echo "[FAIL] $f nao encontrado"
    fi
done

# 3. Verificar GPU
if command -v nvidia-smi &> /dev/null; then
    GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
    echo "[OK] GPU: $GPU"
else
    echo "[WARN] GPU nao detectada (modo CPU)"
fi
```

**Impacto:** +2 pontos (DevOps)

---

### 3.3 Atualizar Dependencias

**requirements_upscale.txt:**
```
# ANTES
torch==1.13.1
torchvision==0.14.1

# DEPOIS
torch>=2.0.0
torchvision>=0.15.0
```

**Acao:** Testar compatibilidade com torch 2.x

**Impacto:** +2 pontos (Seguranca)

---

## Cronograma de Execucao

```
┌─────────────────────────────────────────────────────────────┐
│                    PLANO DE EXECUCAO                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FASE 1: FUNDACAO (4 tarefas)                              │
│  ├── [1.1] pyproject.toml                                  │
│  ├── [1.2] Reorganizar src/                                │
│  ├── [1.3] Criar dev-journey/                              │
│  └── [1.4] Deletar tools/                                  │
│                                                             │
│  FASE 2: QUALIDADE (3 tarefas)                             │
│  ├── [2.1] Type hints em todos os modulos                  │
│  ├── [2.2] Testes unitarios (60% cobertura)                │
│  └── [2.3] .pre-commit-config.yaml                         │
│                                                             │
│  FASE 3: AUTOMACAO (3 tarefas)                             │
│  ├── [3.1] .github/workflows/ci.yml                        │
│  ├── [3.2] scripts/ utilitarios                            │
│  └── [3.3] Atualizar dependencias                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Metricas de Sucesso

| Metrica | Atual | Meta | Status |
|---------|-------|------|--------|
| Nota Geral | 68/100 | 95/100 | Pendente |
| Type Hints | 0% | 100% | Pendente |
| Cobertura Testes | 0% | 60% | Pendente |
| CI/CD | Nao | Sim | Pendente |
| Pre-commit | Nao | Sim | Pendente |
| Documentacao | 30% | 80% | Pendente |

---

## Ordem de Execucao Recomendada

1. **pyproject.toml** - Base para todas as ferramentas
2. **Reorganizar src/** - Estrutura limpa
3. **Type hints** - Qualidade de codigo
4. **dev-journey/** - Documentacao
5. **scripts/** - Utilitarios
6. **.pre-commit-config.yaml** - Hooks locais
7. **Testes** - Cobertura
8. **.github/workflows/** - CI/CD
9. **Atualizar deps** - Seguranca

---

**Assinatura:**
```
"A excelencia nao e um ato, mas um habito."
-- Aristoteles
```
