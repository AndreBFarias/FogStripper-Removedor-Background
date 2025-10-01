#!/bin/bash
echo "### Expurgando o Santuário do FogStripper ###"
rm -rf "$HOME/.local/share/fogstripper"
rm -f "$HOME/.local/share/applications/fogstripper.desktop"
rm -f "$HOME/.local/share/icons/hicolor/128x128/apps/fogstripper.png"
update-desktop-database -q "$HOME/.local/share/applications/"
gtk-update-icon-cache -q -t "$HOME/.local/share/icons/hicolor/"
echo "Expurgo concluído."
