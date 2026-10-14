from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["info", "warning", "error"]


class Finding(BaseModel):
    code: str
    severity: Severity
    message: str
    evidence: dict[str, int | float | str | bool]
    recommendation: str


class ImageMetrics(BaseModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    format: str
    aspect_ratio: float = Field(gt=0)
    file_size_bytes: int = Field(ge=0)
    total_pixels: int = Field(gt=0)


class QualityResult(BaseModel):
    status: Literal["passed", "warning"]
    metrics: ImageMetrics
    findings: list[Finding] = Field(default_factory=list)


class DuplicateComparisonResult(BaseModel):
    is_duplicate: bool
    distance: int = Field(ge=0)
    threshold: int = Field(ge=0)
    hash_a: str
    hash_b: str