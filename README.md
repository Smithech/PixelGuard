# PixelGuard — Product Image Quality & Duplicate Auditor

PixelGuard is a lightweight image-auditing API designed to identify basic technical quality issues and near-identical product images. It combines deterministic image validation with perceptual hashing in a small, modular Python service.

The project demonstrates practical AI Engineering principles: explicit validation contracts, reproducible evaluation, testable components, and honest reporting of model-free baselines.

## Problem

Product catalogs can contain images that are technically unsuitable or visually redundant. PixelGuard provides two focused capabilities:

- **Technical quality auditing:** flags images below configured resolution requirements or outside an allowed aspect-ratio range.
- **Near-duplicate detection:** compares perceptual hashes (pHash) to identify visually similar copies, including resized or recompressed variants.

Background detection and semantic image understanding are outside the current MVP scope.

## Architecture

```text
Client
  |
  v
FastAPI
  |
  +--> Image loader and input validation
  |      +--> File-size and dimension limits
  |      +--> Format and decoding checks
  |
  +--> Quality detector
  |      +--> Resolution rules
  |      +--> Aspect-ratio rules
  |
  +--> Duplicate detector
         +--> Perceptual hash (pHash)
         +--> Hamming-distance threshold
```

The service uses a modular monolith. This keeps the implementation easy to run and test without introducing infrastructure that the current scope does not require.

## Technology

- Python 3.12
- FastAPI and Pydantic
- Pillow
- ImageHash and NumPy
- pytest and HTTPX
- uv for dependency and environment management

The current MVP does not require an LLM or a trained computer-vision model. The quality rules are deterministic, and duplicate detection uses perceptual hashing.

## Features

- `POST /v1/analyze` — validates an uploaded image and returns technical quality metrics and findings.
- `POST /v1/compare` — compares two images and returns their perceptual hashes, Hamming distance, threshold, and duplicate decision.
- `GET /health` — basic health check.
- Configurable upload, pixel-count, dimension, and quality-policy limits.
- Explicit API error responses for invalid images, unsupported formats, and exceeded limits.
- Unit and integration tests.

## Getting started

### Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

### Install dependencies

```bash
uv sync
```

### Run tests

```bash
uv run pytest -v
```

### Start the API

```bash
uv run uvicorn pixelguard.main:app --reload
```

Open the interactive API documentation at `http://127.0.0.1:8000/docs`.

### Example requests

Analyze one image:

```bash
curl -X POST \
  http://127.0.0.1:8000/v1/analyze \
  -F "file=@product.jpg"
```

Compare two images:

```bash
curl -X POST \
  "http://127.0.0.1:8000/v1/compare?threshold=8" \
  -F "file_a=@product-a.jpg" \
  -F "file_b=@product-b.jpg"
```

The threshold is configurable. A lower threshold is stricter; a higher threshold allows more perceptual differences. The default value of `8` is provisional and should be selected using representative, labeled data before production use.

## Evaluation

PixelGuard includes a small evaluation experiment for near-duplicate detection using a sample of Amazon Berkeley Objects (ABO) product images.

The current evaluation manifest contains **61 image pairs**:

- **20 controlled positive pairs:** an image and a resized/recompressed version of that image.
- **41 manually reviewed negative pairs:** candidate pairs reviewed under the project's near-identical-image definition.

At the current pHash threshold of 8, the recorded results are:

| Metric | Result |
|---|---:|
| True positives | 20 |
| False positives | 1 |
| True negatives | 40 |
| False negatives | 0 |
| Precision | 95.24% |
| Recall | 100.00% |
| F1 score | 97.56% |

These are results on this small, constructed evaluation set—not an estimate of production performance. The positive examples are controlled transformations, and the negative examples are a limited, manually reviewed sample. The threshold has not been calibrated on a representative production dataset.

See [`data/evaluation/README.md`](data/evaluation/README.md) for the dataset preparation workflow, evaluation commands, and limitations.

## Reproducibility

### Run the API and tests

The API and test suite do not require the Amazon Berkeley Objects (ABO) evaluation dataset.

```bash
uv sync
uv run pytest -v
uv run uvicorn pixelguard.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to explore the API.

### Reproduce the duplicate-detection evaluation

The ABO benchmark requires the evaluation manifest and the referenced image files to be available locally. These data files may be excluded from version control and are not required to run PixelGuard itself.

If the evaluation files are available, run:

```bash
uv run python scripts/run_benchmark.py \
  --manifest data/evaluation/abo/evaluation_manifest.csv \
  --threshold 8 \
  --thresholds 0,2,4,6,8,10,12,16 \
  --output /tmp/pixelguard-evaluation-report.json \
  --csv-output /tmp/pixelguard-threshold-sweep.csv
```

The JSON report contains the selected-threshold results and per-pair predictions. The CSV contains metrics for the threshold sweep.

If the manifest or image files are missing, follow [`data/evaluation/README.md`](data/evaluation/README.md) for the dataset preparation workflow and evaluation requirements.

Evaluation results are specific to the documented sample and configuration. They should not be interpreted as a guarantee of production performance.

## Security and limitations

- Uploaded content is validated using its actual image format, not merely its filename or declared MIME type.
- File size, decoded dimensions, and pixel count are bounded.
- Invalid and unsupported inputs receive explicit HTTP error responses.
- pHash measures perceptual similarity; it does not establish semantic equivalence.
- Similar-looking images may be false positives, and transformed copies may be missed depending on the threshold.
- The service does not currently perform background segmentation, product recognition, or semantic visual analysis.
- The evaluation sample is small and should not be used to claim production readiness.

## Roadmap

- Expand the labeled evaluation set with more diverse positive and negative pairs.
- Analyze false positives and false negatives before changing the threshold.
- Measure API latency and memory usage on a documented test environment.
- Evaluate additional visual signals only if the baseline reveals a clear gap.

## License and dataset notes

Review the repository's project license and the applicable Amazon Berkeley Objects dataset and image licenses before redistributing data or derived artifacts. The evaluation workflow is designed to keep downloaded source images and regenerable files out of version control where appropriate.