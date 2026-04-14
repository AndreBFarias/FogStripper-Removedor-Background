import argparse
import os
from argparse import Namespace
from pathlib import Path

_MODELS_DIR = Path(
    os.environ.get(
        "U2NET_HOME",
        str(Path.home() / ".local" / "share" / "fogstripper" / "models" / "u2net"),
    )
)
os.environ["U2NET_HOME"] = str(_MODELS_DIR)
_MODELS_DIR.mkdir(parents=True, exist_ok=True)

from PIL import Image
from rembg import new_session, remove


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="u2net")
    parser.add_argument("--potencia", type=int, default=75)
    args: Namespace = parser.parse_args()

    try:
        erode_size: int = 5 + int((args.potencia / 100) * 35)
        bg_threshold: int = 15 - int((args.potencia / 100) * 20)

        session = new_session(args.model)
        with Image.open(args.input) as img:
            output_img = remove(
                img,
                session=session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=bg_threshold,
                alpha_matting_erode_size=erode_size,
            )
            output_img.save(args.output)
        print("Rembg worker concluído.")
    except Exception as e:
        print(f"Erro no rembg worker: {e}")
        exit(1)


if __name__ == "__main__":
    main()
