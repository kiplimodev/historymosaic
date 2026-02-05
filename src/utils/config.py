import os
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AppConfig:
    environment: str
    log_level: str
    openai_model: str
    openai_timeout_seconds: int
    openai_max_retries: int
    x_dry_run: bool
    alert_webhook_url: str


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_config() -> AppConfig:
    return AppConfig(
        environment=os.getenv("ENVIRONMENT", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        openai_timeout_seconds=int(os.getenv("OPENAI_TIMEOUT_SECONDS", "30")),
        openai_max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "3")),
        x_dry_run=_as_bool(os.getenv("X_DRY_RUN", "true"), default=True),
        alert_webhook_url=os.getenv("ALERT_WEBHOOK_URL", ""),
    )


def validate_startup_environment() -> List[str]:
    errors = []

    timeout = os.getenv("OPENAI_TIMEOUT_SECONDS", "30")
    retries = os.getenv("OPENAI_MAX_RETRIES", "3")
    if not timeout.isdigit() or int(timeout) <= 0:
        errors.append("OPENAI_TIMEOUT_SECONDS must be a positive integer")
    if not retries.isdigit() or int(retries) < 0:
        errors.append("OPENAI_MAX_RETRIES must be a non-negative integer")

    return errors
