import asyncio
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.validate_event import validate_event_schema
from src.utils.filename import build_event_filename
from src import extract_event as extract_module


def test_validate_event_schema_accepts_valid_payload():
    event = {
        "title": "March on Washington",
        "date": "1963-08-28",
        "summary": "A major civil rights march in Washington, D.C.",
        "sources": ["https://en.wikipedia.org/wiki/March_on_Washington_for_Jobs_and_Freedom"],
    }
    assert validate_event_schema(event) is True


def test_validate_event_schema_rejects_missing_required_fields():
    event = {
        "title": "March on Washington",
        "summary": "Missing date and sources",
    }
    assert validate_event_schema(event) is False


def test_build_event_filename_uses_date_and_slugified_title():
    filename = build_event_filename({"date": "1963-08-28", "title": "March on Washington!"})
    assert filename == "1963-08-28-march-on-washington.json"


def test_extract_event_uses_summary_field_in_prompt(monkeypatch):
    captured = {}

    async def fake_run_openai(prompt: str):
        captured["prompt"] = prompt
        return '{"title":"X","date":"1963-08-28","summary":"Y","sources":["u"]}'

    async def fake_validate(event):
        return event

    monkeypatch.setattr(extract_module, "run_openai", fake_run_openai)
    monkeypatch.setattr(extract_module, "validate_or_fix_event", fake_validate)

    source = {
        "title": "March on Washington",
        "summary": "This is the canonical source summary.",
        "url": "https://example.com/march",
    }

    result = asyncio.run(extract_module.extract_event(source))

    assert result["title"] == "X"
    assert "This is the canonical source summary." in captured["prompt"]
    assert "https://example.com/march" in captured["prompt"]
