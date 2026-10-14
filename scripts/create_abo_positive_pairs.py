import csv
from pathlib import Path

from PIL import Image, ImageOps

DATA_DIR = Path("data/evaluation/abo")
SOURCE_MANIFEST = DATA_DIR / "candidate_pairs.csv"
OUTPUT_MANIFEST = DATA_DIR / "controlled_positive_manifest.csv"
TRANSFORM_DIR = DATA_DIR / "positive_images"

MAX_IMAGES = 20
MAX_SIDE = 128
JPEG_QUALITY = 70


def main() -> None:
    with SOURCE_MANIFEST.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        rows = list(csv.DictReader(file))

    # Seleccionar imágenes originales únicas.
    source_paths = sorted({
        row[column]
        for row in rows
        for column in ("image_a_path", "image_b_path")
    })[:MAX_IMAGES]

    if not source_paths:
        raise SystemExit("No source images found in the manifest.")

    TRANSFORM_DIR.mkdir(parents=True, exist_ok=True)
    output_rows = []

    for index, relative_path in enumerate(source_paths, start=1):
        original_path = DATA_DIR / "images" / relative_path
        transformed_name = f"positive_{index:03d}.jpg"
        transformed_path = TRANSFORM_DIR / transformed_name

        with Image.open(original_path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.thumbnail((MAX_SIDE, MAX_SIDE))
            image.save(
                transformed_path,
                format="JPEG",
                quality=JPEG_QUALITY,
                optimize=True,
            )

        output_rows.append({
            "name": f"controlled_positive_{index:03d}",
            "image_a": f"images/{relative_path}",
            "image_b": f"positive_images/{transformed_name}",
            "is_duplicate": "true",
        })

    with OUTPUT_MANIFEST.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "name",
                "image_a",
                "image_b",
                "is_duplicate",
            ],
        )
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Positive pairs: {len(output_rows)}")
    print(f"Manifest: {OUTPUT_MANIFEST}")
    print(f"Transformed images: {TRANSFORM_DIR}")


if __name__ == "__main__":
    main()