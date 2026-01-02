# Contribuindo

Veja a documentacao completa em [docs/development/contributing.md](docs/development/contributing.md).

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
```

### Como Começar

1.  Leia a documentação técnica em `docs/`.
2.  Faça um fork do projeto.
3.  Crie uma branch para sua feature (`git checkout -b feature/nova-feature`).
4.  Commit suas mudanças (`git commit -m 'feat: adiciona nova feature'`).
5.  Push para a branch (`git push origin feature/nova-feature`).
6.  Abra um Pull Request.

## Checklist

- [ ] Fork do repositorio
- [ ] Branch para sua feature (`git checkout -b feature/nome`)
- [ ] Commits com mensagens claras
- [ ] Testes passando (`pytest src/tests/`)
- [ ] Pre-commit passando
- [ ] PR com template preenchido
