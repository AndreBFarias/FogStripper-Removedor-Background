# Contribuindo

Veja a documentacao completa em [docs/development/contributing.md](docs/development/contributing.md) ou na [documentacao online](https://andrebfarias.github.io/FogStripper-Removedor-Background/development/contributing/).

## Inicio Rapido

```bash
# Clone e configure
git clone https://github.com/SEU_USUARIO/FogStripper-Removedor-Background.git
cd FogStripper-Removedor-Background
./install.sh

# Configure pre-commit
source venv/bin/activate
pip install pre-commit
pre-commit install

# Rode os testes
pytest src/tests/ -v
```

## Checklist

- [ ] Fork do repositorio
- [ ] Branch para sua feature (`git checkout -b feature/nome`)
- [ ] Commits com mensagens claras
- [ ] Testes passando (`pytest src/tests/`)
- [ ] Pre-commit passando
- [ ] PR com template preenchido
