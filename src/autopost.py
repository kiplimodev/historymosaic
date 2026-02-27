# src/autopost.py
import json
import asyncio
from pathlib import Path
from typing import Optional

from src.validate_event import validate_or_fix_event
from src.rewrite_x import rewrite_for_x
from src.post_to_x import post_tweet
from src.utils.log import log_info, log_warning, log_error

EVENTS_DIR = Path("events")
POSTED_LOG = EVENTS_DIR / "posted_log.json"


# --------------------------------------------------
# Posted log helpers
# --------------------------------------------------

def load_posted_log() -> list[str]:
    """Return the list of already-posted event filenames."""
    if not POSTED_LOG.exists():
        return []
    try:
        return json.loads(POSTED_LOG.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        log_warning("posted_log.json is corrupt or unreadable — starting fresh.")
        return []


def save_posted_log(posted: list[str]) -> None:
    EVENTS_DIR.mkdir(exist_ok=True)
    POSTED_LOG.write_text(json.dumps(posted, indent=2), encoding="utf-8")


# --------------------------------------------------
# Event selection
# --------------------------------------------------

def pick_next_event(posted: list[str]) -> Optional[Path]:
    """
    Return the Path of the next unposted event JSON file,
    sorted chronologically by filename (YYYY-MM-DD-slug.json).
    Returns None if all events have been posted.
    """
    all_events = sorted(
        p for p in EVENTS_DIR.glob("*.json")
        if p.name != POSTED_LOG.name
    )

    for path in all_events:
        if path.name not in posted:
            return path

    return None


# --------------------------------------------------
# Main autopost pipeline
# --------------------------------------------------

async def run_autopost() -> None:
    """
    Full autopost pipeline:
      1. Pick next unposted event
      2. Validate it
      3. Rewrite for X
      4. Post to X
      5. Mark as posted
    """
    log_info("--- Autopost cycle starting ---")

    posted = load_posted_log()
    event_path = pick_next_event(posted)

    if event_path is None:
        log_warning("No unposted events remaining. Add more events to continue posting.")
        return

    log_info(f"Selected event: {event_path.name}")

    # --- Load event ---
    try:
        event = json.loads(event_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        log_error(f"Failed to load {event_path.name}: {e}")
        return

    # --- Validate ---
    event = await validate_or_fix_event(event)

    # --- Rewrite for X ---
    tweet = await rewrite_for_x(event)

    if tweet.startswith("ERROR"):
        log_error(f"Rewrite failed for {event_path.name} — skipping.")
        return

    log_info(f"Tweet ready ({len(tweet)} chars): {tweet[:80]}...")

    # --- Post to X ---
    result = post_tweet(tweet)

    if result["success"]:
        posted.append(event_path.name)
        save_posted_log(posted)
        log_info(f"Posted and logged: {event_path.name} (tweet ID: {result['tweet_id']})")
    else:
        log_error(f"Post failed for {event_path.name}: {result.get('detail', 'unknown error')}")

    log_info("--- Autopost cycle complete ---")


# -------- CLI TEST --------
if __name__ == "__main__":
    asyncio.run(run_autopost())
