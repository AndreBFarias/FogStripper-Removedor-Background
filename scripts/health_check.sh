#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

ERRORS=0

check_pass() {
    echo -e "${GREEN}[OK]${NC} $1"
}

check_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ERRORS=$((ERRORS + 1))
}

check_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo "=========================================="
echo "FogStripper Health Check"
echo "=========================================="
echo ""

echo ">> Verificando estrutura de diretorios..."
for dir in src src/core src/gui src/utils src/tests assets; do
    if [ -d "$dir" ]; then
        check_pass "$dir/"
    else
        check_fail "$dir/ nao encontrado"
    fi
done
if [ -d "logs" ]; then
    check_pass "logs/"
else
    check_warn "logs/ nao encontrado (sera criado na execucao)"
fi
echo ""

echo ">> Verificando arquivos essenciais..."
for file in src/main.py requirements.txt install.sh LICENSE pyproject.toml; do
    if [ -f "$file" ]; then
        check_pass "$file"
    else
        check_fail "$file nao encontrado"
    fi
done
if [ -f "config.ini" ]; then
    check_pass "config.ini"
else
    check_warn "config.ini nao encontrado (sera criado pelo install.sh)"
fi
echo ""

echo ">> Verificando ambientes virtuais..."
for venv in venv venv_rembg venv_upscale; do
    if [ -d "$venv" ] && [ -f "$venv/bin/python" ]; then
        check_pass "$venv/"
    else
        check_warn "$venv/ nao configurado"
    fi
done
echo ""

echo ">> Verificando dependencias principais..."
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || true

    declare -A pkg_imports=(
        ["PyQt6"]="PyQt6"
        ["Pillow"]="PIL"
        ["numpy"]="numpy"
        ["opencv-python"]="cv2"
    )

    for pkg in "${!pkg_imports[@]}"; do
        import_name="${pkg_imports[$pkg]}"
        if python -c "import $import_name" 2>/dev/null; then
            check_pass "$pkg instalado"
        else
            check_fail "$pkg nao encontrado"
        fi
    done

    deactivate 2>/dev/null || true
else
    check_warn "venv nao encontrado, pulando verificacao de dependencias"
fi
echo ""

echo ">> Verificando sintaxe Python..."
for pyfile in $(find src -name "*.py" -type f 2>/dev/null); do
    if python -m py_compile "$pyfile" 2>/dev/null; then
        check_pass "$pyfile"
    else
        check_fail "Erro de sintaxe em $pyfile"
    fi
done
echo ""

echo ">> Verificando imports principais..."
if python -c "from src.core.processor import ProcessThread" 2>/dev/null; then
    check_pass "src.core.processor"
else
    check_fail "Falha ao importar src.core.processor"
fi

if python -c "from src.gui.main_window import DesnudadorWindow" 2>/dev/null; then
    check_pass "src.gui.main_window"
else
    check_fail "Falha ao importar src.gui.main_window"
fi

if python -c "from src.utils.svg_utils import raster_to_svg" 2>/dev/null; then
    check_pass "src.utils.svg_utils"
else
    check_fail "Falha ao importar src.utils.svg_utils"
fi
echo ""

echo ">> Verificando workers..."
for worker in worker_rembg worker_background worker_effects worker_upscale; do
    if [ -f "src/${worker}.py" ]; then
        if python -m py_compile "src/${worker}.py" 2>/dev/null; then
            check_pass "$worker.py"
        else
            check_fail "Erro de sintaxe em $worker.py"
        fi
    else
        check_fail "$worker.py nao encontrado"
    fi
done
echo ""

echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}Health check concluido sem erros${NC}"
    exit 0
else
    echo -e "${RED}Health check encontrou $ERRORS erro(s)${NC}"
    exit 1
fi
