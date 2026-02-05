from src.utils.log import log_error, log_info
from src.utils.security import moderate_output
from src.utils.x_client import XClient


def post_to_x(text: str) -> dict:
    if not moderate_output(text):
        return {"error": "Moderation blocked post"}

    client = XClient()
    try:
        result = client.post(text)
        log_info("X post complete", result)
        return result
    except Exception as exc:
        log_error(f"Failed to post to X: {exc}")
        return {"error": str(exc)}
