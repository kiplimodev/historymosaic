import asyncio
import json
from pathlib import Path
from typing import Any, Dict

from src.utils.openai_client import run_openai
from src.validate_event import validate_or_fix_event
from src.utils.log import log_info, log_error

# Load the event extraction system prompt
EXTRACT_PROMPT_PATH = Path("prompts/event-extraction.md")
EXTRACT_PROMPT = EXTRACT_PROMPT_PATH.read_text(encoding="utf-8")


async def extract_event(source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts a structured history event from a fetched source dictionary.

    Required source keys:
      - title: str
      - summary: str
    Optional source keys:
      - url: str
      - html: str
    """

    if "error" in source:
        return {"error": source["error"]}

    event_title = source.get("title", "Untitled event")
    source_summary = source.get("summary", "")
    source_url = source.get("url", "")

    log_info(f"Starting extraction for: {event_title}")

    llm_input = f"""
{EXTRACT_PROMPT}

### EVENT REQUEST
Title: {event_title}

### SOURCE URL
{source_url}

### SOURCE TEXT
{source_summary}
"""

    try:
        raw_output = await run_openai(llm_input)
    except Exception as e:
        log_error(f"Extraction LLM failed: {e}")
        return {"error": str(e)}

    try:
        event_json = json.loads(raw_output)
    except json.JSONDecodeError:
        log_error("LLM returned non-JSON. Attempting auto-fix.")
        event_json = {
            "title": event_title,
            "summary": source_summary,
            "sources": [source_url] if source_url else [],
            "raw_output": raw_output,
        }

    clean_event = await validate_or_fix_event(event_json)

    log_info("Extraction complete.")
    return clean_event


# -------- OPTIONAL: CLI TEST --------
if __name__ == "__main__":
    from src.fetch_source import fetch_wikipedia_page

    source = fetch_wikipedia_page("March on Washington")
    event = asyncio.run(extract_event(source))
    print(json.dumps(event, indent=2))
