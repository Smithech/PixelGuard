import argparse
import csv
import json
import sys
from pathlib import Path

from pixelguard.evaluation import (
    PairExample,
    calculate_metrics,
    compare_pair,
)


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")


def load_manifest(path: Path) -> list[PairExample]:
    examples: list[PairExample] = []

    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {"name", "image_a", "image_b", "is_duplicate"}

        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                f"CSV must contain columns: {', '.join(sorted(required))}"
            )

        for row_number, row in enumerate(reader, start=2):
            image_a_path = path.parent / row["image_a"]
            image_b_path = path.parent / row["image_b"]

            try:
                examples.append(
                    PairExample(
                        name=row["name"],
                        image_a=image_a_path.read_bytes(),
                        image_b=image_b_path.read_bytes(),
                        is_duplicate=parse_bool(row["is_duplicate"]),
                    )
                )
            except (OSError, ValueError) as exc:
                raise ValueError(
                    f"Invalid row {row_number} in {path}: {exc}"
                ) from exc

    if not examples:
        raise ValueError("Manifest contains no examples")

    return examples


def parse_thresholds(value: str) -> list[int]:
    try:
        thresholds = [int(item.strip()) for item in value.split(",")]
    except ValueError as exc:
        raise ValueError(
            "Thresholds must be comma-separated integers, e.g. 0,2,4,8,12"
        ) from exc

    if not thresholds or any(value < 0 for value in thresholds):
        raise ValueError("All thresholds must be non-negative")

    if len(set(thresholds)) != len(thresholds):
        raise ValueError("Thresholds must not contain duplicates")

    return sorted(thresholds)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate PixelGuard duplicate detection."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--threshold", type=int, default=8)
    parser.add_argument(
        "--thresholds",
        type=str,
        default=None,
        help="Optional threshold sweep, e.g. 0,2,4,6,8,10,12,16",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmark-results.json"),
    )
    parser.add_argument(
        "--csv-output",
        type=Path,
        default=None,
        help="Optional CSV path for threshold-sweep metrics",
    )
    args = parser.parse_args()

    if args.threshold < 0:
        parser.error("--threshold must be non-negative")

    try:
        thresholds = (
            parse_thresholds(args.thresholds)
            if args.thresholds is not None
            else [args.threshold]
        )
        examples = load_manifest(args.manifest)

        # Calculate each pair's perceptual distance only once.
        base_results = [
            compare_pair(example, threshold=0)
            for example in examples
        ]

        sweep_rows = []
        for threshold in thresholds:
            expected = [
                result.expected_duplicate for result in base_results
            ]
            predicted = [
                result.phash_distance <= threshold
                for result in base_results
            ]
            metrics = calculate_metrics(
                expected=expected,
                predicted=predicted,
            )
            sweep_rows.append({
                "threshold": threshold,
                "example_count": len(base_results),
                **metrics,
            })

        # Keep the JSON report compatible with the original CLI.
        selected_threshold = args.threshold
        selected_metrics = next(
            row for row in sweep_rows
            if row["threshold"] == selected_threshold
        ) if selected_threshold in thresholds else None

        if selected_metrics is None:
            selected_results = [
                compare_pair(example, threshold=selected_threshold)
                for example in examples
            ]
            selected_metrics = calculate_metrics(
                expected=[
                    result.expected_duplicate for result in selected_results
                ],
                predicted=[
                    result.predicted_duplicate for result in selected_results
                ],
            )
        else:
            selected_results = base_results

        report = {
            "threshold": selected_threshold,
            "example_count": len(selected_results),
            "metrics": {
                key: value
                for key, value in selected_metrics.items()
                if key not in {"threshold", "example_count"}
            },
            "pairs": [
                {
                    "name": result.name,
                    "expected_duplicate": result.expected_duplicate,
                    "exact_match": result.exact_match,
                    "phash_distance": result.phash_distance,
                    "predicted_duplicate": (
                        result.phash_distance <= selected_threshold
                    ),
                }
                for result in selected_results
            ],
        }

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )

        if args.csv_output is not None:
            args.csv_output.parent.mkdir(parents=True, exist_ok=True)
            with args.csv_output.open(
                "w", newline="", encoding="utf-8"
            ) as file:
                fieldnames = [
                    "threshold",
                    "example_count",
                    "true_positives",
                    "false_positives",
                    "false_negatives",
                    "true_negatives",
                    "precision",
                    "recall",
                    "f1",
                ]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sweep_rows)

        print(json.dumps({
            "threshold": selected_threshold,
            "example_count": len(selected_results),
            "metrics": report["metrics"],
            "report": str(args.output),
            "threshold_sweep": (
                str(args.csv_output)
                if args.csv_output is not None
                else None
            ),
        }, indent=2))

    except (OSError, ValueError) as exc:
        print(f"Benchmark error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
