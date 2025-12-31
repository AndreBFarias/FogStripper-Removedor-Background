# FogStripper

**Removedor de fundo de imagens**

FogStripper e uma ferramenta desktop para remocao automatica de fundo de imagens usando modelos de segmentacao. Suporta imagens estaticas e animacoes (GIF/video).

## Funcionalidades

- **Remocao de fundo** - Usa modelos como U2Net, ISNET para segmentacao precisa
- **Upscale com RealESRGAN** - Aumenta a resolucao da imagem apos processamento
- **Suporte a animacoes** - Processa GIFs e videos frame a frame
- **Efeitos de pos-processamento** - Sombras, fundos customizados
- **Exportacao flexivel** - PNG, WEBP, SVG, GIF

## Inicio Rapido

```bash
# Clonar repositorio
git clone https://github.com/AndreBFarias/FogStripper-Removedor-Background.git
cd FogStripper-Removedor-Background

# Executar instalador
chmod +x install.sh
./install.sh

# Iniciar aplicacao
source venv/bin/activate
python src/main.py
```

## Requisitos

- Python 3.10+
- GPU NVIDIA com CUDA (recomendado para upscale)
- Linux (testado em Ubuntu/Pop!_OS)

## Links

- [Instalacao Completa](guides/installation.md)
- [Uso Basico](guides/basic-usage.md)
- [Contribuindo](development/contributing.md)
