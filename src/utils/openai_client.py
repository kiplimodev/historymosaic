import os
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:  # optional in some test/runtime contexts
    load_dotenv = None

try:
    from openai import OpenAI
except ImportError:  # optional until LLM call-time
    OpenAI = None

if load_dotenv:
    load_dotenv()

_client: Optional["OpenAI"] = None


def _get_client() -> "OpenAI":
    global _client

    if OpenAI is None:
        raise RuntimeError(
            "openai package is not installed. Install dependencies before running LLM features."
        )

    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        _client = OpenAI(api_key=api_key)

    return _client


async def run_openai(prompt: str) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content
