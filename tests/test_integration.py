import pathlib
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import asyncio
import json
from pathlib import Path

from src import extract_event as extract_module
from src.autopost import autopost_event_file
from src.post_to_x import post_to_x
from src.schedule import run_schedule
from src.utils.config import validate_startup_environment
from src.utils.reliability import CircuitBreaker, RetryPolicy, run_with_retry


def test_retry_succeeds_after_transient_failures():
    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("transient")
        return "ok"

    result = run_with_retry("flaky", flaky, RetryPolicy(max_attempts=3, initial_delay_seconds=0))
    assert result == "ok"


def test_circuit_breaker_opens_after_threshold():
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=999)
    assert breaker.allow_request() is True
    breaker.on_failure()
    assert breaker.allow_request() is True
    breaker.on_failure()
    assert breaker.allow_request() is False


def test_startup_validation_detects_invalid_numeric_env(monkeypatch):
    monkeypatch.setenv("OPENAI_TIMEOUT_SECONDS", "abc")
    errors = validate_startup_environment()
    assert any("OPENAI_TIMEOUT_SECONDS" in e for e in errors)


def test_post_to_x_blocked_by_moderation():
    result = post_to_x("we should kill all people")
    assert result["error"] == "Moderation blocked post"


def test_extract_event_attaches_provenance(monkeypatch):
    async def fake_run_openai(prompt: str):
        return '{"title":"T","date":"2000-01-01","summary":"S","sources":["u"]}'

    async def fake_validate(event):
        return event

    monkeypatch.setattr(extract_module, "run_openai", fake_run_openai)
    monkeypatch.setattr(extract_module, "validate_or_fix_event", fake_validate)

    source = {"title": "A", "summary": "B", "url": "https://example.com"}
    result = asyncio.run(extract_module.extract_event(source))

    assert "provenance" in result
    assert result["provenance"]["source_url"] == "https://example.com"


def test_autopost_and_schedule_end_to_end(monkeypatch, tmp_path: Path):
    async def fake_rewrite(event):
        return "A safe historical post #history"

    monkeypatch.setattr("src.autopost.rewrite_for_x", fake_rewrite)

    event = {
        "title": "March on Washington",
        "date": "1963-08-28",
        "summary": "Civil rights march",
        "sources": ["https://example.com"],
    }

    events_dir = tmp_path / "events"
    events_dir.mkdir()
    event_path = events_dir / "event.json"
    event_path.write_text(json.dumps(event), encoding="utf-8")

    result = asyncio.run(autopost_event_file(str(event_path)))
    assert result["status"] in {"dry_run", "posted"}

    all_results = asyncio.run(run_schedule(str(events_dir)))
    assert len(all_results) == 1
    assert all_results[0]["status"] in {"dry_run", "posted"}
