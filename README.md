# FogStripper - Removedor de Fundo 🌫️

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

FogStripper é uma aplicação desktop robusta para remover fundos de imagens e vídeos usando IA, com suporte a upscale e efeitos visuais.

## 🚀 Funcionalidades

- **Remoção de Fundo**: Utiliza `rembg` (u2net, isnet, etc.) para recortes precisos.
- **Upscale IA**: Aumenta a resolução com Real-ESRGAN (2x, 4x).
- **Processamento em Lote**: Arraste múltiplas imagens ou pastas.
- **Animações e Vídeos**: Suporte a GIF, MP4, WEBM (experimental).
- **Efeitos**: Sombras, bordas suaves e substituição de fundo.
- **Interface Moderna**: GUI em PyQt6 com tema escuro e responsivo.

## 📂 Estrutura do Projeto

```
FogStripper/
├── src/
│   ├── core/           # Núcleo (logger, processamento, config)
│   ├── gui/            # Interface gráfica (PyQt6)
│   ├── workers/        # Scripts de IA (Rembg, Upscale)
│   ├── utils/          # Utilitários (ícones, svg)
│   └── main.py         # Ponto de entrada
├── scripts/
│   ├── qa/             # Scripts de qualidade (hooks git)
│   └── install_hooks.sh
├── dev-journey/        # Documentação do projeto (Status, Debt)
├── requirements.txt    # Dependências unificadas
├── dev_run.py          # Script de desenvolvimento
└── README.md
```

## 🛠️ Instalação e Uso

1.  **Pré-requisitos**: Python 3.10+ e Drivers NVIDIA (opcional, para GPU).
2.  **Instalação**:
    ```bash
    git clone https://github.com/AndreBFarias/FogStripper-Removedor-Background.git
    cd FogStripper-Removedor-Background
    pip install -r requirements.txt
    ```
3.  **Executar (Modo Dev)**:
    ```bash
    python3 dev_run.py
    ```

## 🤝 Contribuindo

Consulte `CONTRIBUTING.md` para diretrizes de código. O projeto utiliza `pre-commit` para garantir qualidade.

1.  Instale os hooks: `./scripts/install_hooks.sh`
2.  Siga o padrão de commits.

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
