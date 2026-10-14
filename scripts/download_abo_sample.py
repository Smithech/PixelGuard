import csv
import subprocess
import sys
from pathlib import Path

DATA_DIR = Path("data/evaluation/abo")
MANIFEST = DATA_DIR / "candidate_pairs.csv"
IMAGE_DIR = DATA_DIR / "images"
BUCKET = "s3://amazon-berkeley-objects/images/small"


def main() -> int:
    with MANIFEST.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    paths = sorted({
        row[column]
        for row in rows
        for column in ("image_a_path", "image_b_path")
    })

    downloaded = 0
    
    for relative_path in paths:
        destination = IMAGE_DIR / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists():
            continue

        url = f"{BUCKET}/{relative_path}"
        result = subprocess.run(
            [
                "aws", "s3", "cp", "--no-sign-request",
                url, str(destination),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(
                f"Failed to download {relative_path}: {result.stderr.strip()}",
                file=sys.stderr,
            )
            return 1

        downloaded += 1

    print(f"Candidate pairs: {len(rows)}")
    print(f"Unique images: {len(paths)}")
    print(f"New images downloaded: {downloaded}")
    print(f"Image directory: {IMAGE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
