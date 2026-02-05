import datetime
import json
import os
from typing import Any, Dict


def _emit(level: str, message: str, context: Dict[str, Any] | None = None) -> None:
    payload = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "level": level,
        "message": message,
        "environment": os.getenv("ENVIRONMENT", "development"),
    }
    if context:
        payload["context"] = context
    print(json.dumps(payload, ensure_ascii=False))


def log_info(message: str, context: Dict[str, Any] | None = None) -> None:
    _emit("INFO", message, context)


def log_error(message: str, context: Dict[str, Any] | None = None) -> None:
    _emit("ERROR", message, context)
