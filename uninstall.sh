#!/bin/bash

echo "### Desinstalando o FogStripper ###"

#2
echo "--> Removendo diretório da aplicação..."
rm -rf "$HOME/.local/share/fogstripper"

#3
echo "--> Removendo atalho do menu..."
rm -f "$HOME/.local/share/applications/fogstripper.desktop"

#4
echo "--> Removendo ícone..."
rm -f "$HOME/.local/share/icons/hicolor/128x128/apps/fogstripper.png"

#5
echo "--> Atualizando cache de aplicativos e ícones..."
update-desktop-database -q "$HOME/.local/share/applications/"
gtk-update-icon-cache -q -t "$HOME/.local/share/icons/hicolor/"

echo ""
echo "Desinstalação concluída."
