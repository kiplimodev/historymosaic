# src/utils/filename.py
import re
from dateutil import parser as dateutil_parser


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def normalize_date(date_str: str) -> str:
    """
    Normalize any recognizable date string to ISO 8601 (YYYY-MM-DD).
    Falls back to the original string if parsing fails.

    Examples:
        "July 20, 1969"  -> "1969-07-20"
        "Aug 28, 1963"   -> "1963-08-28"
        "1969-07-20"     -> "1969-07-20"
    """
    try:
        parsed = dateutil_parser.parse(date_str, default=None)
        return parsed.strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return date_str


def build_event_filename(event: dict) -> str:
    """
    Build filename in the format: YYYY-MM-DD-slug.json
    Normalizes the date to ISO 8601 before building the name.
    """
    date = event.get("date", "unknown-date")
    title = event.get("title", "untitled-event")

    normalized = normalize_date(date)
    slug = slugify(title)
    return f"{normalized}-{slug}.json"
