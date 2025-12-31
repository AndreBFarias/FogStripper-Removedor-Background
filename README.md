<div align="center">

[![CI](https://github.com/AndreBFarias/FogStripper-Removedor-Background/actions/workflows/ci.yml/badge.svg)](https://github.com/AndreBFarias/FogStripper-Removedor-Background/actions/workflows/ci.yml)
[![Docs](https://github.com/AndreBFarias/FogStripper-Removedor-Background/actions/workflows/docs.yml/badge.svg)](https://andrebfarias.github.io/FogStripper-Removedor-Background/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

[![Estrelas](https://img.shields.io/github/stars/AndreBFarias/FogStripper-Removedor-Background.svg?style=social)](https://github.com/AndreBFarias/FogStripper-Removedor-Background/stargazers)
[![Contribuicoes](https://img.shields.io/badge/contribuicoes-bem--vindas-brightgreen.svg)](CONTRIBUTING.md)

---

<img src="https://raw.githubusercontent.com/AndreBFarias/FogStripper-Removedor-Background/main/assets/icon.png" width="120" alt="FogStripper">

<h1>FogStripper</h1>

</div>

---

Aplicacao desktop Linux para remocao automatica de fundos de imagens. Usa modelos de segmentacao para separar objetos do fundo com precisao.

---

<img src="https://raw.githubusercontent.com/AndreBFarias/FogStripper-Removedor-Background/main/assets/Fogstripper.png" width="700" alt="Screenshot do FogStripper">

### Funcionalidades

- **Remocao de Fundo:** Multiplos modelos de segmentacao disponiveis:
    - `u2net` / `u2netp`: Uso geral, bom equilibrio velocidade/qualidade
    - `u2net_human_seg`: Otimizado para figuras humanas
    - `isnet-general-use`: Alta precisao para objetos complexos

- **Upscale (Real-ESRGAN):** Aumente a resolucao das imagens em 2x ou 4x

- **Pos-Processamento:**
    - Composicao de fundo (cor solida ou imagem)
    - Projecao de sombra
    - Recorte automatico (trim)
    - Preenchimento de buracos
    - Limpeza de ruido

- **Animacoes:** Suporte a GIF e WEBM, processamento frame a frame

- **Exportacao:** PNG, WEBP, SVG, GIF

- **Interface:** Drag and drop, feedback de progresso

### Arquitetura

O projeto usa 3 ambientes virtuais isolados para evitar conflitos de dependencias:

1. `venv_gui`: Interface (PyQt6)
2. `venv_rembg`: Segmentacao (rembg, ONNX)
3. `venv_upscale`: Upscale (Real-ESRGAN, PyTorch)

### Instalacao

```bash
git clone https://github.com/AndreBFarias/FogStripper-Removedor-Background.git
cd FogStripper-Removedor-Background

chmod +x install.sh
./install.sh
```

### Dependencias

- **PyQt6**: Interface grafica
- **rembg**: Remocao de fundo
- **Pillow**: Manipulacao de imagens
- **Real-ESRGAN**: Upscale (opcional)

### Uso

1. Arraste imagens para a janela ou clique em "Selecione Imagens"
2. Ajuste potencia e opcoes de pos-processamento
3. Clique em processar

### Documentacao

Disponivel em: **[andrebfarias.github.io/FogStripper-Removedor-Background](https://andrebfarias.github.io/FogStripper-Removedor-Background/)**

### Licenca

GPL v3 - Livre para modificar e usar.
