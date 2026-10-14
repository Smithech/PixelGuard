
from pixelguard.config import Settings, settings
from pixelguard.imaging.loader import LoadedImage
from pixelguard.schemas import Finding, ImageMetrics, QualityResult


def analyze_quality(
    loaded: LoadedImage,
    config: Settings | None = None,
) -> QualityResult:
    """Apply deterministic image quality policy rules."""
    config = config or settings
    findings: list[Finding] = []

    if (
        loaded.width < config.min_width
        or loaded.height < config.min_height
    ):
        findings.append(
            Finding(
                code="LOW_RESOLUTION",
                severity="warning",
                message="Image dimensions are below the configured minimum.",
                evidence={
                    "width": loaded.width,
                    "height": loaded.height,
                    "minimum_width": config.min_width,
                    "minimum_height": config.min_height,
                },
                recommendation=(
                    "Upload an image that meets the minimum resolution."
                ),
            )
        )

    ratio = loaded.aspect_ratio
    
    if not config.min_aspect_ratio <= ratio <= config.max_aspect_ratio:
        findings.append(
            Finding(
                code="ASPECT_RATIO_OUT_OF_RANGE",
                severity="warning",
                message="Image aspect ratio is outside the configured range.",
                evidence={
                    "aspect_ratio": round(ratio, 4),
                    "minimum_aspect_ratio": config.min_aspect_ratio,
                    "maximum_aspect_ratio": config.max_aspect_ratio,
                },
                recommendation=(
                    "Check the marketplace image policy and adjust "
                    "the image dimensions or crop if appropriate."
                ),
            )
        )

    metrics = ImageMetrics(
        width=loaded.width,
        height=loaded.height,
        format=loaded.format,
        aspect_ratio=round(ratio, 4),
        file_size_bytes=loaded.file_size_bytes,
        total_pixels=loaded.total_pixels,
    )

    return QualityResult(
        status="warning" if findings else "passed",
        metrics=metrics,
        findings=findings,
    )
