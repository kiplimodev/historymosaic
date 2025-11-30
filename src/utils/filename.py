# src/utils/filename.py
import re

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def build_event_filename(event: dict) -> str:
    """
    Build filename in the format:
    YYYY-MM-DD-slug.json
    """
    date = event.get("date", "unknown-date")
    title = event.get("title", "untitled-event")

    slug = slugify(title)
    return f"{date}-{slug}.json"
