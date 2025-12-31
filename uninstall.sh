#!/bin/bash

APP_DIR="$HOME/.local/share/fogstripper"
DESKTOP_FILE="$HOME/.local/share/applications/fogstripper.desktop"
ICON_DIR_BASE="$HOME/.local/share/icons/hicolor"

echo "============================================================"
echo "  FOGSTRIPPER - DESINSTALACAO"
echo "============================================================"
echo ""

if [ -d "$APP_DIR" ]; then
    echo ">> Removendo arquivos da aplicacao em $APP_DIR..."
    rm -rf "$APP_DIR"
else
    echo ">> Diretorio da aplicacao nao encontrado (ja removido?)."
fi

if [ -f "$DESKTOP_FILE" ]; then
    echo ">> Removendo atalho..."
    rm "$DESKTOP_FILE"
fi

echo ">> Removendo icones..."
for size in 16 32 64 128; do
    rm -f "$ICON_DIR_BASE/${size}x${size}/apps/fogstripper.png"
done

echo ">> Atualizando caches..."
update-desktop-database -q "$HOME/.local/share/applications"
gtk-update-icon-cache -q -f -t "$ICON_DIR_BASE"

echo ""
echo ">> Desinstalacao concluida."
