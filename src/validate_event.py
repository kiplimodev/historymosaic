import json
from typing import Dict, Any

from src.utils.alerts import send_alert
from src.utils.log import log_info, log_error
from src.utils.metrics import incr
from src.utils.openai_client import run_openai


def validate_event_schema(event: Dict[str, Any]) -> bool:
    required_fields = {
        "title": str,
        "date": str,
        "summary": str,
        "sources": list,
    }

    for field, field_type in required_fields.items():
        if field not in event:
            log_error(f"Missing field: {field}")
            return False

        if not isinstance(event[field], field_type):
            log_error(f"Wrong type for field '{field}': expected {field_type}, got {type(event[field])}")
            return False

    if any(not isinstance(src, str) for src in event["sources"]):
        log_error("All items in 'sources' must be strings.")
        return False

    return True


async def llm_fix_event(event: Dict[str, Any]) -> Dict[str, Any]:
    prompt = f"""
You are a JSON validation engine.
Fix this event so that it has exactly the fields:

- title: string
- date: string (any readable format)
- summary: string
- sources: list of strings

Here is the event to fix:

{json.dumps(event, indent=2)}

Return ONLY corrected JSON. No backticks. No explanations.
"""

    response = await run_openai(prompt)

    try:
        cleaned = json.loads(response)
        log_info("LLM successfully fixed the event.")
        incr("validate.repair_success")
        return cleaned
    except json.JSONDecodeError:
        incr("validate.repair_failed")
        log_error("LLM returned invalid JSON. Using original event.")
        return event


async def validate_or_fix_event(event: Dict[str, Any]) -> Dict[str, Any]:
    if validate_event_schema(event):
        incr("validate.success")
        log_info("Event passed schema validation.")
        return event

    incr("validate.failed")
    log_info("Event failed validation — attempting LLM repair...")
    repaired = await llm_fix_event(event)

    if validate_event_schema(repaired):
        incr("validate.repair_valid")
        log_info("Repaired event passed validation.")
        return repaired

    send_alert("event_validation_failure", {"event": event})
    log_error("Repaired event still invalid — returning original event.")
    return event
