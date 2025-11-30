import json
from pathlib import Path
from typing import Dict
from src.utils.openai_client import run_openai
from src.validate_event import validate_or_fix_event
from src.utils.log import log_info, log_error

REWRITE_PROMPT_PATH = Path("prompts/rewrite-for-x.md")

# Load rewrite prompt template
REWRITE_TEMPLATE = REWRITE_PROMPT_PATH.read_text(encoding="utf-8")


async def rewrite_for_x(event: Dict[str, any]) -> str:
    """
    Takes a validated event dictionary and rewrites it into a tweet-length post.
    Ensures the event is valid first.
    """

    # Validate and auto-fix the event
    event = await validate_or_fix_event(event)

    # Insert event JSON into template
    prompt = REWRITE_TEMPLATE.replace("{{event_json}}", json.dumps(event, indent=2))

    log_info("Generating X rewrite...")

    try:
        rewritten = await run_openai(prompt)
        log_info("Rewrite complete.")
        return rewritten.strip()

    except Exception as e:
        log_error(f"Rewrite failed: {e}")
        return "ERROR: Could not generate rewrite."
