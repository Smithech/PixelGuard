import csv
import gzip
import json
from pathlib import Path

DATA_DIR = Path("data/evaluation/abo")
IMAGES_CSV = DATA_DIR / "images.csv.gz"
LISTINGS_GZ = DATA_DIR / "listings_0.json.gz"
OUTPUT = DATA_DIR / "candidate_pairs.csv"
MAX_PRODUCTS = 10


def load_image_index(path: Path) -> dict[str, str]:
    index: dict[str, str] = {}

    with gzip.open(path, "rt", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {"image_id", "path"}

        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Unexpected images.csv.gz columns")

        for row in reader:
            index[row["image_id"]] = row["path"]

    return index


def iter_listings(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                yield json.loads(line)


def main() -> None:
    image_index = load_image_index(IMAGES_CSV)
    rows: list[dict[str, str]] = []
    selected_products = 0

    for listing in iter_listings(LISTINGS_GZ):
        item_id = listing.get("item_id")
        image_ids = []

        main_id = listing.get("main_image_id")
        if main_id:
            image_ids.append(main_id)

        image_ids.extend(listing.get("other_image_id") or [])
        image_ids = list(dict.fromkeys(
            image_id for image_id in image_ids if image_id in image_index
        ))

        if len(image_ids) < 2:
            continue

        # Candidate pair: main image against each additional image.
        main_image_id = image_ids[0]
        for other_image_id in image_ids[1:]:
            rows.append({
                "item_id": str(item_id),
                "image_a_id": main_image_id,
                "image_a_path": image_index[main_image_id],
                "image_b_id": other_image_id,
                "image_b_path": image_index[other_image_id],
                "label": "",
                "label_notes": "",
            })

        selected_products += 1
        if selected_products >= MAX_PRODUCTS:
            break

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    
    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "item_id",
            "image_a_id",
            "image_a_path",
            "image_b_id",
            "image_b_path",
            "label",
            "label_notes",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Products selected: {selected_products}")
    print(f"Candidate pairs: {len(rows)}")
    print(f"Manifest: {OUTPUT}")


if __name__ == "__main__":
    main()
