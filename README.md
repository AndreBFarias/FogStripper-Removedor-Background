<div align="center">

[![opensource](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](#)
[![licenca](https://img.shields.io/badge/licenca-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![Estrelas](https://img.shields.io/github/stars/[REDACTED]/FogStripper.svg?style=social)](https://github.com/[REDACTED]/FogStripper/stargazers)
[![Contribuicoes](https://img.shields.io/badge/contribuicoes-bem--vindas-brightgreen.svg)](CONTRIBUTING.md)

---

<img src="https://raw.githubusercontent.com/[REDACTED]/FogStripper-Removedor-Background/main/assets/icon.png" width="120" alt="Icone do FogStripper">

<h1>FogStripper</h1>

</div>

---

Uma aplicacao grafica para Linux que remove fundos de imagens e videos usando modelos de redes neurais que rodam **localmente**, sem depender de servicos externos.

---

<img src="https://raw.githubusercontent.com/[REDACTED]/FogStripper-Removedor-Background/main/assets/Fogstripper.png" width="700" alt="Screenshot do FogStripper">

---

## Funcionalidades

**Remocao de fundo com multiplos modelos:**
- `u2netp` — versao leve, mais rapida, ideal para uso geral
- `u2net` — equilibrio entre velocidade e precisao
- `u2net_human_seg` — especializado em figuras humanas
- `isnet-general-use` — maxima precisao para objetos complexos

**Upscaling com RealESRGAN:**
- Ampliacao em **2x, 3x ou 4x** de resolucao
- Controle de VRAM via tamanho de bloco (tile)

**Pos-processamento integrado:**
- Composicao de fundo com cor solida ou imagem personalizada
- Sombra projetada com controle de desfoque e opacidade
- Recorte inteligente (Trim) para remover excesso de transparencia
- Preenchimento de buracos internos no objeto
- Limpeza de ruido externo via morfologia

**Suporte a animacoes:**
- Processa GIF e WEBM quadro a quadro
- Exporta animacao recomposta ou sequencia de frames estaticos

**Exportacao:** PNG, WEBP, SVG (vetor multicolorido via vtracer), GIF

---

## Arquitetura

O FogStripper usa um **venv unificado** instalado em:

```
~/.local/share/fogstripper/venv/
```

Todas as dependencias — GUI, rembg, torch, RealESRGAN — coexistem neste unico
ambiente. Os workers de processamento sao executados como subprocessos independentes,
o que isola falhas sem exigir ambientes separados.

Os modelos U2Net sao armazenados em:

```
~/.local/share/fogstripper/models/u2net/
```

Eles sao baixados automaticamente na primeira execucao de cada modelo.

---

## Instalacao

Requer Python 3.10+ e conexao com a internet na primeira instalacao.

```bash
git clone https://github.com/[REDACTED]/FogStripper-Removedor-Background.git
cd FogStripper-Removedor-Background

chmod +x install.sh
./install.sh
```

O instalador:
1. Cria o venv em `~/.local/share/fogstripper/venv/`
2. Instala PyTorch 2.0.1 + torchvision 0.15.2 (GPU ou CPU)
3. Instala todas as demais dependencias
4. Cria o atalho no menu de aplicativos

Apos a instalacao, inicie pelo menu de aplicativos ou:

```bash
PYTHONPATH=~/.local/share/fogstripper \
~/.local/share/fogstripper/venv/bin/python3 \
~/.local/share/fogstripper/src/main.py
```

---

## Uso

1. Arraste imagens para a janela ou clique na area de drop para selecionar arquivos
2. Configure o modelo, formato de saida e potencia de borda
3. Ative o pos-processamento se desejar fundo, sombra ou recorte
4. Confirme no dialogo de opcoes
5. O resultado e salvo no mesmo diretorio da imagem original
   (o arquivo original e preservado com sufixo `.bak`)

---

## Dependencias Principais

| Pacote | Versao | Funcao |
|--------|--------|--------|
| PyQt6 | 6.10.0 | Interface grafica |
| rembg | 2.0.60 | Remocao de fundo |
| onnxruntime | 1.23.2 | Inferencia dos modelos |
| torch | 2.0.1 | Backend do RealESRGAN |
| torchvision | 0.15.2 | Auxiliar do torch |
| basicsr | >=1.4.2 | Arquitetura RRDBNet |
| realesrgan | >=0.3.0 | Upscaling |
| Pillow | >=9.0.0 | Manipulacao de imagens |
| opencv-python | >=4.8.0 | Processamento de mascara |
| vtracer | >=0.6.0 | Vetorizacao SVG |

---

## Desinstalacao

```bash
~/.local/share/fogstripper/uninstall.sh
```

---

## Licenca

GPLv3 — livre para modificar e usar desde que tudo permanca livre.

Consulte o arquivo [LICENSE](LICENSE) para os termos completos.
