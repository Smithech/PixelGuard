from dataclasses import dataclass

import imagehash

from pixelguard.imaging.loader import LoadedImage


@dataclass(frozen=True)
class DuplicateComparison:
    is_duplicate: bool
    distance: int
    threshold: int
    hash_a: str
    hash_b: str


def calculate_phash(image: LoadedImage) -> imagehash.ImageHash:
    """Calculate a perceptual hash for a loaded image."""

    return imagehash.phash(image.image)


def compare_images(
    image_a: LoadedImage,
    image_b: LoadedImage,
    threshold: int = 8,
) -> DuplicateComparison:
    """Compare two images using perceptual-hash Hamming distance."""

    if threshold < 0:
        raise ValueError("threshold must be non-negative")

    hash_a = calculate_phash(image_a)
    hash_b = calculate_phash(image_b)
    
    distance = int(hash_a - hash_b)

    return DuplicateComparison(
        is_duplicate=bool(distance <= threshold),
        distance=distance,
        threshold=threshold,
        hash_a=str(hash_a),
        hash_b=str(hash_b),
    )
