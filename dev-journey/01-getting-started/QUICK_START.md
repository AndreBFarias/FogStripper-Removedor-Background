# Quick Start - FogStripper

## Requisitos

- Python 3.10+
- GPU NVIDIA (opcional, mas recomendado)
- Pop!_OS / Ubuntu / Debian

## Instalacao

```bash
git clone https://github.com/AndreBFarias/FogStripper-Removedor-Background.git
cd FogStripper-Removedor-Background
chmod +x install.sh
./install.sh
```

O script detecta automaticamente se voce tem GPU NVIDIA e configura os ambientes apropriados.

## Execucao

Apos instalacao, o FogStripper estara disponivel no menu de aplicacoes.

Alternativamente:
```bash
~/.local/share/fogstripper/venv/bin/python ~/.local/share/fogstripper/src/main.py
```

## Modo Desenvolvimento

```bash
python dev_run.py
```

## Estrutura de Venvs

O projeto usa 3 ambientes virtuais isolados:

| Venv | Proposito |
|------|-----------|
| venv/ | GUI (PyQt6) |
| venv_rembg/ | Remocao de fundo (rembg, onnxruntime) |
| venv_upscale/ | Upscaling (torch, RealESRGAN) |

Isso evita conflitos entre PyTorch e ONNX Runtime.

## Uso Basico

1. Arraste uma imagem para a janela
2. Selecione o modelo de remocao
3. Configure opcoes de pos-processamento
4. Clique em processar

## Formatos Suportados

**Entrada:** PNG, JPG, WEBP, GIF, MP4, WebM, MOV

**Saida:** PNG, WEBP, SVG, GIF
