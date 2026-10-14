from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from pixelguard.config import settings
from pixelguard.main import app

client = TestClient(app)


def make_image(
    image_format: str = "JPEG",
    size: tuple[int, int] = (800, 800),
) -> bytes:
    """Generate a small in-memory image for API tests."""
    
    buffer = BytesIO()
    Image.new("RGB", size, color=(120, 160, 200)).save(
        buffer,
        format=image_format,
    )
    return buffer.getvalue()


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_valid_image_returns_quality_result() -> None:
    image_bytes = make_image()

    response = client.post(
        "/v1/analyze",
        files={"file": ("product.jpg", image_bytes, "image/jpeg")},
    )

    assert response.status_code == 200
    result = response.json()
    assert "status" in result
    assert "metrics" in result
    assert "findings" in result
    assert result["metrics"]["width"] == 800
    assert result["metrics"]["height"] == 800


def test_analyze_corrupt_image_returns_400() -> None:
    response = client.post(
        "/v1/analyze",
        files={"file": ("broken.jpg", b"not a real image", "image/jpeg")},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_IMAGE"


def test_analyze_unsupported_format_returns_415() -> None:
    image_bytes = make_image(image_format="BMP")

    response = client.post(
        "/v1/analyze",
        files={"file": ("product.bmp", image_bytes, "image/bmp")},
    )

    assert response.status_code == 415
    assert response.json()["detail"]["code"] == "UNSUPPORTED_IMAGE_FORMAT"


def test_analyze_oversized_upload_returns_413(
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "max_upload_bytes", 20)
    image_bytes = make_image()

    response = client.post(
        "/v1/analyze",
        files={"file": ("product.jpg", image_bytes, "image/jpeg")},
    )

    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "UPLOAD_TOO_LARGE"


def test_compare_identical_images_returns_duplicate() -> None:
    image_bytes = make_image()

    response = client.post(
        "/v1/compare",
        files={
            "file_a": ("first.jpg", image_bytes, "image/jpeg"),
            "file_b": ("second.jpg", image_bytes, "image/jpeg"),
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["is_duplicate"] is True
    assert result["distance"] == 0
    assert result["threshold"] == 8
    assert result["hash_a"] == result["hash_b"]


def test_compare_different_images_returns_not_duplicate() -> None:
    first = Image.new("RGB", (256, 256), color=(0, 0, 0))
    second = Image.new("RGB", (256, 256), color=(0, 0, 0))

    first_pixels = first.load()
    second_pixels = second.load()

    for y in range(32, 224):
        for x in range(16, 112):
            first_pixels[x, y] = (255, 255, 255)
        for x in range(144, 240):
            second_pixels[x, y] = (255, 255, 255)

    image_bytes = []
    for image in (first, second):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        image_bytes.append(buffer.getvalue())

    response = client.post(
        "/v1/compare",
        files={
            "file_a": ("first.png", image_bytes[0], "image/png"),
            "file_b": ("second.png", image_bytes[1], "image/png"),
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["is_duplicate"] is False
    assert result["distance"] > result["threshold"]


def test_compare_unsupported_format_returns_415() -> None:
    bmp_bytes = make_image(image_format="BMP")

    response = client.post(
        "/v1/compare",
        files={
            "file_a": ("first.bmp", bmp_bytes, "image/bmp"),
            "file_b": ("second.jpg", make_image(), "image/jpeg"),
        },
    )

    assert response.status_code == 415
    assert response.json()["detail"]["code"] == "UNSUPPORTED_IMAGE_FORMAT"


def test_compare_negative_threshold_returns_422() -> None:
    image_bytes = make_image()

    response = client.post(
        "/v1/compare?threshold=-1",
        files={
            "file_a": ("first.jpg", image_bytes, "image/jpeg"),
            "file_b": ("second.jpg", image_bytes, "image/jpeg"),
        },
    )

    assert response.status_code == 422
