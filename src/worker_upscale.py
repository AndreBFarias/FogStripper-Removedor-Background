import argparse
import numpy as np
from PIL import Image
from realesrgan import RealESRGAN
from basicsr.archs.rrdbnet_arch import RRDBNet

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--tile", type=int, default=512)
    args = parser.parse_args()

    try:
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        upscaler = RealESRGAN(scale=4, model_path='weights/RealESRGAN_x4plus.pth', model=model, half=True, tile=args.tile)
        
        with Image.open(args.input) as img:
            img = img.convert("RGBA")
            rgb_img = img.convert('RGB')
            alpha = img.split()[-1]

            rgb_np = np.array(rgb_img)
            upscaled_rgb_np, _ = upscaler.enhance(rgb_np)
            
            output_img_rgb = Image.fromarray(upscaled_rgb_np)
            alpha_resized = alpha.resize(output_img_rgb.size, Image.LANCZOS)
            output_img_rgb.putalpha(alpha_resized)
                
            output_img_rgb.save(args.output)
        print(f"Upscale worker concluído.")
    except Exception as e:
        print(f"Erro no upscale worker: {e}")
        exit(1)

if __name__ == "__main__":
    main()
