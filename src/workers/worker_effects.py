import argparse
import sys
from argparse import Namespace

from PIL import Image, ImageFilter


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Aplica um efeito de sombra a uma imagem.")
    parser.add_argument("--input", required=True, help="Caminho para a imagem de entrada (com fundo transparente).")
    parser.add_argument("--output", required=True, help="Caminho para salvar a imagem final com a sombra.")
    parser.add_argument("--blur-radius", type=int, default=15, help="Raio do desfoque da sombra.")
    parser.add_argument("--offset-x", type=int, default=10, help="Deslocamento horizontal da sombra.")
    parser.add_argument("--offset-y", type=int, default=10, help="Deslocamento vertical da sombra.")
    parser.add_argument("--opacity", type=int, default=180, help="Opacidade da sombra (0-255).")

    args: Namespace = parser.parse_args()

    try:
        blur_radius: int = args.blur_radius
        offset_x: int = args.offset_x
        offset_y: int = args.offset_y
        shadow_color: tuple[int, int, int, int] = (0, 0, 0, max(0, min(255, args.opacity)))

        original_img: Image.Image = Image.open(args.input).convert("RGBA")

        alpha_mask: Image.Image = original_img.getchannel("A")

        solid_shadow: Image.Image = Image.new("RGBA", original_img.size, color=shadow_color)
        solid_shadow.putalpha(alpha_mask)

        blurred_shadow: Image.Image = solid_shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        new_width: int = original_img.width + abs(offset_x) + blur_radius * 2
        new_height: int = original_img.height + abs(offset_y) + blur_radius * 2

        final_canvas: Image.Image = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))

        shadow_paste_pos: tuple[int, int] = (blur_radius + offset_x, blur_radius + offset_y)
        image_paste_pos: tuple[int, int] = (blur_radius, blur_radius)

        final_canvas.paste(blurred_shadow, shadow_paste_pos, blurred_shadow)
        final_canvas.paste(original_img, image_paste_pos, original_img)

        final_canvas.save(args.output)
        print(f"Worker de efeitos concluiu. Sombra aplicada e salva em: {args.output}")

    except FileNotFoundError as e:
        sys.stderr.write(f"ERRO: Arquivo não encontrado: {e.filename}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"ERRO inesperado no worker de efeitos: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
