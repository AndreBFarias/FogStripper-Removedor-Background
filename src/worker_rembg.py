import argparse
from rembg import remove, new_session
from PIL import Image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="u2net")
    parser.add_argument("--potencia", type=int, default=75)
    args = parser.parse_args()

    try:
        erode_size = 5 + int((args.potencia / 100) * 35)
        bg_threshold = 15 - int((args.potencia / 100) * 20)
        
        session = new_session(args.model)
        with Image.open(args.input) as img:
            output_img = remove(img, 
                                session=session,
                                alpha_matting=True,
                                alpha_matting_foreground_threshold=240,
                                alpha_matting_background_threshold=bg_threshold,
                                alpha_matting_erode_size=erode_size)
            output_img.save(args.output)
        print(f"Rembg worker concluído.")
    except Exception as e:
        print(f"Erro no rembg worker: {e}")
        exit(1)

if __name__ == "__main__":
    main()
