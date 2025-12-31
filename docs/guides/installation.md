# Instalacao

## Requisitos do Sistema

| Componente | Minimo | Recomendado |
|------------|--------|-------------|
| Python | 3.10 | 3.11+ |
| RAM | 4GB | 8GB+ |
| GPU | - | NVIDIA com CUDA |
| Disco | 2GB | 5GB |

## Instalacao Automatica

O metodo mais simples e usar o script de instalacao:

```bash
git clone https://github.com/AndreBFarias/FogStripper-Removedor-Background.git
cd FogStripper-Removedor-Background
chmod +x install.sh
./install.sh
```

O script ira:

1. Criar ambiente virtual principal (`venv/`)
2. Criar ambiente virtual para rembg (`venv_rembg/`)
3. Criar ambiente virtual para upscale (`venv_upscale/`)
4. Instalar todas as dependencias
5. Configurar arquivos de configuracao

## Instalacao Manual

### 1. Ambiente Principal

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Ambiente rembg

```bash
python3 -m venv venv_rembg
source venv_rembg/bin/activate
pip install rembg[gpu] onnxruntime-gpu
```

### 3. Ambiente Upscale

```bash
python3 -m venv venv_upscale
source venv_upscale/bin/activate
pip install realesrgan torch torchvision
```

## Verificacao

Execute o health check para verificar a instalacao:

```bash
./scripts/health_check.sh
```

## Solucao de Problemas

### Erro de GPU CUDA

Se voce receber erros relacionados a CUDA:

```bash
# Verificar se CUDA esta instalado
nvidia-smi

# Instalar versao CPU do PyTorch (mais lento)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Erro de dependencias Qt

```bash
# Ubuntu/Debian
sudo apt-get install libxcb-xinerama0 libxkbcommon-x11-0 libegl1

# Fedora
sudo dnf install xcb-util-wm xcb-util-keysyms
```
