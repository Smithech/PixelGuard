import csv
from pathlib import Path

DATA_DIR = Path("data/evaluation/abo")
NEGATIVE_INPUT = DATA_DIR / "candidate_pairs.csv"
POSITIVE_INPUT = DATA_DIR / "controlled_positive_manifest.csv"
OUTPUT = DATA_DIR / "evaluation_manifest.csv"

FIELDS = ["name", "image_a", "image_b", "is_duplicate"]


def main() -> None:
    combined = []

    with NEGATIVE_INPUT.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        for index, row in enumerate(csv.DictReader(file), start=1):
            label = row["label"].strip().lower()
            if label not in {"true", "false"}:
                raise ValueError(f"Invalid label in negative pair {index}: {label}")

            combined.append({
                "name": f"abo_negative_{index:03d}",
                "image_a": f"images/{row['image_a_path']}",
                "image_b": f"images/{row['image_b_path']}",
                "is_duplicate": label,
            })

    with POSITIVE_INPUT.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        for row in csv.DictReader(file):
            combined.append({
                "name": row["name"],
                "image_a": row["image_a"],
                "image_b": row["image_b"],
                "is_duplicate": row["is_duplicate"].strip().lower(),
            })

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(combined)

    positives = sum(r["is_duplicate"] == "true" for r in combined)
    negatives = sum(r["is_duplicate"] == "false" for r in combined)

    print(f"Total pairs: {len(combined)}")
    print(f"Positive pairs: {positives}")
    print(f"Negative pairs: {negatives}")
    print(f"Manifest: {OUTPUT}")


if __name__ == "__main__":
    main()