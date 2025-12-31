# Changelog

Todas as mudancas notaveis neste projeto serao documentadas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [1.0.0] - 2025-12-31

### Adicionado
- Reorganizacao completa do projeto seguindo padrao CLAUDE.md
- pyproject.toml com configuracao ruff e mypy
- Estrutura src/core/, src/gui/, src/utils/, src/tests/
- dev-journey/ para documentacao de desenvolvimento
- Plano de evolucao 10/10

### Alterado
- Movido config_loader.py, logger_config.py, processor.py para src/core/
- Movido gui.py para src/gui/main_window.py
- Movido svg_utils.py para src/utils/
- Movido icon_resizer.py de tools/ para src/utils/
- Atualizado todos os imports para nova estrutura

### Removido
- Pasta tools/ (unificada com src/utils/)

## [0.9.0] - Anterior

### Funcionalidades Originais
- Remocao de fundo com rembg (4 modelos)
- Upscaling com RealESRGAN (2x, 3x, 4x)
- Efeito de sombra
- Composicao de fundo (cor solida ou imagem)
- Conversao para SVG vetorial
- Suporte a animacoes (GIF, WebM, MP4)
- Interface PyQt6 com tema escuro
- Drag & drop
- Sistema de backup automatico
