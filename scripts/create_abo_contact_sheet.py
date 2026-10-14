import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

DATA_DIR = Path("data/evaluation/abo")
MANIFEST = DATA_DIR / "candidate_pairs.csv"
IMAGE_DIR = DATA_DIR / "images"
OUTPUT_DIR = DATA_DIR / "contact_sheets"

PAIRS_PER_SHEET = 12
COLUMNS = 3
CARD_WIDTH = 420
CARD_HEIGHT = 190
THUMB_WIDTH = 185
THUMB_HEIGHT = 125
PADDING = 12


def load_thumbnail(path: Path) -> Image.Image:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        return ImageOps.contain(image, (THUMB_WIDTH, THUMB_HEIGHT))


def main() -> None:
    with MANIFEST.open("r", newline="", encoding="utf-8") as file:
        pairs = list(csv.DictReader(file))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for sheet_index, start in enumerate(
        range(0, len(pairs), PAIRS_PER_SHEET), start=1
    ):
        batch = pairs[start : start + PAIRS_PER_SHEET]
        rows = (len(batch) + COLUMNS - 1) // COLUMNS

        sheet = Image.new(
            "RGB",
            (COLUMNS * CARD_WIDTH, rows * CARD_HEIGHT),
            "white",
        )
        draw = ImageDraw.Draw(sheet)

        for local_index, pair in enumerate(batch):
            x = (local_index % COLUMNS) * CARD_WIDTH
            y = (local_index // COLUMNS) * CARD_HEIGHT
            pair_number = start + local_index + 1

            draw.text(
                (x + PADDING, y + 6),
                f"Pair {pair_number} | Product: {pair['item_id']}",
                fill="black",
            )

            for image_index, column in enumerate(
                ("image_a_path", "image_b_path")
            ):
                image_path = IMAGE_DIR / pair[column]
                thumbnail = load_thumbnail(image_path)
                thumb_x = x + PADDING + image_index * (THUMB_WIDTH + 12)
                thumb_y = y + 30

                sheet.paste(thumbnail, (thumb_x, thumb_y))
                draw.rectangle(
                    (
                        thumb_x,
                        thumb_y,
                        thumb_x + thumbnail.width,
                        thumb_y + thumbnail.height,
                    ),
                    outline="gray",
                )

            draw.text(
                (x + PADDING, y + 165),
                f"A: {pair['image_a_id']}  B: {pair['image_b_id']}",
                fill="black",
            )

        output_path = OUTPUT_DIR / f"contact-sheet-{sheet_index:02d}.png"
        sheet.save(output_path)
        print(f"Created: {output_path}")

    print(f"Total pairs: {len(pairs)}")
    print(f"Sheets directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
