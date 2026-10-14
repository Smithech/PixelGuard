from io import BytesIO

from PIL import Image

from pixelguard.detectors.duplicates import calculate_phash, compare_images
from pixelguard.imaging.loader import load_image


def make_loaded_image(
    color: tuple[int, int, int],
    size: tuple[int, int] = (256, 256),
    image_format: str = "PNG",
):
    buffer = BytesIO()
    Image.new("RGB", size, color=color).save(buffer, format=image_format)
    return load_image(buffer.getvalue())


def test_identical_images_have_zero_phash_distance() -> None:
    image_a = make_loaded_image((220, 30, 30))
    image_b = make_loaded_image((220, 30, 30))

    result = compare_images(image_a, image_b)

    assert result.distance == 0
    assert result.is_duplicate is True
    assert result.hash_a == result.hash_b


def test_resized_image_has_similar_phash() -> None:
    original = Image.new("RGB", (256, 256), color=(40, 120, 200))
    resized = original.resize((128, 128))

    buffers = []
    for image in (original, resized):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffers.append(load_image(buffer.getvalue()))

    result = compare_images(buffers[0], buffers[1])

    assert result.distance <= result.threshold
    assert result.is_duplicate is True


def test_different_visual_patterns_can_be_compared() -> None:
    # Large-scale structures are more suitable for testing pHash
    # than a uniform image against a high-frequency checkerboard.
    left_black = Image.new("RGB", (256, 256), color=(0, 0, 0))
    right_black = Image.new("RGB", (256, 256), color=(0, 0, 0))

    left_pixels = left_black.load()
    right_pixels = right_black.load()

    # Bright square on the left.
    for y in range(32, 224):
        for x in range(16, 112):
            left_pixels[x, y] = (255, 255, 255)

    # Bright square on the right.
    for y in range(32, 224):
        for x in range(144, 240):
            right_pixels[x, y] = (255, 255, 255)

    loaded_images = []
    for image in (left_black, right_black):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        loaded_images.append(load_image(buffer.getvalue()))

    result = compare_images(loaded_images[0], loaded_images[1])

    assert result.distance > result.threshold
    assert result.is_duplicate is False



def test_negative_threshold_is_rejected() -> None:
    image = make_loaded_image((30, 80, 120))

    try:
        compare_images(image, image, threshold=-1)
    except ValueError as exc:
        assert "threshold" in str(exc)
    else:
        raise AssertionError("Expected ValueError for negative threshold")


def test_calculate_phash_returns_hash() -> None:
    image = make_loaded_image((50, 100, 150))

    result = calculate_phash(image)

    assert len(str(result)) == 16
