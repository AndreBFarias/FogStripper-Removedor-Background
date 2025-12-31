#!/bin/bash
# install_hooks.sh
# Instala os hooks do git usando pre-commit framework

set -e

# Garantir que estamos na raiz do projeto
cd "$(dirname "$0")/.."

echo ">> Instalando pre-commit..."
pip install pre-commit

echo ">> Configurando hooks do git..."
pre-commit install

echo ">> Hooks instalados com sucesso!"
