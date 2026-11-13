# taptap-codetest

Pipeline que lee eventos de anuncios en JSONL, los limpia (duplicados, precios y timestamps inválidos), los enriquece con el nombre del publisher y genera métricas por hora, país y publisher.

## Requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (gestiona Python 3.12 y las dependencias automáticamente)

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Instalación

Desde la raíz del proyecto (una vez activado el entorno virtual):

```bash
uv sync
```

## Ejecución

```bash
uv run taptap-codetest --input data --output out
```

- `--input`: un fichero `.jsonl` o una carpeta con ficheros `*.jsonl`. El fichero `publishers.csv` se lee de esa misma carpeta (si no existe, `publisher_name` queda vacío).
- `--output`: carpeta donde se escriben los resultados (se crea si no existe).
- `--format`: `csv` (por defecto) o `parquet`.
- `--log-level`: nivel de log (por defecto `INFO`).

Ejemplos:

```bash
# Un solo fichero
uv run taptap-codetest --input data/events_2026-09-01.jsonl --output out



> Nota: al pasar la carpeta `data`, se procesan **todos** los `*.jsonl` que contiene, incluido `events-test.jsonl`.

## Resultados

```
out/
├── date=2026-09-01/metrics.csv   # métricas por día (una carpeta por fecha)
├── date=2026-09-02/metrics.csv
├── _rejects/rejects.jsonl        # líneas rechazadas y el motivo
└── _summary.json                 # líneas leídas, aceptadas, rechazadas y por tipo
```

Columnas de `metrics`: `date_utc`, `hour_utc`, `country`, `publisher_id`, `publisher_name`, `bid_requests`, `impressions`, `clicks`, `ctr`, `spend_eur`.

## Tests

```bash
uv run pytest
```
