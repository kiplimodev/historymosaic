import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_openai(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",   # Very cheap + powerful
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # NEW OpenAI API response format (v2.x)
    return response.choices[0].message.content
