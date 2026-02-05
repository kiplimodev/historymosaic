import asyncio
from pathlib import Path

from src.autopost import autopost_event_file
from src.utils.log import log_info


async def run_schedule(events_dir: str = "events") -> list[dict]:
    base = Path(events_dir)
    if not base.exists():
        return []

    results = []
    for event_file in sorted(base.glob("*.json")):
        log_info("Scheduling autopost", {"event_file": str(event_file)})
        results.append(await autopost_event_file(str(event_file)))

    return results


if __name__ == "__main__":
    print(asyncio.run(run_schedule()))
