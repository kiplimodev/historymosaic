# src/autopost.py
import json
import asyncio
import os
from pathlib import Path
from typing import Optional

from src.validate_event import validate_or_fix_event
from src.rewrite_x import rewrite_for_x
from src.post_to_x import post_tweet
from src.utils.log import log_info, log_warning, log_error
from src.utils.alert import send_alert

# --------------------------------------------------
# Config
# --------------------------------------------------
EVENTS_DIR = Path("events")

# DATA_DIR is where posted_log.json lives.
# On Railway: mount a Volume at /data and set DATA_DIR=/data
# Locally: defaults to the events/ directory
_data_dir = Path(os.getenv("DATA_DIR", str(EVENTS_DIR)))
POSTED_LOG = _data_dir / "posted_log.json"

# Set DRY_RUN=true in .env to rewrite tweets without posting them
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"


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
    _data_dir.mkdir(parents=True, exist_ok=True)
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
      4. Post to X (or dry-run)
      5. Mark as posted
    """
    log_info("--- Autopost cycle starting ---")

    if DRY_RUN:
        log_info("DRY RUN mode — tweets will be generated but not posted.")

    posted = load_posted_log()
    event_path = pick_next_event(posted)

    if event_path is None:
        msg = "No unposted events remaining. Add more events to continue posting."
        log_warning(msg)
        send_alert(f"WARNING: {msg}")
        return

    log_info(f"Selected event: {event_path.name}")

    # --- Load event ---
    try:
        event = json.loads(event_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        msg = f"Failed to load {event_path.name}: {e}"
        log_error(msg)
        send_alert(f"ERROR: {msg}")
        return

    # --- Validate ---
    event = await validate_or_fix_event(event)

    # --- Rewrite for X ---
    tweet = await rewrite_for_x(event)

    if tweet.startswith("ERROR"):
        msg = f"Rewrite failed for {event_path.name} — skipping."
        log_error(msg)
        send_alert(f"ERROR: {msg}")
        return

    log_info(f"Tweet ready ({len(tweet)} chars): {tweet[:80]}...")

    # --- Dry run: print and stop ---
    if DRY_RUN:
        log_info(f"[DRY RUN] Would have posted:\n{tweet}")
        log_info("--- Autopost cycle complete (dry run) ---")
        return

    # --- Post to X ---
    result = post_tweet(tweet)

    if result["success"]:
        posted.append(event_path.name)
        save_posted_log(posted)
        log_info(f"Posted and logged: {event_path.name} (tweet ID: {result['tweet_id']})")
    else:
        msg = f"Post failed for {event_path.name}: {result.get('detail', 'unknown error')}"
        log_error(msg)
        send_alert(f"ERROR: {msg}")

    log_info("--- Autopost cycle complete ---")


# -------- CLI TEST --------
if __name__ == "__main__":
    asyncio.run(run_autopost())
