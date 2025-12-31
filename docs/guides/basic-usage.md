# Uso Basico

## Iniciando a Aplicacao

```bash
source venv/bin/activate
python src/main.py
```

## Interface

A interface e dividida em:

1. **Area de entrada** - Arraste imagens ou clique para selecionar
2. **Configuracoes** - Modelo, potencia, formato de saida
3. **Pos-processamento** - Upscale, sombra, fundo
4. **Barra de progresso** - Status do processamento

## Fluxo de Trabalho

### 1. Selecionar Imagem

- Arraste uma imagem para a janela
- Ou clique no botao "Selecionar Arquivo"

Formatos suportados: PNG, JPG, WEBP, GIF, MP4, MOV

### 2. Configurar Modelo

| Modelo | Uso Recomendado |
|--------|-----------------|
| u2net | Uso geral, boa qualidade |
| isnet-general-use | Objetos diversos |
| sam | Segmentacao precisa |
| u2net_human_seg | Pessoas/retratos |

### 3. Ajustar Potencia

O slider de potencia (0-100) controla a agressividade da remocao:

- **Baixa (0-30)**: Preserva mais detalhes, pode deixar residuos
- **Media (30-70)**: Balanceado
- **Alta (70-100)**: Remocao agressiva, pode perder detalhes finos

### 4. Pos-Processamento (Opcional)

#### Upscale

Aumenta a resolucao da imagem:

- 2x: Dobra a resolucao
- 4x: Quadruplica a resolucao

!!! warning "Atencao"
    Upscale requer GPU NVIDIA com CUDA para desempenho aceitavel.

#### Sombra

Adiciona sombra drop shadow ao objeto:

- Offset: 10px
- Blur: 15px
- Cor: Preto com 70% opacidade

#### Fundo Customizado

- **Cor solida**: Selecione uma cor hex (#FFFFFF)
- **Imagem**: Selecione uma imagem de fundo

### 5. Processar

Clique em "Processar" e aguarde. O arquivo original sera preservado como `.bak`.

## Formatos de Saida

| Formato | Caracteristicas |
|---------|-----------------|
| PNG | Transparencia, sem perda |
| WEBP | Menor tamanho, transparencia |
| SVG | Vetorial, escalavel |
| GIF | Animacoes |

## Dicas

1. Para melhores resultados, use imagens com bom contraste entre objeto e fundo
2. O modelo `u2net_human_seg` funciona melhor para fotos de pessoas
3. Use potencia mais baixa para objetos com bordas suaves (cabelo, pelo)
