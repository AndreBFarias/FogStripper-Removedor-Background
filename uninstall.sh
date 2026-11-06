#!/bin/bash

APP_DIR=$(cd "$(dirname "$0")" && pwd)
LEGACY_DIR="$HOME/.local/share/fogstripper"
DESKTOP_FILE="$HOME/.local/share/applications/fogstripper.desktop"
ICON_DIR_BASE="$HOME/.local/share/icons/hicolor"

echo "============================================================"
echo "  FOGSTRIPPER - DESINSTALACAO"
echo "============================================================"
echo ""

echo ">> Removendo ambiente da aplicação em $APP_DIR (o código fica)..."
rm -rf "$APP_DIR/venv" "$APP_DIR/models/u2net"
rm -f "$APP_DIR/config.json" "$APP_DIR/app.log" "$APP_DIR/app.log.old"

if [ -d "$LEGACY_DIR" ]; then
    echo ">> Removendo instalação antiga em $LEGACY_DIR..."
    rm -rf "$LEGACY_DIR"
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
