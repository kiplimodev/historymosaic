import os
import openai
from typing import Any, Optional

from src.utils.config import load_config
from src.utils.log import log_info
from src.utils.metrics import incr
from src.utils.reliability import RetryPolicy, run_with_retry


async def run_openai(prompt: str) -> str:
    cfg = load_config()
    from dotenv import load_dotenv
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    def _call() -> str:
        response = openai.ChatCompletion.create(
            model=cfg.openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            timeout=cfg.openai_timeout_seconds,
        )
        content = response.choices[0].message.content
        return content or ""

    result = run_with_retry(
        "openai_chat_completion",
        _call,
        RetryPolicy(max_attempts=cfg.openai_max_retries, initial_delay_seconds=0.5),
    )
    incr("openai.calls")
    return result
