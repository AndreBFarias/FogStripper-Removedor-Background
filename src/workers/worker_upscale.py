import argparse
import sys
import traceback
from argparse import Namespace

import numpy as np
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from numpy.typing import NDArray
from PIL import Image
from realesrgan import RealESRGANer


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--tile", type=int, default=512)
    parser.add_argument("--outscale", type=int, default=4, help="Fator de escala final da imagem.")
    args: Namespace = parser.parse_args()

    try:
        model: RRDBNet = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        model_path: str = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"

        upsampler: RealESRGANer = RealESRGANer(
            scale=4,
            model_path=model_path,
            dni_weight=None,
            model=model,
            tile=args.tile,
            tile_pad=10,
            pre_pad=0,
            half=torch.cuda.is_available(),
            gpu_id=None,
        )

        with Image.open(args.input) as img:
            img = img.convert("RGBA")
            rgb_img: Image.Image = img.convert("RGB")
            alpha: Image.Image = img.split()[-1]

            rgb_np: NDArray[np.uint8] = np.array(rgb_img, dtype=np.uint8)

            upscaled_rgb_np: NDArray[np.uint8]
            upscaled_rgb_np, _ = upsampler.enhance(rgb_np, outscale=args.outscale)

            output_img_rgb: Image.Image = Image.fromarray(upscaled_rgb_np)
            alpha_resized: Image.Image = alpha.resize(output_img_rgb.size, Image.Resampling.LANCZOS)
            output_img_rgb.putalpha(alpha_resized)

            output_img_rgb.save(args.output)
        print(f"Upscale worker concluído para a escala {args.outscale}x.")
    except Exception:
        detailed_error: str = traceback.format_exc()
        sys.stderr.write("--- CONFISSÃO DO SERVO UPSCALE ---\n")
        sys.stderr.write(detailed_error)
        sys.stderr.write("--- FIM DA CONFISSÃO ---\n")
        exit(1)


if __name__ == "__main__":
    main()
