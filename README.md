<div align="center">

[![Licença](https://img.shields.io/badge/licença-GPL--3.0-blue.svg)](https://opensource.org/licenses/GPL-3.0)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Estrelas](https://img.shields.io/github/stars/AndreBFarias/FogStripper.svg?style=social)](https://github.com/AndreBFarias/FogStripper/stargazers)
[![Contribuições](https://img.shields.io/badge/contribuições-bem--vindas-brightgreen.svg)](https://github.com/AndreBFarias/FogStripper/issues)

<div style="text-align: center;">
  <h1 style="font-size: 2em;">FogStripper</h1>
  <img src="https://raw.githubusercontent.com/AndreBFarias/FogStripper-Removedor-Background/main/assets/desnudador.png" width="200" alt="Logo do FogStripper">
</div>
</div>

Uma aplicação gráfica que remove fundos de imagens com um toque neural, baseada no modelo U2Net e acelerada por GPU via CUDA. Open source, desenhada para quem busca eficiência e privacidade.

---

## Pré-requisitos

Antes de instalar, garanta que seu sistema atende aos seguintes requisitos:

1.  **Python**: Versão `3.8` ou superior.
2.  **Hardware**: Placa de vídeo NVIDIA com suporte a CUDA é altamente recomendada para o melhor desempenho.
3.  **Dependências de Sistema (para Debian/Ubuntu/Pop!_OS)**: A interface gráfica depende de algumas bibliotecas de sistema que podem não vir instaladas por padrão. Execute o comando abaixo para instalá-las:
    ```bash
    sudo apt update && sudo apt install libxcb1-dev
    ```

---

## Instalação

Com os pré-requisitos atendidos, a instalação é simples. Clone o repositório e execute o script de instalação:

```bash
# 1. Clone o repositório
git clone [https://github.com/AndreBFarias/FogStripper-Removedor-Background.git](https://github.com/AndreBFarias/FogStripper-Removedor-Background.git)

# 2. Entre no diretório
cd FogStripper-Removedor-Background

# 3. Dê permissão de execução e rode o script
chmod +x install.sh
./install.sh
```


O script criará um ambiente isolado para a aplicação, instalará todas as dependências do Python e criará um atalho no menu de aplicativos do seu sistema.

---

## Uso

Após a instalação, procure por **"FogStripper"** no seu menu de aplicativos e inicie-o.

- Arraste e solte as imagens na janela ou use o botão "Selecione Imagens".
    
- Ajuste o controle "Potência da GPU" para refinar o recorte.
    
- As imagens processadas serão salvas na mesma pasta das originais com o sufixo `_despido.png`.
    

---

## Desinstalação

Para remover completamente a aplicação, execute o script de desinstalação:

Bash

```
# No diretório do projeto
chmod +x uninstall.sh
./uninstall.sh
```


## Dependências do Projeto

As dependências do Python estão listadas no arquivo

`requirements.txt` e são gerenciadas automaticamente pelo script de instalação.

- **PyQt6**: Para a interface gráfica.
    
- **rembg[gpu]**: Para a remoção de fundo com aceleração de GPU.
    
- **Pillow**: Para a manipulação de imagens.


### Licença GLP
Livre para modificar e usar da forma que preferir desde que tudo permaneça livre.


As dependências do Python estão listadas no arquivo

`requirements.txt` e são gerenciadas automaticamente pelo script de instalação.

- **PyQt6**: Para a interface gráfica.
    
- **rembg[gpu]**: Para a remoção de fundo com aceleração de GPU.
    
- **Pillow**: Para a manipulação de imagens.


### Licença GLP
Livre para modificar e usar da forma que preferir desde que tudo permaneça livre.
