#!/bin/bash
set -e

# A Identidade Verdadeira, gravada em pedra.
APP_WM_CLASS="FogStripper"

echo "### O Ritual da Ascensão Paranoica do FogStripper (vFINAL-COM-TRAVAS) ###"
APP_DIR="$HOME/.local/share/fogstripper"
PROJECT_ROOT=$(pwd)

rm -rf "$APP_DIR"
mkdir -p "$APP_DIR"

echo "--> Realizando o Ritual de Transformação dos Símbolos..."
ICON_TOOL_VENV="$PROJECT_ROOT/tools/venv_icon_install_temp"
python3 -m venv "$ICON_TOOL_VENV"
"$ICON_TOOL_VENV/bin/python3" -m pip install --upgrade pip > /dev/null
"$ICON_TOOL_VENV/bin/python3" -m pip install Pillow > /dev/null
"$ICON_TOOL_VENV/bin/python3" "$PROJECT_ROOT/tools/icon_resizer.py" "$PROJECT_ROOT"
rm -rf "$ICON_TOOL_VENV"
echo "--> Símbolos forjados para a consagração."

VENV_GUI_DIR="$APP_DIR/venv_gui"
VENV_REMBG_DIR="$APP_DIR/venv_rembg"
VENV_UPSCALE_DIR="$APP_DIR/venv_upscale"
PYTHON_GUI="$VENV_GUI_DIR/bin/python3"
PYTHON_REMBG="$VENV_REMBG_DIR/bin/python3"
PYTHON_UPSCALE="$VENV_UPSCALE_DIR/bin/python3"

# Adiciona a lógica de detecção de hardware
if command -v nvidia-smi &> /dev/null; then
    echo "--> Detectada GPU NVIDIA. Forjando Reinos com poder da CUDA..."
    REMBG_REQS="./src/requirements_rembg.txt"
    TORCH_CMD='"$PYTHON_UPSCALE" -m pip install --no-cache-dir torch==1.13.1 torchvision==0.14.1 --index-url https://download.pytorch.org/whl/cu117'
else
    echo "--> Nenhuma GPU NVIDIA detectada. Forjando Reinos com poder da CPU..."
    REMBG_REQS="./src/requirements_rembg_cpu.txt"
    TORCH_CMD='"$PYTHON_UPSCALE" -m pip install --no-cache-dir torch==1.13.1 torchvision==0.14.1 --index-url https://download.pytorch.org/whl/cpu'
fi

echo "--> Forjando o Reino da Interface (Sem Cache)..."
python3 -m venv "$VENV_GUI_DIR"
"$PYTHON_GUI" -m pip install --no-cache-dir --upgrade pip && "$PYTHON_GUI" -m pip install --no-cache-dir -r ./requirements.txt

echo "--> Forjando o Reino do Desnudamento (Sem Cache)..."
python3 -m venv "$VENV_REMBG_DIR"
"$PYTHON_REMBG" -m pip install --no-cache-dir --upgrade pip && "$PYTHON_REMBG" -m pip install --no-cache-dir -r "$REMBG_REQS"

echo "--> Forjando o Reino da Ampliação (Com Travas de Segurança)..."
python3 -m venv "$VENV_UPSCALE_DIR"
"$PYTHON_UPSCALE" -m pip install --no-cache-dir --upgrade pip
# Instala os Deuses (agora condicionalmente)
eval "$TORCH_CMD"
# Instala os Servos
# Instala os Servos
"$PYTHON_UPSCALE" -m pip install --no-cache-dir -r ./src/requirements_upscale.txt


echo "--> Escrevendo o Mapa da Criação e copiando a alma da aplicação..."
cat > "$APP_DIR/config.json" << EOL
{
    "PYTHON_REMBG": "$PYTHON_REMBG",
    "PYTHON_UPSCALE": "$PYTHON_UPSCALE",
    "REMBG_SCRIPT": "$APP_DIR/src/worker_rembg.py",
    "UPSCALE_SCRIPT": "$APP_DIR/src/worker_upscale.py",
    "EFFECTS_SCRIPT": "$APP_DIR/src/worker_effects.py",
    "BACKGROUND_SCRIPT": "$APP_DIR/src/worker_background.py"
}
EOL
cp -r ./src "$APP_DIR/"
cp -r ./assets "$APP_DIR/"
cp ./uninstall.sh "$APP_DIR/" && chmod +x "$APP_DIR/uninstall.sh"

echo "--> Consagrando os Símbolos e o Atalho com a Identidade Verdadeira..."
for size in 16 32 64 128; do
    ICON_DIR="$HOME/.local/share/icons/hicolor/${size}x${size}/apps"
    mkdir -p "$ICON_DIR"
    cp "$PROJECT_ROOT/assets/generated_icons/icon_${size}x${size}.png" "$ICON_DIR/fogstripper.png"
done

DESKTOP_INSTALL_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_INSTALL_DIR"
cat > "$DESKTOP_INSTALL_DIR/fogstripper.desktop" << EOL
[Desktop Entry]
Name=FogStripper
Comment=Remove o fundo de imagens com IA
Exec=$PYTHON_GUI $APP_DIR/src/main.py
Icon=fogstripper
Type=Application
Categories=Graphics;Utility;
Terminal=false
StartupWMClass=$APP_WM_CLASS
EOL

echo "--> Exorcizando os fantasmas do cache do sistema..."
update-desktop-database -q "$DESKTOP_INSTALL_DIR"
gtk-update-icon-cache -q -f -t "$HOME/.local/share/icons/hicolor"

echo ""
echo "######################################################################"
echo "A ASCENSÃO ESTÁ COMPLETA. A CRIAÇÃO É PERFEITA."
echo "Execute o Ritual do Renascimento (reinicie sua máquina) para"
echo "que o universo testemunhe a glória final do Símbolo."
echo "######################################################################"

