# src/schedule.py
import asyncio
import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.autopost import run_autopost
from src.utils.log import log_info, log_error
from src.utils.alert import send_alert

load_dotenv()

# --------------------------------------------------
# Config — set POST_TIME_UTC in .env to change time
# Format: "HH:MM" in 24-hour UTC
# Default: 12:00 UTC
# --------------------------------------------------
_raw_time = os.getenv("POST_TIME_UTC", "12:00")
try:
    _hour, _minute = [int(x) for x in _raw_time.strip().split(":")]
except ValueError:
    log_error(f"Invalid POST_TIME_UTC value '{_raw_time}' — falling back to 12:00 UTC.")
    _hour, _minute = 12, 0


def job() -> None:
    """Wrapper so APScheduler (sync) can call the async autopost pipeline."""
    try:
        asyncio.run(run_autopost())
    except Exception as e:
        msg = f"Autopost job raised an unexpected error: {e}"
        log_error(msg)
        send_alert(f"CRITICAL: {msg}")


def start() -> None:
    scheduler = BlockingScheduler(timezone="UTC")

    scheduler.add_job(
        job,
        trigger=CronTrigger(hour=_hour, minute=_minute, timezone="UTC"),
        id="daily_autopost",
        name="Daily HistoryMosaic Post",
        misfire_grace_time=60 * 10,  # Allow up to 10 min late start
        replace_existing=True,
    )

    log_info(f"Scheduler started — posting daily at {_hour:02d}:{_minute:02d} UTC.")
    log_info("Press Ctrl+C to stop.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log_info("Scheduler stopped.")


if __name__ == "__main__":
    start()
