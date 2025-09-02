<div align="center">

[![Licença](https://img.shields.io/badge/licença-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Estrelas](https://img.shields.io/github/stars/AndreBFarias/FogStripper.svg?style=social)](https://github.com/AndreBFarias/FogStripper/stargazers)
[![Contribuições](https://img.shields.io/badge/contribuições-bem--vindas-brightgreen.svg)](https://github.com/AndreBFarias/FogStripper/issues)

<div style="text-align: center;">
  <h1 style="font-size: 2em;">FogStripper - Removedor de Background</h1>
  <img src="https://raw.githubusercontent.com/AndreBFarias/FogStripper/main/assets/desnudador.png" width="200" alt="Screenshot do FogStripper" text-align = "center">
</div>
</div>
Uma aplicação gráfica que desnuda fundos de imagens com um toque neural, baseada no modelo U2Net e acelerada por GPU via CUDA. Open source, desenhada para quem busca eficiência e privacidade em cada camada revelada.
---
<div style="text-align: center;">
  <h3 style="font-size: 2em;">Interface</h3>
  <img src="https://raw.githubusercontent.com/AndreBFarias/FogStripper-Removedor-Background/main/assets/Fogstripper.png" width="600" alt="Screenshot do FogStripper" style="display: block; margin: 0 auto;">
</div>

---

### Pré-requisitos

- Python 3.8 ou superior.
- Placa de vídeo NVIDIA com suporte a CUDA (recomendado para um desempenho que seduz).
- Modelo U2Net (u2net.onnx).

### Instalação

```bash
# Clone o repositório:
git clone https://github.com/AndreBFarias/FogStripper.git
cd FogStripper
# Crie um ambiente virtual e instale as dependências:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Execute a aplicação:
python main.py 
```
### Para Remover
```
chmod +x uninstall.sh
./uninstall.sh
```

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
