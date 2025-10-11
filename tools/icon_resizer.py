from PIL import Image
import os
import sys

def resize_icon(source_path, output_dir, sizes):
    """
    Redimensiona o ícone para múltiplos tamanhos e salva no diretório de saída.
    """
    try:
        img = Image.open(source_path).convert("RGBA")
    except FileNotFoundError:
        print(f"Erro: Arquivo de ícone original não encontrado em '{source_path}'")
        sys.exit(1)
        
    os.makedirs(output_dir, exist_ok=True)
    base_name = "icon" 
    
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        output_path = os.path.join(output_dir, f"{base_name}_{size}x{size}.png")
        resized.save(output_path, "PNG")
        print(f"Ícone salvo em {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 icon_resizer.py <caminho_raiz_do_projeto>")
        sys.exit(1)
        
    project_root = sys.argv[1]
    source = os.path.join(project_root, "assets", "icon.png")
    output = os.path.join(project_root, "assets", "generated_icons")
    sizes = [16, 32, 64, 128]
    
    resize_icon(source, output, sizes)
