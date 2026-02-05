# HistoryMosaic

HistoryMosaic builds structured historical-event records from source text, validates schema quality, rewrites posts for X, and supports autopost workflows.

## Production Baseline

This repository now includes:
- Dependency manifest: `requirements.txt`
- Runtime environment template: `.env.example`
- Startup environment validation (numeric bounds and required runtime behavior)
- Containerization baseline: `Dockerfile`
- CI checks: `.github/workflows/ci.yml`

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest -q
```

Run extraction pipeline:

```bash
python src/run_pipeline.py "March on Washington"
```

Run autopost for a saved event:

```bash
python src/autopost.py events/<event-file>.json
```

Run scheduler on all event files:

```bash
python src/schedule.py
```

## Reliability and Failure Policies

- HTTP source retrieval uses retry + exponential backoff.
- Circuit breaker protects external source dependencies from repeated failures.
- Failure paths return explicit error payloads and emit alert events.

## Observability

- Structured JSON logs with environment metadata.
- In-process metrics counters for core pipeline behaviors.
- Alert dispatch support using `ALERT_WEBHOOK_URL`.

## Security and Policy Controls

- Secrets are loaded via environment variables.
- Generated post text passes a lightweight moderation rule-set before posting.
- Event payloads include provenance metadata (model, timestamp, source URL, pipeline id).

## Notes

X posting currently supports dry-run mode (`X_DRY_RUN=true`) and a simulated posting branch for safer development and CI.
