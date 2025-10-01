#!/bin/bash
set -e

echo "### Construindo os Reinos Isolados para o FogStripper (Versão Definitiva) ###"
APP_DIR="$HOME/.local/share/fogstripper"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR"

VENV_GUI_DIR="$APP_DIR/venv_gui"
VENV_REMBG_DIR="$APP_DIR/venv_rembg"
VENV_UPSCALE_DIR="$APP_DIR/venv_upscale"

PYTHON_GUI="$VENV_GUI_DIR/bin/python3"
PYTHON_REMBG="$VENV_REMBG_DIR/bin/python3"
PYTHON_UPSCALE="$VENV_UPSCALE_DIR/bin/python3"

echo "--> Forjando o Reino da Interface..."
python3 -m venv "$VENV_GUI_DIR"
"$PYTHON_GUI" -m pip install --upgrade pip
"$PYTHON_GUI" -m pip install -r ./requirements.txt

echo "--> Forjando o Reino do Desnudamento (rembg)..."
python3 -m venv "$VENV_REMBG_DIR"
"$PYTHON_REMBG" -m pip install --upgrade pip
"$PYTHON_REMBG" -m pip install -r ./src/requirements_rembg.txt

echo "--> Forjando o Reino da Ampliação (realesrgan)... (Isso pode demorar)"
python3 -m venv "$VENV_UPSCALE_DIR"
"$PYTHON_UPSCALE" -m pip install --upgrade pip
"$PYTHON_UPSCALE" -m pip install -r ./src/requirements_upscale.txt

echo "--> Escrevendo o Mapa da Criação (config.json)..."
cat > "$APP_DIR/config.json" << EOL
{
    "PYTHON_REMBG": "$PYTHON_REMBG",
    "PYTHON_UPSCALE": "$PYTHON_UPSCALE",
    "REMBG_SCRIPT": "$APP_DIR/src/worker_rembg.py",
    "UPSCALE_SCRIPT": "$APP_DIR/src/worker_upscale.py"
}
EOL

echo "--> Copiando a alma da aplicação..."
mkdir -p "$APP_DIR/src"
cp ./src/*.py "$APP_DIR/src/"
cp -R ./assets "$APP_DIR/"
cp ./uninstall.sh "$APP_DIR/"
chmod +x "$APP_DIR/uninstall.sh"

echo "--> Consagrando ícone e atalho..."
mkdir -p "$HOME/.local/share/icons/hicolor/128x128/apps"
cp ./assets/desnudador.png "$HOME/.local/share/icons/hicolor/128x128/apps/fogstripper.png"

cat > "$HOME/.local/share/applications/fogstripper.desktop" << EOL
[Desktop Entry]
Name=FogStripper
Comment=Remove o fundo de imagens com IA
Exec=$PYTHON_GUI $APP_DIR/src/main.py
Icon=fogstripper
Type=Application
Categories=Graphics;Utility;
Terminal=false
StartupWMClass=FogStripper
EOL

update-desktop-database -q "$HOME/.local/share/applications/"
gtk-update-icon-cache -q -t "$HOME/.local/share/icons/hicolor/"

echo "✨ Instalação Concluída. A Criação está completa e o Mapa foi selado."
