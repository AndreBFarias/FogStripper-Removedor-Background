import argparse
import numpy as np
import torch
from PIL import Image
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact
#1
import traceback
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--tile", type=int, default=512)
    args = parser.parse_args()

    try:
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        model_path = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
        
        upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            dni_weight=None,
            model=model,
            tile=args.tile,
            tile_pad=10,
            pre_pad=0,
            half=torch.cuda.is_available(),
            gpu_id=None)

        with Image.open(args.input) as img:
            img = img.convert("RGBA")
            rgb_img = img.convert('RGB')
            alpha = img.split()[-1]

            rgb_np = np.array(rgb_img, dtype=np.uint8)
            
            upscaled_rgb_np, _ = upsampler.enhance(rgb_np, outscale=4)
            
            output_img_rgb = Image.fromarray(upscaled_rgb_np)
            alpha_resized = alpha.resize(output_img_rgb.size, Image.Resampling.LANCZOS)
            output_img_rgb.putalpha(alpha_resized)
                
            output_img_rgb.save(args.output)
        print(f"Upscale worker concluído.")
    #1
    except Exception:
        # Interrogatório: Força o servo a confessar a causa exata da sua morte para o stderr.
        detailed_error = traceback.format_exc()
        sys.stderr.write("--- CONFISSÃO DO SERVO ---\n")
        sys.stderr.write(detailed_error)
        sys.stderr.write("--- FIM DA CONFISSÃO ---\n")
        exit(1)

if __name__ == "__main__":
    main()
