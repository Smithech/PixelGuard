# Experimento ABO: evaluación de duplicados

## Objetivo

Evaluar el detector perceptual de duplicados de PixelGuard con pares negativos revisados manualmente y pares positivos generados mediante transformaciones controladas.

## Datos y etiquetas

- **41 pares negativos:** pares del muestreo de Amazon Berkeley Objects (ABO), revisados manualmente. Se etiquetaron como `false` según el criterio de duplicado visual casi idéntico.
- **20 pares positivos controlados:** cada par contiene una imagen original y una versión redimensionada y recomprimida como JPEG. Se etiquetaron como `true` porque ambas imágenes proceden de la misma imagen fuente.
- **Total:** 61 pares, 20 positivos y 41 negativos.

La muestra es pequeña y no representa necesariamente la distribución real de imágenes de un marketplace. Los positivos controlados evalúan un tipo concreto de transformación y no cubren todos los casos posibles de duplicación.

## Preparación

Los scripts de `scripts/` permiten reconstruir el experimento:

1. `prepare_abo_sample.py`: prepara pares candidatos a partir de los metadatos.
2. `download_abo_sample.py`: descarga las imágenes referenciadas.
3. `create_abo_contact_sheet.py`: genera hojas para revisar visualmente los pares.
4. `create_abo_positive_pairs.py`: genera positivos controlados.
5. `build_abo_evaluation_manifest.py`: combina los negativos etiquetados y los positivos.

Los negativos contienen etiquetas revisadas manualmente. No se deben sobrescribir automáticamente con predicciones del detector.

Los pasos de descarga requieren acceso a los objetos públicos de ABO y la AWS CLI. Antes de redistribuir imágenes o metadatos, verifica las condiciones de uso y licencia aplicables.

## Ejecutar la evaluación

Con `evaluation_manifest.csv` y los archivos de imagen necesarios disponibles:

```bash
uv run python scripts/run_benchmark.py \
  --manifest data/evaluation/abo/evaluation_manifest.csv \
  --threshold 8 \
  --thresholds 0,2,4,6,8,10,12,16 \
  --output data/evaluation/abo/evaluation-report.json \
  --csv-output data/evaluation/abo/evaluation-threshold-sweep.csv
```

## Resultado observado

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

## Fuente Dataset 

- **Dataset**: Amazon Berkeley Objects (ABO).
- **Fuente**: https://amazon-berkeley-objects.s3.amazonaws.com/index.html
- **Licencia declarada**: CC BY 4.0, con atribución requerida.
- **Uso en PixelGuard**: muestra pequeña para evaluación de duplicados visuales.
- **Etiquetas de pares**: creadas y revisadas manualmente; no son etiquetas oficiales de duplicación.