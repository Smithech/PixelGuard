from io import BytesIO

import pytest
from PIL import Image

from pixelguard.config import Settings
from pixelguard.detectors.quality import analyze_quality
from pixelguard.imaging.loader import (
    ImageInputError,
    ImageSizeLimitError,
    UnsupportedImageFormatError,
    load_image,
)


def make_image(
    width: int = 1000,
    height: int = 1000,
    image_format: str = "JPEG",
) -> bytes:
    buffer = BytesIO()
    image = Image.new("RGB", (width, height), color="white")
    image.save(buffer, format=image_format)
    return buffer.getvalue()


@pytest.fixture
def config() -> Settings:
    return Settings(
        max_upload_bytes=1_000_000,
        max_image_pixels=2_000_000,
        max_image_dimension=2_000,
        allowed_formats=["JPEG", "PNG", "WEBP"],
        min_width=800,
        min_height=800,
        min_aspect_ratio=0.5,
        max_aspect_ratio=2.0,
    )


def test_valid_image_passes_quality_policy(config):
    loaded = load_image(make_image(), config)

    result = analyze_quality(loaded, config)

    assert result.status == "passed"
    assert result.findings == []
    assert result.metrics.width == 1000
    assert result.metrics.height == 1000
    assert result.metrics.format == "JPEG"


def test_low_resolution_generates_finding(config):
    loaded = load_image(make_image(640, 640), config)

    result = analyze_quality(loaded, config)

    assert result.status == "warning"
    assert result.findings[0].code == "LOW_RESOLUTION"


def test_extreme_aspect_ratio_generates_finding(config):
    loaded = load_image(make_image(1800, 600), config)

    result = analyze_quality(loaded, config)

    codes = {finding.code for finding in result.findings}
    assert "ASPECT_RATIO_OUT_OF_RANGE" in codes


def test_unsupported_format_is_rejected(config):
    with pytest.raises(UnsupportedImageFormatError):
        load_image(make_image(image_format="GIF"), config)


def test_corrupted_file_is_rejected(config):
    with pytest.raises(ImageInputError):
        load_image(b"not an image", config)


def test_empty_file_is_rejected(config):
    with pytest.raises(ImageInputError):
        load_image(b"", config)


def test_upload_size_limit_is_enforced(config):
    strict_config = config.model_copy(
        update={"max_upload_bytes": 10}
    )

    with pytest.raises(ImageSizeLimitError):
        load_image(make_image(), strict_config)


def test_pixel_limit_is_enforced(config):
    strict_config = config.model_copy(
        update={"max_image_pixels": 100_000}
    )

    with pytest.raises(ImageSizeLimitError):
        load_image(make_image(1000, 1000), strict_config)


def test_result_contains_reproducible_evidence(config):
    loaded = load_image(make_image(640, 640), config)

    result = analyze_quality(loaded, config)
    finding = result.findings[0]

    assert finding.evidence["width"] == 640
    assert finding.evidence["minimum_width"] == 800
    assert finding.severity == "warning"
    assert finding.recommendation
