# src/autopost.py
import json
import asyncio
import os
from pathlib import Path
from typing import Optional

from src.validate_event import validate_or_fix_event
from src.rewrite_x import rewrite_for_x
from src.post_to_x import post_tweet
from src.fetch_onthisday import fetch_onthisday_event
from src.extract_event import extract_event
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
    """Return the list of already-posted event titles/filenames."""
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
# Seed event fallback
# --------------------------------------------------

def pick_next_seed_event(posted: list[str]) -> Optional[Path]:
    """
    Return the next unposted seed event JSON file,
    sorted chronologically by filename (YYYY-MM-DD-slug.json).
    Returns None if all seed events have been posted.
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
      1. Try live fetch from Wikipedia On This Day
      2. If live fetch fails, fall back to next seed event
      3. Validate the event
      4. Rewrite for X
      5. Post to X (or dry-run)
      6. Mark as posted
    """
    log_info("--- Autopost cycle starting ---")

    if DRY_RUN:
        log_info("DRY RUN mode — tweets will be generated but not posted.")

    posted = load_posted_log()
    event = None
    post_key = None  # What we store in posted log to prevent duplicates

    # --------------------------------------------------
    # 1. Try live fetch
    # --------------------------------------------------
    log_info("Attempting live fetch from Wikipedia On This Day...")
    source = fetch_onthisday_event()

    if "error" not in source:
        # Check if we already posted this title today
        post_key = source["title"]
        if post_key in posted:
            log_info(f"Already posted '{post_key}' — trying seed fallback.")
        else:
            log_info(f"Live event fetched: {source.get('year', '')} — {source['title']}")
            event = await extract_event(source)
            if "error" in event:
                log_warning(f"Live extraction failed: {event['error']} — falling back to seed.")
                event = None
    else:
        log_warning(f"Live fetch failed: {source['error']} — falling back to seed.")

    # --------------------------------------------------
    # 2. Fall back to seed events if live failed
    # --------------------------------------------------
    if event is None:
        seed_path = pick_next_seed_event(posted)

        if seed_path is None:
            msg = "No unposted events remaining (live fetch failed and seed events exhausted)."
            log_warning(msg)
            send_alert(f"WARNING: {msg}")
            return

        log_info(f"Using seed event: {seed_path.name}")
        try:
            event = json.loads(seed_path.read_text(encoding="utf-8"))
            post_key = seed_path.name
        except (json.JSONDecodeError, OSError) as e:
            msg = f"Failed to load seed event {seed_path.name}: {e}"
            log_error(msg)
            send_alert(f"ERROR: {msg}")
            return

        # Validate seed events (live events are validated inside extract_event)
        event = await validate_or_fix_event(event)

    # --------------------------------------------------
    # 3. Rewrite for X
    # --------------------------------------------------
    tweet = await rewrite_for_x(event)

    if tweet.startswith("ERROR"):
        msg = f"Rewrite failed for '{post_key}' — skipping."
        log_error(msg)
        send_alert(f"ERROR: {msg}")
        return

    log_info(f"Tweet ready ({len(tweet)} chars): {tweet[:80]}...")

    # --------------------------------------------------
    # 5. Dry run
    # --------------------------------------------------
    if DRY_RUN:
        log_info(f"[DRY RUN] Would have posted:\n{tweet}")
        log_info("--- Autopost cycle complete (dry run) ---")
        return

    # --------------------------------------------------
    # 6. Post to X
    # --------------------------------------------------
    result = post_tweet(tweet)

    if result["success"]:
        posted.append(post_key)
        save_posted_log(posted)
        log_info(f"Posted and logged: '{post_key}' (tweet ID: {result['tweet_id']})")
    else:
        msg = f"Post failed for '{post_key}': {result.get('detail', 'unknown error')}"
        log_error(msg)
        send_alert(f"ERROR: {msg}")

    log_info("--- Autopost cycle complete ---")


# -------- CLI TEST --------
if __name__ == "__main__":
    asyncio.run(run_autopost())
