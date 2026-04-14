# Changelog

Todas as mudancas notaveis neste projeto serao documentadas aqui.

O formato e baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.1.0] - 2026-04-13

### Corrigido
- Shim de compatibilidade para basicsr 1.4.2 com torchvision >= 0.16 (modulo functional_tensor removido)
- Versoes de torch (2.0.1) e torchvision (0.15.2) pinadas no install.sh para garantir compatibilidade
- Configuracao de U2NET_HOME para isolamento do cache de modelos em diretorio local do projeto
- Parametros shadow_blur e shadow_opacity agora sao repassados corretamente ao worker de efeitos
- PYTHONPATH ausente no launcher do pacote .deb corrigido
- dev_run.py atualizado com versoes corretas do PyTorch (cu118/cpu)
- Venv reinstalavel apos limpeza de disco ou atualizacao do sistema operacional

### Adicionado
- Diretorio models/u2net/ criado automaticamente pelo install.sh
- U2NET_HOME adicionado ao config.json para controle do cache de modelos
- worker_effects.py aceita --blur-radius, --offset-x, --offset-y e --opacity via argparse

### Tecnico
- Ferramentas de desenvolvimento removidas do requirements.txt (uso exclusivo de requirements-ci.txt)
- ARCHITECTURE.md atualizado para refletir arquitetura de venv unificado
- README.md reescrito com instrucoes e dependencias atuais
- check_structure.py melhorado com verificacao de workers e arquivos criticos
- SPRINT_ISOLAMENTO_MODELOS_U2NET.md removido apos conclusao da sprint

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
