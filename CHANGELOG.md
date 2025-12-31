# Changelog

Todas as mudancas notaveis neste projeto serao documentadas aqui.

O formato e baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2024-12-31

### Adicionado
- Remocao de fundo usando rembg
- Suporte a multiplos modelos (u2net, isnet, sam)
- Upscale com RealESRGAN (2x, 4x)
- Efeitos de pos-processamento (sombra)
- Suporte a fundo customizado (cor ou imagem)
- Exportacao para PNG, WEBP, SVG, GIF
- Processamento de animacoes (GIF/video)
- Interface grafica com PyQt6
- Tema escuro (Dark Dracula)
- Sistema de backup automatico (.bak)
- Documentacao completa com MkDocs
- CI/CD com GitHub Actions
- Testes unitarios e de integracao
- Type hints em todos os modulos
- Pre-commit hooks
- Docker support
- Makefile para comandos comuns

### Tecnico
- Arquitetura multi-venv para isolamento de dependencias
- Workers em subprocess para processamento paralelo
- Logging rotacionado
- Configuracao via JSON
- Semantic release para versionamento automatico
