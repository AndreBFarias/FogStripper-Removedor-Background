# Configuracao

## Arquivos de Configuracao

### config.json

Localizado em `~/.local/share/fogstripper/config.json`:

```json
{
  "venv_rembg": "/caminho/para/venv_rembg",
  "venv_upscale": "/caminho/para/venv_upscale"
}
```

### Modo Desenvolvimento

Para usar configuracao local, defina a variavel de ambiente:

```bash
export FOGSTRIPPER_DEV_MODE=1
python src/main.py
```

Isso ira usar `config.dev.json` no diretorio do projeto.

## Logs

Os logs sao salvos em `~/.local/share/fogstripper/app.log`.

Para ver logs em tempo real:

```bash
tail -f ~/.local/share/fogstripper/app.log
```

## Variaveis de Ambiente

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `FOGSTRIPPER_DEV_MODE` | Modo desenvolvimento | `0` |
| `CUDA_VISIBLE_DEVICES` | GPU a usar | `0` |

## Modelos Disponiveis

Os modelos sao baixados automaticamente na primeira execucao:

| Modelo | Tamanho | Download |
|--------|---------|----------|
| u2net | ~176MB | Automatico |
| u2net_human_seg | ~176MB | Automatico |
| isnet-general-use | ~174MB | Automatico |
| sam | ~2.4GB | Automatico |

Os modelos ficam em cache em `~/.u2net/`.

## Tile Size

O parametro tile_size controla o tamanho dos blocos para upscale:

- **256**: Menos memoria, mais lento
- **512**: Balanceado (padrao)
- **1024**: Mais memoria, mais rapido

Ajuste conforme sua GPU:

| VRAM | Tile Size Recomendado |
|------|----------------------|
| 4GB | 256 |
| 6GB | 512 |
| 8GB+ | 1024 |
