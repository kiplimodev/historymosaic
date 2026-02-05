import time
from dataclasses import dataclass
from typing import Callable, TypeVar

from src.utils.log import log_error, log_info

T = TypeVar("T")


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    initial_delay_seconds: float = 0.5
    backoff_multiplier: float = 2.0


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout_seconds: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.failure_count = 0
        self.opened_at = 0.0

    def allow_request(self) -> bool:
        if self.failure_count < self.failure_threshold:
            return True

        if time.time() - self.opened_at >= self.recovery_timeout_seconds:
            log_info("Circuit breaker entering half-open state.")
            self.failure_count = 0
            return True

        return False

    def on_success(self) -> None:
        self.failure_count = 0
        self.opened_at = 0.0

    def on_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold and self.opened_at == 0.0:
            self.opened_at = time.time()
            log_error("Circuit breaker opened due to repeated failures.")


def run_with_retry(name: str, fn: Callable[[], T], policy: RetryPolicy) -> T:
    delay = policy.initial_delay_seconds
    last_error = None

    for attempt in range(1, policy.max_attempts + 1):
        try:
            return fn()
        except Exception as exc:
            last_error = exc
            if attempt == policy.max_attempts:
                break
            log_error(f"{name} attempt {attempt} failed: {exc}. Retrying in {delay}s")
            time.sleep(delay)
            delay *= policy.backoff_multiplier

    raise RuntimeError(f"{name} failed after {policy.max_attempts} attempts: {last_error}")
