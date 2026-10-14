
from dataclasses import dataclass
from io import BytesIO
import warnings

from PIL import Image, UnidentifiedImageError

from pixelguard.config import Settings, settings


class ImageInputError(ValueError):
    """Base exception for invalid image inputs."""


class UnsupportedImageFormatError(ImageInputError):
    """Raised when an image format is not allowed."""


class ImageSizeLimitError(ImageInputError):
    """Raised when file or decoded image dimensions exceed limits."""


@dataclass(frozen=True)
class LoadedImage:
    image: Image.Image
    format: str
    width: int
    height: int
    file_size_bytes: int

    @property
    def total_pixels(self) -> int:
        return self.width * self.height

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height


def load_image(
    data: bytes,
    config: Settings | None = None,
) -> LoadedImage:
    """Validate and fully decode an image from untrusted bytes."""
    config = config or settings

    if not data:
        raise ImageInputError("The uploaded file is empty.")

    file_size = len(data)

    if file_size > config.max_upload_bytes:
        raise ImageSizeLimitError(
            f"File size exceeds {config.max_upload_bytes} bytes."
        )

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)

            # inspect metadata and verify file integrity.
            with Image.open(BytesIO(data)) as probe:
                image_format = probe.format
                width, height = probe.size

                if image_format not in config.allowed_formats:
                    raise UnsupportedImageFormatError(
                        f"Unsupported image format: {image_format}."
                    )

                if width <= 0 or height <= 0:
                    raise ImageInputError("Invalid image dimensions.")

                if (
                    width > config.max_image_dimension
                    or height > config.max_image_dimension
                    or width * height > config.max_image_pixels
                ):
                    raise ImageSizeLimitError(
                        "Image dimensions exceed configured limits."
                    )

                probe.verify()

            # verify again by fully decoding the pixel data.
            with Image.open(BytesIO(data)) as source:
                source.load()
                image = source.copy()

        return LoadedImage(
            image=image,
            format=image_format,
            width=width,
            height=height,
            file_size_bytes=file_size,
        )

    except ImageInputError:
        raise
    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        SyntaxError,
        ValueError,
    ) as exc:
        raise ImageInputError(
            "The uploaded content is not a valid, safely decodable image."
        ) from exc
