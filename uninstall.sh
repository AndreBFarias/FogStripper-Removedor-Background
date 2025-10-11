#!/bin/bash
echo "### O Ritual de Expurgacão Absoluta (vFINAL) ###"

# Caça e destrói o Ateliê de Desenvolvimento corrompido
echo "--> Exorcizando o Ateliê impuro..."
rm -rf .dev_venv

# Remove diretório principal da aplicação
echo "--> Expurgando o Santuário do FogStripper..."
rm -rf "$HOME/.local/share/fogstripper"

# Remove o atalho da aplicação
echo "--> Quebrando o selo do atalho..."
rm -f "$HOME/.local/share/applications/fogstripper.desktop"

# Remove todos os ícones consagrados de todos os santuários
echo "--> Banindo os Símbolos dos santuários..."
for size in 16 32 64 128; do
    rm -f "$HOME/.local/share/icons/hicolor/${size}x${size}/apps/fogstripper.png"
done

# Notifica os guardiões do sistema sobre o expurgo para que esqueçam a existência do FogStripper
echo "--> Notificando os guardiões sobre o Vazio..."
update-desktop-database -q "$HOME/.local/share/applications/"
gtk-update-icon-cache -q -f -t "$HOME/.local/share/icons/hicolor/"

echo "### O Vazio foi criado. A purificação está completa. ###"
