<div align="center">

[![opensource](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](#)
[![licença](https://img.shields.io/badge/licença-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Estrelas](https://img.shields.io/github/stars/AndreBFarias/FogStripper.svg?style=social)](https://github.com/AndreBFarias/FogStripper/stargazers)
[![Contribuições](https://img.shields.io/badge/contribuições-bem--vindas-brightgreen.svg)](https://github.com/AndreBFarias/FogStripper/issues)

<div align="center">
  <h1 style="font-size: 2em;">FogStripper v2.0</h1>
  <img src="https://raw.githubusercontent.com/AndreBFarias/FogStripper-Removedor-Background/main/assets/Fogstripper.png" width="700" alt="Screenshot do FogStripper">
</div>

Uma aplicação gráfica para Linux que remove fundos de imagens usando IA, com uma arquitetura de "Reinos Isolados" para garantir máxima estabilidade e evitar conflitos de dependências.

### Funcionalidades
- **Remoção de Fundo com IA:** Múltiplos modelos à sua escolha para diferentes tipos de imagem.
- **Upscaling 4x Opcional:** Melhore a qualidade e a resolução da imagem final com Real-ESRGAN.
- **Controle de Recursos:** Ajuste a "Potência" do recorte e o "Tamanho do Bloco" do upscale para gerenciar o uso de VRAM.
- **Interface Intuitiva:** Arraste e solte, com pop-ups de confirmação e conclusão.
- **Arquitetura Robusta:** Três ambientes Python (`venv`) isolados para a Interface, o `rembg` e o `realesrgan`, orquestrados por um processo principal.

---

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

