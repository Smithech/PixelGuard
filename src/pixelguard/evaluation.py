from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO

import imagehash
from PIL import Image

from pixelguard.config import settings
from pixelguard.imaging.loader import load_image


@dataclass(frozen=True)
class PairExample:
    name: str
    image_a: bytes
    image_b: bytes
    is_duplicate: bool


@dataclass(frozen=True)
class PairResult:
    name: str
    expected_duplicate: bool
    exact_match: bool
    phash_distance: int
    predicted_duplicate: bool


def exact_match(image_a: bytes, image_b: bytes) -> bool:
    """Return whether both files have exactly the same bytes."""

    return sha256(image_a).digest() == sha256(image_b).digest()


def compare_pair(
    example: PairExample,
    threshold: int = 8,
) -> PairResult:
    """Evaluate one pair with exact hashing and perceptual hashing."""

    loaded_a = load_image(example.image_a, config=settings)
    loaded_b = load_image(example.image_b, config=settings)

    hash_a = imagehash.phash(loaded_a.image)
    hash_b = imagehash.phash(loaded_b.image)
    distance = int(hash_a - hash_b)

    return PairResult(
        name=example.name,
        expected_duplicate=example.is_duplicate,
        exact_match=exact_match(example.image_a, example.image_b),
        phash_distance=distance,
        predicted_duplicate=distance <= threshold,
    )


def calculate_metrics(
    expected: list[bool],
    predicted: list[bool],
) -> dict[str, float | int]:
    """Calculate binary classification metrics without extra dependencies."""

    if len(expected) != len(predicted):
        raise ValueError("expected and predicted must have equal lengths")
    if not expected:
        raise ValueError("at least one example is required")

    tp = sum(e and p for e, p in zip(expected, predicted))
    fp = sum(not e and p for e, p in zip(expected, predicted))
    fn = sum(e and not p for e, p in zip(expected, predicted))
    tn = sum(not e and not p for e, p in zip(expected, predicted))

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def make_png(color: tuple[int, int, int], size: tuple[int, int] = (800, 800)) -> bytes:
    """Create a synthetic image for smoke tests or demo examples."""

    buffer = BytesIO()
    Image.new("RGB", size, color=color).save(buffer, format="PNG")
    
    return buffer.getvalue()
