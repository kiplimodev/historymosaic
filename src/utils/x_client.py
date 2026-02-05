import os
from typing import Dict, Any

from src.utils.config import load_config
from src.utils.log import log_info
from src.utils.metrics import incr


class XClient:
    def __init__(self):
        self.cfg = load_config()

    def _credentials_present(self) -> bool:
        required = [
            os.getenv("X_API_KEY"),
            os.getenv("X_API_SECRET"),
            os.getenv("X_ACCESS_TOKEN"),
            os.getenv("X_ACCESS_TOKEN_SECRET"),
        ]
        return all(required)

    def post(self, text: str) -> Dict[str, Any]:
        if self.cfg.x_dry_run:
            incr("x.post.dry_run")
            log_info("Dry-run enabled. Skipping real X post.", {"text": text})
            return {"status": "dry_run", "id": "dry-run-id"}

        if not self._credentials_present():
            raise RuntimeError("X credentials missing. Set X_API_KEY/X_API_SECRET/X_ACCESS_TOKEN/X_ACCESS_TOKEN_SECRET")

        # Placeholder for real integration.
        incr("x.post.success")
        return {"status": "posted", "id": "simulated-post-id"}
