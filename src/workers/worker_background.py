import argparse
import sys
from argparse import Namespace

from PIL import Image


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Aplica um fundo a uma imagem.")
    parser.add_argument("--input", required=True, help="Caminho para a imagem de entrada (com fundo transparente).")
    parser.add_argument("--output", required=True, help="Caminho para salvar a imagem final.")
    parser.add_argument("--bg-type", required=True, choices=["color", "image"], help="Tipo de fundo a ser aplicado.")
    parser.add_argument(
        "--bg-data",
        required=True,
        help="Dado do fundo: código hexadecimal da cor (ex: '#FFFFFF') ou caminho para a imagem de fundo.",
    )
    parser.add_argument(
        "--resize-mode",
        default="fit-bg-to-fg",
        choices=["fit-bg-to-fg", "fit-fg-to-bg"],
        help="Modo de redimensionamento do fundo.",
    )

    args: Namespace = parser.parse_args()

    try:
        foreground: Image.Image = Image.open(args.input).convert("RGBA")

        if args.bg_type == "color":
            background: Image.Image = Image.new("RGBA", foreground.size, args.bg_data)
            final_canvas: Image.Image = background

        elif args.bg_type == "image":
            background = Image.open(args.bg_data).convert("RGBA")

            if args.resize_mode == "fit-bg-to-fg":
                resized_bg: Image.Image = background.resize(foreground.size, Image.Resampling.LANCZOS)
                final_canvas = resized_bg
            else:
                final_canvas = Image.new("RGBA", background.size, (0, 0, 0, 0))
                final_canvas.paste(background, (0, 0))

        if args.bg_type == "image" and args.resize_mode == "fit-fg-to-bg":
            bg_w: int
            bg_h: int
            bg_w, bg_h = final_canvas.size
            fg_w: int
            fg_h: int
            fg_w, fg_h = foreground.size
            offset: tuple[int, int] = ((bg_w - fg_w) // 2, (bg_h - fg_h) // 2)
            final_canvas.paste(foreground, offset, foreground)
        else:
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
