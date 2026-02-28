import json
import asyncio
from pathlib import Path
from typing import Dict

from src.utils.openai_client import run_openai
from src.validate_event import validate_or_fix_event
from src.utils.log import log_info, log_warning, log_error

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
        tweet = rewritten.strip()

        # Enforce 280-char hard limit — retry once with explicit feedback
        if len(tweet) > 280:
            log_warning(f"Tweet too long ({len(tweet)} chars) — retrying with stricter prompt.")
            retry_prompt = (
                f"{prompt}\n\n"
                f"IMPORTANT: Your previous attempt was {len(tweet)} characters, which exceeds the 280-character X limit.\n"
                f"Rewrite it again. It MUST be under 260 characters total (including hashtags). No exceptions."
            )
            rewritten = await run_openai(retry_prompt)
            tweet = rewritten.strip()
            if len(tweet) > 280:
                log_warning(f"Retry still too long ({len(tweet)} chars) — truncating.")
                tweet = tweet[:277] + "..."

        log_info("Rewrite complete.")
        return tweet

    except Exception as e:
        log_error(f"Rewrite failed: {e}")
        return "ERROR: Could not generate rewrite."


# -------- CLI MODE --------
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m src.rewrite_x <event_file.json>")
        sys.exit(1)

    event_path = Path(sys.argv[1])

    if not event_path.exists():
        print(f"ERROR: File not found → {event_path}")
        sys.exit(1)

    # Load event JSON
    with open(event_path, "r", encoding="utf-8") as f:
        event_data = json.load(f)

    # Run async function
    tweet = asyncio.run(rewrite_for_x(event_data))

    print("\n=== GENERATED TWEET ===")
    print(tweet)
