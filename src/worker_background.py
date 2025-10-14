import argparse
import sys
from PIL import Image

def main():
    """
    Worker para aplicar um fundo (cor sólida ou imagem) a uma imagem com canal alfa.
    """
    parser = argparse.ArgumentParser(description="Aplica um fundo a uma imagem.")
    parser.add_argument("--input", required=True, help="Caminho para a imagem de entrada (com fundo transparente).")
    parser.add_argument("--output", required=True, help="Caminho para salvar a imagem final.")
    parser.add_argument("--bg-type", required=True, choices=['color', 'image'], help="Tipo de fundo a ser aplicado.")
    parser.add_argument("--bg-data", required=True, help="Dado do fundo: código hexadecimal da cor (ex: '#FFFFFF') ou caminho para a imagem de fundo.")
    parser.add_argument("--resize-mode", default='fit-bg-to-fg', choices=['fit-bg-to-fg', 'fit-fg-to-bg'], help="Modo de redimensionamento do fundo.")
    
    args = parser.parse_args()

    try:
        foreground = Image.open(args.input).convert("RGBA")

        if args.bg_type == 'color':
            background = Image.new("RGBA", foreground.size, args.bg_data)
            final_canvas = background
        
        elif args.bg_type == 'image':
            background = Image.open(args.bg_data).convert("RGBA")
            
            if args.resize_mode == 'fit-bg-to-fg':
                # Modo antigo: redimensiona o fundo para o tamanho do objeto
                resized_bg = background.resize(foreground.size, Image.Resampling.LANCZOS)
                final_canvas = resized_bg
            else: # 'fit-fg-to-bg'
                # Modo novo: usa o fundo como tela e centraliza o objeto
                final_canvas = Image.new("RGBA", background.size, (0, 0, 0, 0))
                final_canvas.paste(background, (0,0))

        # Define a posição para colar o objeto
        if args.bg_type == 'image' and args.resize_mode == 'fit-fg-to-bg':
            # Centraliza o objeto na tela de fundo
            bg_w, bg_h = final_canvas.size
            fg_w, fg_h = foreground.size
            offset = ((bg_w - fg_w) // 2, (bg_h - fg_h) // 2)
            final_canvas.paste(foreground, offset, foreground)
        else:
            # Cola o objeto preenchendo toda a tela
            final_canvas.paste(foreground, (0, 0), foreground)
        
        final_canvas.save(args.output)
        print(f"Worker de fundo concluiu. Imagem salva em: {args.output}")

    except FileNotFoundError as e:
        sys.stderr.write(f"ERRO: Arquivo não encontrado: {e.filename}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"ERRO inesperado no worker de fundo: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()

