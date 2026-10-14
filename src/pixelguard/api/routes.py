from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from pixelguard.config import settings
from pixelguard.detectors.duplicates import compare_images
from pixelguard.detectors.quality import analyze_quality
from pixelguard.imaging.loader import (
    ImageInputError,
    ImageSizeLimitError,
    UnsupportedImageFormatError,
    load_image,
)
from pixelguard.schemas import DuplicateComparisonResult, QualityResult

router = APIRouter()


async def _read_limited_upload(upload: UploadFile, max_bytes: int) -> bytes:
    """Read an upload incrementally, rejecting it if it exceeds the byte limit."""
    chunks: list[bytes] = []
    total_bytes = 0

    while True:
        chunk = await upload.read(64 * 1024)
        if not chunk:
            break

        total_bytes += len(chunk)

        if total_bytes > max_bytes:
            raise HTTPException(
                status_code=413,
                detail={
                    "code": "UPLOAD_TOO_LARGE",
                    "message": f"El archivo supera el límite de {max_bytes} bytes.",
                },
            )

        chunks.append(chunk)

    return b"".join(chunks)


@router.post("/v1/analyze", response_model=QualityResult)
async def analyze_image(file: UploadFile = File(...)) -> QualityResult:
    """Analyze an uploaded image's basic technical quality."""
    try:
        data = await _read_limited_upload(file, settings.max_upload_bytes)
        loaded_image = load_image(data, config=settings)

        return analyze_quality(loaded_image, config=settings)

    except UnsupportedImageFormatError as exc:
        raise HTTPException(
            status_code=415,
            detail={
                "code": "UNSUPPORTED_IMAGE_FORMAT", 
                "message": str(exc)
            },
        ) from exc

    except ImageSizeLimitError as exc:
        raise HTTPException(
            status_code=413,
            detail={
                "code": "IMAGE_LIMIT_EXCEEDED", 
                "message": str(exc)
            },
        ) from exc

    except ImageInputError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_IMAGE", 
                "message": str(exc)
            },
        ) from exc

    finally:
        await file.close()


@router.post("/v1/compare", response_model=DuplicateComparisonResult)
async def compare_uploaded_images(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    threshold: int = Query(default=8, ge=0),
) -> DuplicateComparisonResult:
    """Compare two uploaded images using perceptual hashing."""

    try:
        data_a = await _read_limited_upload(file_a, settings.max_upload_bytes)
        data_b = await _read_limited_upload(file_b, settings.max_upload_bytes)

        image_a = load_image(data_a, config=settings)
        image_b = load_image(data_b, config=settings)

        result = compare_images(image_a, image_b, threshold=threshold)

        return DuplicateComparisonResult(
            is_duplicate=result.is_duplicate,
            distance=result.distance,
            threshold=result.threshold,
            hash_a=result.hash_a,
            hash_b=result.hash_b,
        )

    except UnsupportedImageFormatError as exc:
        raise HTTPException(
            status_code=415,
            detail={"code": "UNSUPPORTED_IMAGE_FORMAT", "message": str(exc)},
        ) from exc

    except ImageSizeLimitError as exc:
        raise HTTPException(
            status_code=413,
            detail={"code": "IMAGE_LIMIT_EXCEEDED", "message": str(exc)},
        ) from exc

    except ImageInputError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_IMAGE", "message": str(exc)},
        ) from exc

    finally:
        await file_a.close()
        await file_b.close()
