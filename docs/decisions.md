
# Architecture Decision Log

## ADR-001: Modular monolith
Status: Accepted

Use a single Python package with independent API, ingestion, detector, and evaluation modules. Avoid distributed infrastructure
until requirements justify it.

## ADR-002: Deterministic technical quality baseline
Status: Accepted

Use Pillow and configurable rules for file format, dimensions, pixel count, and aspect ratio. Do not introduce a vision model
for checks that can be evaluated deterministically.

## ADR-003: Safe image ingestion
Status: Accepted

Enforce compressed file size, maximum dimensions, maximum pixel count, supported formats, integrity checks, and full decoding.

## ADR-004: Separate ingestion failures from quality findings
Status: Accepted

Reject invalid or unsupported files explicitly. Return structured warnings for valid images that violate configurable quality policy.

## ADR-005: Confidence semantics
Status: Accepted

Do not expose confidence values for deterministic rules unless a meaningful probabilistic interpretation is established.
