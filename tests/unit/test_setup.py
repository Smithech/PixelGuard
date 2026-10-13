from PIL import Image
import imagehash
import numpy as np

import pixelguard


def test_package_is_importable():
    assert pixelguard.__version__ == "0.1.0"


def test_image_dependencies_work():
    pixels = np.zeros((32, 32, 3), dtype=np.uint8)
    image = Image.fromarray(pixels, mode="RGB")

    perceptual_hash = imagehash.phash(image)

    assert image.size == (32, 32)
    assert len(str(perceptual_hash)) == 16