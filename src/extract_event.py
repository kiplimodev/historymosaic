import asyncio
import json
from pathlib import Path

from src.utils.openai_client import run_openai
from src.fetch_source import fetch_wikipedia_page
from src.validate_event import validate_or_fix_event
from src.utils.log import log_info, log_error

# Load the event extraction system prompt
EXTRACT_PROMPT_PATH = Path("prompts/event-extraction.md")
EXTRACT_PROMPT = EXTRACT_PROMPT_PATH.read_text(encoding="utf-8")


async def extract_event(event_title: str):
    """
    Extracts a structured history event from Wikipedia using:
        1) Raw fetcher
        2) Event-extraction LLM
        3) Validator + automatic repair
    """

    log_info(f"Starting extraction for: {event_title}")

    # --- 1. FETCH WIKIPEDIA ---
    # SAFER FIX: Handle dict OR string input
    title = event_title["title"] if isinstance(event_title, dict) else event_title

    wiki_text = fetch_wikipedia_page(title)
    if "error" in wiki_text:
        log_error(f"Failed to fetch base text: {wiki_text['error']}")
        return {"error": wiki_text["error"]}

    # --- 2. COMPOSE LLM INPUT ---
    llm_input = f"""
{EXTRACT_PROMPT}

### EVENT REQUEST
Title: {title}

### SOURCE TEXT
{wiki_text.get("summary", "")}
"""

    # --- 3. RUN EXTRACTION MODEL ---
    try:
        raw_output = await run_openai(llm_input)
    except Exception as e:
        log_error(f"Extraction LLM failed: {e}")
        return {"error": str(e)}

    # --- 4. PARSE LLM OUTPUT ---
    try:
        event_json = json.loads(raw_output)
    except json.JSONDecodeError:
        log_error("LLM returned non-JSON. Attempting auto-fix.")
        event_json = {"title": title, "raw_output": raw_output}

    # --- 5. VALIDATE & AUTO-REPAIR ---
    clean_event = await validate_or_fix_event(event_json)

    log_info("Extraction complete.")
    return clean_event


# -------- OPTIONAL: CLI TEST --------
if __name__ == "__main__":
    event = asyncio.run(extract_event("March on Washington"))
    print(json.dumps(event, indent=2))
