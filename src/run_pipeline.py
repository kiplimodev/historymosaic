import asyncio
import json
import sys
from pathlib import Path

from src.extract_event import extract_event
from src.fetch_source import fetch_wikipedia_page
from src.validate_event import validate_or_fix_event
from src.utils.alerts import send_alert
from src.utils.config import validate_startup_environment
from src.utils.filename import build_event_filename
from src.utils.log import log_info, log_error
from src.utils.metrics import snapshot

EVENTS_DIR = Path("events")


async def run(query: str):
    startup_errors = validate_startup_environment()
    if startup_errors:
        for err in startup_errors:
            log_error(f"Startup validation error: {err}")
        return

    log_info(f"Running pipeline for query: {query}")

    source = fetch_wikipedia_page(query)
    if "error" in source:
        log_error(f"Source fetch failed: {source['error']}")
        send_alert("source_fetch_failure", {"query": query, "error": source["error"]})
        return

    log_info("Fetched source text.")

    event = await extract_event(source)
    if "error" in event:
        log_error(f"Event extraction failed: {event['error']}")
        send_alert("event_extraction_failure", {"query": query, "error": event["error"]})
        return

    log_info("Extracted event dictionary.")

    validated_event = await validate_or_fix_event(event)
    log_info("Event validated.")

    filename = build_event_filename(validated_event)
    filepath = EVENTS_DIR / filename

    EVENTS_DIR.mkdir(exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(validated_event, f, indent=2)

    log_info("Saved event", {"filepath": str(filepath)})
    log_info("Metrics snapshot", snapshot())
    print(f"\nDONE → {filepath}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/run_pipeline.py \"Search term\"")
        sys.exit(1)

    query = sys.argv[1]
    asyncio.run(run(query))
