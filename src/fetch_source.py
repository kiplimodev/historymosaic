from src.utils.log import log_info, log_error
from src.utils.metrics import incr
from src.utils.reliability import CircuitBreaker, RetryPolicy, run_with_retry

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": "HistoryMosaicBot/1.0 (https://github.com/kiplimodev/historymosaic)"
}

WIKI_BREAKER = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=60)


def _get_json(url: str, **kwargs):
    import requests

    response = requests.get(url, **kwargs)
    response.raise_for_status()
    return response.json()


def _get_text(url: str, **kwargs):
    import requests

    response = requests.get(url, **kwargs)
    response.raise_for_status()
    return response.text


def fetch_wikipedia_page(title: str) -> dict:
    log_info(f"Fetching Wikipedia page for: {title}")

    if not WIKI_BREAKER.allow_request():
        incr("source_fetch.circuit_open")
        return {"error": "Source provider temporarily unavailable (circuit open)"}

    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "format": "json",
        "titles": title,
    }

    try:
        data = run_with_retry(
            "wikipedia_api",
            lambda: _get_json(WIKI_API_URL, params=params, headers=HEADERS, timeout=10),
            RetryPolicy(max_attempts=3, initial_delay_seconds=0.25),
        )
        WIKI_BREAKER.on_success()
        incr("source_fetch.success")
    except Exception as e:
        WIKI_BREAKER.on_failure()
        incr("source_fetch.error")
        log_error(f"API request failed: {e}")
        return {"error": str(e)}

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return {"error": "Page not found"}

    page = next(iter(pages.values()))

    if "missing" in page:
        return {"error": f"Page '{title}' does not exist"}

    extract = page.get("extract", "")

    encoded_title = title.replace(" ", "_")
    page_url = f"https://en.wikipedia.org/wiki/{encoded_title}"

    try:
        from bs4 import BeautifulSoup

        html = run_with_retry(
            "wikipedia_html",
            lambda: _get_text(page_url, headers=HEADERS, timeout=10),
            RetryPolicy(max_attempts=2, initial_delay_seconds=0.25),
        )
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        cleaned_html = soup.prettify()
    except Exception as e:
        cleaned_html = ""
        incr("source_fetch.html_error")
        log_error(f"HTML fetch failed: {e}")

    return {
        "title": title,
        "url": page_url,
        "summary": extract,
        "html": cleaned_html,
    }
