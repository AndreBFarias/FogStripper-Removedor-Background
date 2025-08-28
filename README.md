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

## Pré-requisitos

- Python 3.8 ou superior.
- Placa de vídeo NVIDIA com suporte a CUDA (recomendado para um desempenho que seduz).
- Modelo U2Net (u2net.onnx).

## Instalação

```bash
# Clone o repositório:
git clone https://github.com/AndreBFarias/FogStripper-Removedor-Background.git
cd FogStripper
# Crie um ambiente virtual e instale as dependências:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Execute a aplicação:
python main.py 
```

### Uso
- Arraste e solte imagens na janela ou clique em "Selecione Imagens".
- Ajuste a potência da GPU com o slider, sentindo o controle pulsar.
- A imagem processada surge com o sufixo _despido.png, e uma mensagem te guia até a pasta de saída.


### Dependências
As musas deste ritual incluem:
- PyQt6 para a interface que hipnotiza.
- rembg[gpu] para remover fundos com poder bruto.
- Pillow para manipular cada curva da imagem.

### Licença GPL 
> Livre para modificar e ser entregue aos desejos desde que tudo permaneça livre.
