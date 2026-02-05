from datetime import datetime, timezone
from typing import Dict, Any

from src.utils.log import log_error

BLOCKED_TERMS = {
    "hate",
    "kill all",
    "genocide now",
}


def moderate_output(text: str) -> bool:
    normalized = text.lower()
    for term in BLOCKED_TERMS:
        if term in normalized:
            log_error(f"Moderation failed due to blocked term: {term}")
            return False
    return True


def attach_provenance(event: Dict[str, Any], model: str, source_url: str) -> Dict[str, Any]:
    event = dict(event)
    event["provenance"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "source_url": source_url,
        "pipeline": "historymosaic-v1",
    }
    return event
