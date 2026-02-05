import asyncio
import json
from pathlib import Path

from src.post_to_x import post_to_x
from src.rewrite_x import rewrite_for_x
from src.utils.log import log_error, log_info


async def autopost_event_file(path: str) -> dict:
    event_path = Path(path)
    if not event_path.exists():
        return {"error": f"Event file not found: {path}"}

    event = json.loads(event_path.read_text(encoding="utf-8"))
    rewritten = await rewrite_for_x(event)

    if rewritten.startswith("ERROR:"):
        log_error("Rewrite failed, aborting post.")
        return {"error": rewritten}

    result = post_to_x(rewritten)
    if "error" in result:
        return result

    log_info("Autopost succeeded", {"event_file": path, "post_id": result.get("id")})
    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python src/autopost.py events/event-file.json")
        raise SystemExit(1)

    print(asyncio.run(autopost_event_file(sys.argv[1])))
