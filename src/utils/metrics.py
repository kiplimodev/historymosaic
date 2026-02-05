from collections import defaultdict
from typing import Dict

_METRICS = defaultdict(int)


def incr(metric_name: str, value: int = 1) -> None:
    _METRICS[metric_name] += value


def snapshot() -> Dict[str, int]:
    return dict(_METRICS)


def reset() -> None:
    _METRICS.clear()
