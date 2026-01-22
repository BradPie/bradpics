# /// script
# dependencies = [
#   "pillow",
# ]
# ///

import argparse
import sys
from pathlib import Path
from PIL import Image

def convert_image(source_path: Path, dest_path: Path, output_format: str):
    if not source_path.exists():
        print(f"Error: Source file '{source_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        with Image.open(source_path) as img:
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if output_format == 'jpeg':
                # JPEG doesn't support alpha channel
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    # Create a white background for transparent images
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")

                    if img.mode == "RGBA":
                        background.paste(img, mask=img.split()[3])
                    elif img.mode == "LA":
                        background.paste(img, mask=img.split()[1])
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(dest_path, format="JPEG")

            elif output_format == 'webp':
                img.save(dest_path, format="WEBP")

            elif output_format == 'png':
                img.save(dest_path, format="PNG")

            elif output_format == 'png8':
                # Convert to palette mode (8-bit)
                img_p = img.convert("P", palette=Image.ADAPTIVE, colors=256)
                img_p.save(dest_path, format="PNG")

            print(f"Success: {source_path} -> {dest_path} ({output_format})")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Image conversion utility")
    parser.add_argument("source", help="Source image path")
    parser.add_argument("destination", help="Destination image path")
    parser.add_argument("--format", choices=["jpeg", "webp", "png8", "png"], required=True, help="Output format")

    args = parser.parse_args()

    convert_image(Path(args.source), Path(args.destination), args.format)

if __name__ == "__main__":
    main()
