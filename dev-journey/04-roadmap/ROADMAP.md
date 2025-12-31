# Roadmap - FogStripper

## Visao de Longo Prazo

Tornar o FogStripper a melhor ferramenta open source de remocao de fundos para Linux.

---

## Fase 1: Fundacao (Concluida)

- [x] pyproject.toml com ruff e mypy
- [x] Reorganizacao src/ (core, gui, utils, tests)
- [x] dev-journey/ com documentacao
- [x] Unificacao tools/ com src/utils/

---

## Fase 2: Qualidade (Em Andamento)

- [ ] Type hints em todos os modulos
- [ ] Testes unitarios (meta: 60% cobertura)
- [ ] .pre-commit-config.yaml
- [ ] Docstrings em funcoes publicas

---

## Fase 3: Automacao

- [ ] .github/workflows/ci.yml
- [ ] scripts/health_check.sh
- [ ] Semantic versioning
- [ ] GitHub Releases automatizados

---

## Fase 4: Melhorias de UX

- [ ] GUI responsiva (nao mais tamanho fixo)
- [ ] Suporte a atalhos de teclado
- [ ] Batch processing (multiplas imagens)
- [ ] Preview em tempo real

---

## Fase 5: Novas Funcionalidades

- [ ] Mais modelos de remocao (SAM, etc)
- [ ] Edicao manual de mascara
- [ ] Historico de operacoes (undo/redo)
- [ ] Exportacao em lote

---

## Backlog

- Cache de modelos rembg
- API REST opcional
- Containerizacao (Docker)
- Flatpak/Snap packaging
- Suporte a Windows
- Integracao com GIMP/Krita
