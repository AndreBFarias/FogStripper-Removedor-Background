import argparse
import sys
from PIL import Image, ImageFilter

def main():
    """
    Worker para aplicar um efeito de sombra projetada a uma imagem com canal alfa.
    """
    parser = argparse.ArgumentParser(description="Aplica um efeito de sombra a uma imagem.")
    parser.add_argument("--input", required=True, help="Caminho para a imagem de entrada (com fundo transparente).")
    parser.add_argument("--output", required=True, help="Caminho para salvar a imagem final com a sombra.")

    args = parser.parse_args()

    try:

        blur_radius = 15
        offset_x = 10
        offset_y = 10
        shadow_color = (0, 0, 0, 180) 

        original_img = Image.open(args.input).convert("RGBA")

        alpha_mask = original_img.getchannel('A')

        shadow_base = Image.new('RGBA', original_img.size, (0, 0, 0, 0))
        shadow_base.putalpha(Image.new('L', original_img.size, color=shadow_color[3])) 

        solid_shadow = Image.new('RGBA', original_img.size, color=shadow_color)
        solid_shadow.putalpha(alpha_mask)

        blurred_shadow = solid_shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        new_width = original_img.width + abs(offset_x) + blur_radius * 2
        new_height = original_img.height + abs(offset_y) + blur_radius * 2

        final_canvas = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))

        shadow_paste_pos = (blur_radius + offset_x, blur_radius + offset_y)
        image_paste_pos = (blur_radius, blur_radius)

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
