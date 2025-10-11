<div align="center">

[![opensource](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](#)
[![licença](https://img.shields.io/badge/licença-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![Estrelas](https://img.shields.io/github/stars/AndreBFarias/FogStripper.svg?style=social)](https://github.com/AndreBFarias/FogStripper/stargazers)
[![Contribuições](https://img.shields.io/badge/contribuições-bem--vindas-brightgreen.svg)](CONTRIBUTING.md)
---
<h1 style="font-size: 2em;">FogStripper</h1>
<img src="https://raw.githubusercontent.com/AndreBFarias/FogStripper-Removedor-Background/main/assets/icon.png" width="120" alt="Ícone do FogStripper">


---
</div>

Uma aplicação gráfica para Linux forjada para sobreviver à entropia. Remove fundos de imagens e vídeos usando modelos de redes neurais que rodam localmente, com uma arquitetura modularizada que permite estabilidade e evita problemas de conflitos.

---

<img src="https://raw.githubusercontent.com/AndreBFarias/FogStripper-Removedor-Background/main/assets/Fogstripper.png" width="700" alt="Screenshot do FogStripper">

### Funcionalidades

- **Remoção de Fundo com IA:** Múltiplos modelos (`rembg`) para diferentes tipos de imagem.
- **Upscaling 4x Opcional:** Melhore a resolução e a qualidade da imagem final com `Real-ESRGAN`.
- **Suporte a Animações:** Processe GIFs e WEBMs, extraindo e tratando cada quadro individualmente.
- **Controle Fino de Recursos:**
    - **Potência (Borda):** Ajuste a agressividade do recorte para preservar detalhes finos ou garantir bordas limpas.
    - **Bloco (VRAM):** Controle o tamanho dos "tiles" do upscale para gerenciar o uso de VRAM e evitar erros em GPUs com menos memória.
- **Interface Intuitiva:** Arraste e solte, com feedback claro e diálogos informativos de erro.
- **Arquitetura Resiliente:** A estabilidade é garantida por um sistema de três ambientes Python (`venv`) isolados, orquestrados para trabalhar em harmonia sem nunca entrarem em conflito.

### A Arquitetura

O FogStripper tem três módulos principais. A estabilidade foi alcançada ao reconhecer que as bibliotecas de redes neurais modernas.

1.  **Interface (`venv_gui`):** Onde a alma da aplicação (PyQt6) reside. Leve e ágil.
2.  **Remoção da Névoa (`venv_rembg`):** Módulo isolado para `rembg`, que depende de um ecossistema específico de bibliotecas.
3.  **Reino da Ampliação (`venv_upscale`):** Um universo congelado no tempo para `realesrgan` e suas versões precisas de `torch` e `numpy`, imune às quebras de compatibilidade do futuro.

Esta separação, forçada pelo script `install.sh`, é a razão pela qual o FogStripper funciona de forma consistente.

### Instalação

O script de instalação automatiza a criação de todos os reinos e dependências. Requer uma conexão com a internet.


```bash
# Clone este repositório
git clone [https://github.com/AndreBFarias/FogStripper-Removedor-Background.git](https://github.com/AndreBFarias/FogStripper-Removedor-Background.git)
cd FogStripper-Removedor-Background

# Torne o instalador executável e execute-o
chmod +x install.sh
./install.sh

### Dependências do Projeto

As dependências do Python estão listadas no arquivo `requirements.txt` e são gerenciadas automaticamente pelo script de instalação.
- **PyQt6** : Para a interface gráfica.
    
- **rembg[gpu]** :  Para a remoção de fundo com aceleração de GPU.
    
- **Pillow** : Para a manipulação de imagens.

### Uso
- Arraste e solte imagens na janela ou clique em "Selecione Imagens".
- Ajuste a potência da GPU com o slider, sentindo o controle pulsar.
- A imagem processada surge com o sufixo _despido.png, e uma mensagem te guia até a pasta de saída.

### Licença GLP
Livre para modificar e usar da forma que preferir desde que tudo permaneça livre.

