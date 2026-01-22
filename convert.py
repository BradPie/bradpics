# /// script
# dependencies = [
#   "pillow",
# ]
# ///

import argparse
import sys
from pathlib import Path
from PIL import Image

def get_extension(output_format: str) -> str:
    if output_format == 'jpeg':
        return '.jpg'
    elif output_format == 'webp':
        return '.webp'
    elif output_format in ('png', 'png8'):
        return '.png'
    return ''

def convert_single_file(source_path: Path, dest_path: Path, output_format: str) -> bool:
    """Converts a single image file. Returns True on success, False on failure."""
    try:
        with Image.open(source_path) as img:
            # Handle JPEG transparency
            if output_format == 'jpeg':
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
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
                img_p = img.convert("P", palette=Image.ADAPTIVE, colors=256)
                img_p.save(dest_path, format="PNG")

            print(f"Success: {source_path} -> {dest_path}")
            return True

    except Exception as e:
        print(f"Error converting {source_path}: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Image conversion utility")
    parser.add_argument("source", help="Source image path or directory")
    parser.add_argument("destination", help="Destination image path or directory")
    parser.add_argument("--format", choices=["jpeg", "webp", "png8", "png"], required=True, help="Output format")

    args = parser.parse_args()

    source = Path(args.source)
    dest = Path(args.destination)
    fmt = args.format
    ext = get_extension(fmt)

    if not source.exists():
        print(f"Error: Source '{source}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if source.is_dir():
        # Directory to Directory conversion
        dest.mkdir(parents=True, exist_ok=True)
        count = 0
        files = sorted(list(source.iterdir()))
        for file_path in files:
            if file_path.is_file():
                # Try to see if it's an image by extension first to avoid unnecessary errors
                if file_path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tiff'):
                    target_path = dest / file_path.with_suffix(ext).name
                    if convert_single_file(file_path, target_path, fmt):
                        count += 1
        print(f"Done: Converted {count} images.")
    else:
        # File to ... conversion
        if dest.is_dir():
            # If destination is a directory, use source filename with new extension
            target_path = dest / source.with_suffix(ext).name
        else:
            # Ensure parent directory exists
            dest.parent.mkdir(parents=True, exist_ok=True)
            target_path = dest

        if not convert_single_file(source, target_path, fmt):
            sys.exit(1)

if __name__ == "__main__":
    main()
