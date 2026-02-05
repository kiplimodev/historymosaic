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

## Live Testing / Production Readiness Checklist

Before enabling real posting, run through this checklist:

1. **Validate environment config**
   - `cp .env.example .env` (if not already set)
   - Set `OPENAI_API_KEY`, `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`.
   - Keep `X_DRY_RUN=true` for first-pass tests.
2. **Run automated checks**
   - `pytest -q`
3. **Run one end-to-end pipeline test**
   - `python src/run_pipeline.py "March on Washington"`
   - Confirm a valid event file is generated under `events/`.
4. **Run safe autopost dry-run**
   - `python src/autopost.py events/<event-file>.json`
   - Verify generated content, moderation result, and payload metadata in logs.
5. **Run scheduler in dry-run mode**
   - `python src/schedule.py`
   - Confirm no errors across all events.
6. **Enable live posting intentionally**
   - Set `X_DRY_RUN=false` only after the dry-run checks pass.
   - Start with a single curated event, then progressively expand volume.

### Recommended rollout approach

- **Phase 1:** Dry-run only in production-like environment for 24h.
- **Phase 2:** Live post 1-2 manually reviewed events.
- **Phase 3:** Enable scheduled posting with alerts/webhook monitoring.
