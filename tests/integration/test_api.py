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
