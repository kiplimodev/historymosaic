# src/utils/x_client.py
import os
import tweepy
from dotenv import load_dotenv
from src.utils.log import log_error

load_dotenv()


def get_x_client() -> tweepy.Client:
    """
    Build and return an authenticated Tweepy client using OAuth 1.0a.
    This allows posting tweets as the authenticated user.
    """
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    missing = [
        name for name, val in {
            "X_API_KEY": api_key,
            "X_API_SECRET": api_secret,
            "X_ACCESS_TOKEN": access_token,
            "X_ACCESS_TOKEN_SECRET": access_token_secret,
        }.items() if not val
    ]

    if missing:
        log_error(f"Missing X credentials in .env: {', '.join(missing)}")
        raise EnvironmentError(f"Missing X credentials: {', '.join(missing)}")

    return tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
