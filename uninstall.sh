#!/bin/bash
set -e

echo "### O Ritual do Expurgo (Desinstalação) ###"

APP_DIR="$HOME/.local/share/fogstripper"
DESKTOP_FILE="$HOME/.local/share/applications/fogstripper.desktop"

if [ -d "$APP_DIR" ]; then
    echo "--> Removendo arquivos da aplicação em $APP_DIR..."
    rm -rf "$APP_DIR"
else
    echo "--> Diretório da aplicação não encontrado (já removido?)."
fi

if [ -f "$DESKTOP_FILE" ]; then
    echo "--> Removendo atalho do menu..."
    rm "$DESKTOP_FILE"
else
    echo "--> Atalho do menu não encontrado."
fi

echo "--> Removendo ícones..."
for size in 16 32 64 128; do
    ICON_FILE="$HOME/.local/share/icons/hicolor/${size}x${size}/apps/fogstripper.png"
    if [ -f "$ICON_FILE" ]; then
        rm "$ICON_FILE"
    fi
done

echo "--> Atualizando banco de dados do desktop e cache de ícones..."
update-desktop-database -q "$HOME/.local/share/applications"
gtk-update-icon-cache -q -f -t "$HOME/.local/share/icons/hicolor"

echo ""
echo "######################################################################"
echo "O FOGSTRIPPER FOI COMPLETAMENTE REMOVIDO."
echo "######################################################################"
