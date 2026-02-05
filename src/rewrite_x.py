import json
from pathlib import Path
from typing import Dict

from src.utils.log import log_info, log_error
from src.utils.metrics import incr
from src.utils.openai_client import run_openai
from src.utils.security import moderate_output
from src.validate_event import validate_or_fix_event

REWRITE_PROMPT_PATH = Path("prompts/rewrite-for-x.md")
REWRITE_TEMPLATE = REWRITE_PROMPT_PATH.read_text(encoding="utf-8")


async def rewrite_for_x(event: Dict[str, any]) -> str:
    event = await validate_or_fix_event(event)
    prompt = REWRITE_TEMPLATE.replace("{{event_json}}", json.dumps(event, indent=2))

    log_info("Generating X rewrite...")

    try:
        rewritten = (await run_openai(prompt)).strip()
        if not moderate_output(rewritten):
            incr("rewrite.blocked")
            return "ERROR: Output blocked by moderation policy."

        incr("rewrite.success")
        log_info("Rewrite complete.")
        return rewritten
    except Exception as e:
        incr("rewrite.error")
        log_error(f"Rewrite failed: {e}")
        return "ERROR: Could not generate rewrite."
