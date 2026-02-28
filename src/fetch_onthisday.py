# src/fetch_onthisday.py
import requests
from datetime import datetime, timezone
from src.utils.log import log_info, log_error

ONTHISDAY_URL = "https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
HEADERS = {
    "User-Agent": "HistoryMosaicBot/1.0 (https://github.com/kiplimodev/historymosaic)"
}


def _score_event(event: dict) -> int:
    """
    Score an event by historical significance.
    More Wikipedia page links = more significant.
    """
    return len(event.get("pages", []))


def fetch_onthisday_event() -> dict:
    """
    Fetch the most significant historical event for today's date
    using Wikipedia's On This Day API.

    Returns a source dict compatible with extract_event():
        {"title": ..., "url": ..., "summary": ..., "year": ...}

    Returns {"error": ...} on failure.
    """
    today = datetime.now(timezone.utc)
    month = today.month
    day = today.day

    url = ONTHISDAY_URL.format(month=month, day=day)
    log_info(f"Fetching On This Day events for {today.strftime('%B %d')}...")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        log_error(f"On This Day API request failed: {e}")
        return {"error": str(e)}

    events = response.json().get("events", [])

    if not events:
        return {"error": f"No On This Day events found for {month}/{day}"}

    # Pick the most significant event (most Wikipedia page links)
    event = max(events, key=_score_event)

    pages = event.get("pages", [])
    page = pages[0] if pages else {}

    title = page.get("title") or event.get("text", "")[:60]
    summary = page.get("extract") or event.get("text", "")
    page_url = (
        page.get("content_urls", {}).get("desktop", {}).get("page", "")
        or f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    )
    year = str(event.get("year", ""))

    if not title or not summary:
        return {"error": "On This Day event missing title or summary"}

    log_info(f"Selected event: {year} — {title}")

    return {
        "title": title,
        "url": page_url,
        "summary": summary,
        "year": year,
    }
