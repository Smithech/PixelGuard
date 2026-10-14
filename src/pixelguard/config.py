from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for image ingestion and quality rules."""

    model_config = SettingsConfigDict(
        env_prefix="AUDITOR_",
        env_file=".env",
        extra="ignore",
    )

    max_upload_bytes: int = 10 * 1024 * 1024
    max_image_pixels: int = 20_000_000
    max_image_dimension: int = 10_000

    allowed_formats: list[str] = ["JPEG", "PNG", "WEBP"]

    min_width: int = 800
    min_height: int = 800
    min_aspect_ratio: float = 0.5
    max_aspect_ratio: float = 2.0


settings = Settings()
