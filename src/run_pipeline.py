# src/run_pipeline.py

import json
import asyncio
import sys
from pathlib import Path

from src.fetch_source import fetch_wikipedia_page
from src.extract_event import extract_event
from src.validate_event import validate_or_fix_event
from src.utils.filename import build_event_filename
from src.utils.log import log_info, log_error


EVENTS_DIR = Path("events")


async def run(query: str):
    log_info(f"Running pipeline for query: {query}")

    # -----------------------------------
    # 1. Fetch source
    # -----------------------------------
    source = fetch_wikipedia_page(query)

    if "error" in source:
        log_error(f"Source fetch failed: {source['error']}")
        return

    log_info("Fetched source text.")

    # -----------------------------------
    # 2. Extract event (LLM or fallback)
    # -----------------------------------
    event = await extract_event(source)
    if "error" in event:
        log_error(f"Event extraction failed: {event['error']}")
        return

    log_info("Extracted event dictionary.")

    # -----------------------------------
    # 3. Validate / Auto-fix schema
    # -----------------------------------
    validated_event = await validate_or_fix_event(event)
    log_info("Event validated.")

    # -----------------------------------
    # 4. Build filename
    # -----------------------------------
    filename = build_event_filename(validated_event)
    filepath = EVENTS_DIR / filename

    EVENTS_DIR.mkdir(exist_ok=True)

    # -----------------------------------
    # 5. Save output
    # -----------------------------------
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(validated_event, f, indent=2)

    log_info(f"Saved event → {filepath}")
    print(f"\nDONE → {filepath}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/run_pipeline.py \"Search term\"")
        sys.exit(1)

    query = sys.argv[1]
    asyncio.run(run(query))
