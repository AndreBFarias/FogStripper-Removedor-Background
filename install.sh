#!/bin/bash

echo "### Construindo o Santuário para o FogStripper (com Identidade de Janela) ###"

#2
APP_DIR="$HOME/.local/share/fogstripper"
VENV_DIR="$APP_DIR/venv"
PYTHON_EXEC="$VENV_DIR/bin/python3"

#3
echo "--> Limpando instalações antigas..."
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR"

#4
echo "--> Copiando arquivos da aplicação..."
rsync -a --exclude 'venv' --exclude '.git' ./ "$APP_DIR/"

#5
echo "--> Criando ambiente virtual isolado..."
python3 -m venv "$VENV_DIR"
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao criar o ambiente virtual."
    exit 1
fi

#6
echo "--> Instalando dependências dentro do santuário..."
"$PYTHON_EXEC" -m pip install --upgrade pip > /dev/null
"$PYTHON_EXEC" -m pip install -r "$APP_DIR/requirements.txt" > /dev/null
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar as dependências no venv."
    exit 1
fi

#7
echo "--> Instalando ícone..."
mkdir -p "$HOME/.local/share/icons/hicolor/128x128/apps"
cp "$APP_DIR/assets/desnudador.png" "$HOME/.local/share/icons/hicolor/128x128/apps/fogstripper.png"

#8
echo "--> Criando atalho no menu de aplicativos com a identidade correta..."
cat > "$HOME/.local/share/applications/fogstripper.desktop" << EOL
[Desktop Entry]
Name=FogStripper
Comment=Remove o fundo de imagens com IA
Exec=$PYTHON_EXEC $APP_DIR/main.py
Icon=fogstripper
Type=Application
Categories=Graphics;Utility;
Terminal=false
StartupWMClass=main.py
EOL

#9
echo "--> Atualizando cache de aplicativos e ícones..."
update-desktop-database -q "$HOME/.local/share/applications/"
gtk-update-icon-cache -q -t "$HOME/.local/share/icons/hicolor/"

echo ""
echo "Instalação concluída. A identidade do FogStripper foi registrada."
