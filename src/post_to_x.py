# src/post_to_x.py
import time
import tweepy
from typing import Dict, Any

from src.utils.x_client import get_x_client
from src.utils.log import log_info, log_error, log_warning

MAX_TWEET_LENGTH = 280
RATE_LIMIT_WAIT_SECONDS = 15 * 60  # 15 minutes


def post_tweet(text: str) -> Dict[str, Any]:
    """
    Post a single tweet to X.

    Returns a result dict:
        {"success": True,  "tweet_id": "..."}
        {"success": False, "error": "rate_limit" | "forbidden" | "api_error", "detail": "..."}
    """

    # --- Guard: enforce character limit ---
    if len(text) > MAX_TWEET_LENGTH:
        log_warning(
            f"Tweet is {len(text)} chars — truncating to {MAX_TWEET_LENGTH}."
        )
        text = text[:MAX_TWEET_LENGTH]

    client = get_x_client()

    try:
        response = client.create_tweet(text=text)
        tweet_id = response.data["id"]
        log_info(f"Tweet posted successfully. ID: {tweet_id}")
        return {"success": True, "tweet_id": str(tweet_id)}

    except tweepy.TooManyRequests as e:
        log_error(f"Rate limit hit. Waiting {RATE_LIMIT_WAIT_SECONDS // 60} minutes before retry.")
        time.sleep(RATE_LIMIT_WAIT_SECONDS)
        try:
            response = client.create_tweet(text=text)
            tweet_id = response.data["id"]
            log_info(f"Tweet posted on retry. ID: {tweet_id}")
            return {"success": True, "tweet_id": str(tweet_id)}
        except tweepy.TweepyException as retry_err:
            log_error(f"Retry also failed: {retry_err}")
            return {"success": False, "error": "rate_limit", "detail": str(retry_err)}

    except tweepy.Forbidden as e:
        log_error(
            f"Forbidden (403): {e} — Check that your app has Read+Write permissions "
            "and that the Access Token was generated after setting those permissions."
        )
        return {"success": False, "error": "forbidden", "detail": str(e)}

    except tweepy.Unauthorized as e:
        log_error(f"Unauthorized (401): {e} — Check your API credentials in .env.")
        return {"success": False, "error": "unauthorized", "detail": str(e)}

    except tweepy.TweepyException as e:
        log_error(f"X API error: {e}")
        return {"success": False, "error": "api_error", "detail": str(e)}


# -------- CLI TEST --------
if __name__ == "__main__":
    result = post_tweet("HistoryMosaic bot is live. History, one post at a time. 🏛️")
    print(result)
