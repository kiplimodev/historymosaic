import json

from src.utils.config import load_config
from src.utils.log import log_error, log_info


def send_alert(event: str, details: dict) -> None:
    cfg = load_config()
    payload = {"event": event, "details": details, "environment": cfg.environment}

    if not cfg.alert_webhook_url:
        log_info(f"ALERT (no webhook configured): {json.dumps(payload)}")
        return

    try:
        import requests

        requests.post(cfg.alert_webhook_url, json=payload, timeout=5)
    except Exception as exc:
        log_error(f"Failed to dispatch alert: {exc}")
