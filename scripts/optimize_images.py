#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from PIL import Image


def optimize_png(image_path: Path, max_size: int = 2048) -> None:
    """
    Otimiza um arquivo PNG redimensionando e comprimindo.

    Args:
        image_path: Caminho para o arquivo PNG
        max_size: Tamanho máximo para largura/altura
    """
    try:
        with Image.open(image_path) as img:
            original_size = os.path.getsize(image_path)
            width, height = img.size

            needs_resize = width > max_size or height > max_size

            if needs_resize:
                ratio = min(max_size / width, max_size / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)

                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"  Redimensionado: {width}x{height} -> {new_width}x{new_height}")

            img = img.convert("RGBA")

            img.save(image_path, "PNG", optimize=True, compress_level=9)

            new_size = os.path.getsize(image_path)
            reduction = ((original_size - new_size) / original_size) * 100

            print(f"  Tamanho: {original_size} -> {new_size} bytes ({reduction:.1f}% redução)")

    except Exception as e:
        print(f"  ERRO: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 optimize_images.py <diretorio_raiz>")
        sys.exit(1)

    root_dir = Path(sys.argv[1])

    if not root_dir.exists():
        print(f"Erro: Diretório '{root_dir}' não encontrado")
        sys.exit(1)

    assets_dir = root_dir / "assets"

    if not assets_dir.exists():
        print(f"Erro: Pasta assets não encontrada em '{root_dir}'")
        sys.exit(1)

    png_files = [assets_dir / "icon.png", assets_dir / "Fogstripper.png"]

    print("Otimizando imagens PNG...")

    for png_file in png_files:
        if png_file.exists():
            print(f"\nProcessando: {png_file.name}")
            optimize_png(png_file, max_size=2048)
        else:
            print(f"\nAVISO: {png_file.name} não encontrado, pulando...")

    print("\nOtimização concluída!")


if __name__ == "__main__":
    main()
