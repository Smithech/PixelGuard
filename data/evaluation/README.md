# Experimento ABO: evaluación de duplicados

## Objetivo

Evaluar el detector perceptual de duplicados de PixelGuard con pares negativos revisados manualmente y pares positivos generados mediante transformaciones controladas.

## Data and labels

- **41 pares negativos:** pares del muestreo de Amazon Berkeley Objects (ABO), revisados manualmente. Se etiquetaron como `false` según el criterio de duplicado visual casi idéntico.
- **20 pares positivos controlados:** cada par contiene una imagen original y una versión redimensionada y recomprimida como JPEG. Se etiquetaron como `true` porque ambas imágenes proceden de la misma imagen fuente.
- **Total:** 61 pares, 20 positivos y 41 negativos.

La muestra es pequeña y no representa necesariamente la distribución real de imágenes de un marketplace. Los positivos controlados evalúan un tipo concreto de transformación y no cubren todos los casos posibles de duplicación.

## Preparation

The following scripts reconstruct the evaluation workflow:

1. `prepare_abo_sample.py` — prepares candidate pairs from dataset metadata.
2. `download_abo_sample.py` — downloads the referenced source images.
3. `create_abo_contact_sheet.py` — generates contact sheets for manual review.
4. `create_abo_positive_pairs.py` — creates controlled positive pairs by resizing and recompressing source images.
5. `build_abo_evaluation_manifest.py` — combines the labeled negative pairs and controlled positive pairs into the benchmark manifest.

Run the scripts from the repository root. The workflow requires access to the ABO source data and the dependencies and tools required by the download script.

The negative-pair labels were reviewed manually and should not be overwritten with predictions from the detector. The controlled positive pairs test a limited class of transformations; they do not represent every possible duplicate scenario.

Downloaded images and generated artifacts may be excluded from version control. Before redistributing source images or metadata, verify the applicable dataset terms and license.

## Run the evaluation

First, ensure that `data/evaluation/abo/evaluation_manifest.csv` exists and that every image path referenced by the manifest resolves to a local file.

From the repository root, run:

```bash
uv run python scripts/run_benchmark.py \
  --manifest data/evaluation/abo/evaluation_manifest.csv \
  --threshold 8 \
  --thresholds 0,2,4,6,8,10,12,16 \
  --output data/evaluation/abo/evaluation-report.json \
  --csv-output data/evaluation/abo/evaluation-threshold-sweep.csv
```

The command writes a JSON report for the selected threshold and a CSV containing metrics for each threshold in the sweep.

If the manifest or images are unavailable, follow the preparation steps above before running the benchmark. Running the API and tests does not require the ABO evaluation data.

## Observed result

En esta ejecución, con umbral 8:

| Métrica | Resultado |
|---|---:|
| Pares evaluados | 61 |
| Verdaderos positivos | 20 |
| Falsos positivos | 1 |
| Falsos negativos | 0 |
| Verdaderos negativos | 40 |
| Precisión | 95,24 % |
| Recall | 100 % |
| F1 | 97,56 % |

Estos valores describen únicamente esta muestra y configuración. No constituyen una garantía de rendimiento en producción. El umbral 8 sigue siendo provisional y debe evaluarse con datos más variados.

## Dataset provenance and licensing

- **Dataset:** Amazon Berkeley Objects (ABO).
- **Official dataset page:** https://amazon-berkeley-objects.s3.amazonaws.com/index.html
- **AWS Open Data registry:** https://registry.opendata.aws/amazon-berkeley-objects/
- **Purpose:** a small sample for evaluating visual near-duplicate detection.
- **Pair labels:** manually reviewed for this experiment; they are not official ABO duplicate labels.

**Licensing note:** Check the current dataset documentation and AWS registry terms before redistributing source images, metadata, or derived artifacts. The applicable terms must be verified for the specific materials being used. This repository does not claim that all dataset assets can be redistributed under a single license.