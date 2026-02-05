import os
from typing import Any, Optional

from src.utils.config import load_config
from src.utils.metrics import incr
from src.utils.reliability import RetryPolicy, run_with_retry

_client: Optional[Any] = None


def _get_client() -> Any:
    global _client

    if _client is None:
        from dotenv import load_dotenv
        from openai import OpenAI

        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        _client = OpenAI(api_key=api_key)

    return _client


async def run_openai(prompt: str) -> str:
    cfg = load_config()
    client = _get_client()

    def _call() -> str:
        response = client.chat.completions.create(
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
