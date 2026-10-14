
import csv
from pathlib import Path

from PIL import Image, ImageDraw

OUTPUT_DIR = Path("data/evaluation/demo")
IMAGES_DIR = OUTPUT_DIR / "images"


def save_image(name: str, image: Image.Image, image_format: str = "PNG") -> Path:
    path = IMAGES_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format=image_format)

    return path


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Synthetic image with a large, centered product-like shape.
    base = Image.new("RGB", (800, 800), (235, 235, 235))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle((250, 150, 550, 650), radius=35, fill=(30, 100, 180))
    draw.ellipse((330, 220, 470, 360), fill=(230, 180, 50))

    base_path = save_image("item_a.png", base)

    # Same visual content with a different resolution and JPEG encoding.
    recompressed = base.resize((400, 400))
    recompressed_path = save_image(
        "item_a_recompressed.jpg",
        recompressed,
        image_format="JPEG",
    )

    # Visually distinct synthetic product.
    different = Image.new("RGB", (800, 800), (245, 245, 245))
    different_draw = ImageDraw.Draw(different)
    different_draw.rectangle((150, 250, 650, 550), fill=(190, 40, 45))
    different_draw.ellipse((300, 300, 500, 500), fill=(30, 150, 70))
    different_path = save_image("item_b.png", different)

    manifest_path = OUTPUT_DIR / "manifest.csv"
    
    with manifest_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "image_a", "image_b", "is_duplicate"])
        writer.writerow([
            "same_file",
            "images/item_a.png",
            "images/item_a.png",
            "true",
        ])
        writer.writerow([
            "recompressed_copy",
            "images/item_a.png",
            "images/item_a_recompressed.jpg",
            "true",
        ])
        writer.writerow([
            "different_products",
            "images/item_a.png",
            "images/item_b.png",
            "false",
        ])

    print(f"Manifest created: {manifest_path}")
    print(f"Created images: {base_path}, {recompressed_path}, {different_path}")


if __name__ == "__main__":
    main()
