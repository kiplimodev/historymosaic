import requests
from bs4 import BeautifulSoup
from src.utils.log import log_info, log_error

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": "HistoryMosaicBot/1.0 (https://github.com/kiplimodev/historymosaic)"
}

def fetch_wikipedia_page(title: str) -> dict:
    log_info(f"Fetching Wikipedia page for: {title}")

    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "format": "json",
        "titles": title
    }

    try:
        response = requests.get(WIKI_API_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        log_error(f"API request failed: {e}")
        return {"error": str(e)}

    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return {"error": "Page not found"}

    page = next(iter(pages.values()))

    if "missing" in page:
        return {"error": f"Page '{title}' does not exist"}

    extract = page.get("extract", "")

    # Build URL manually
    encoded_title = title.replace(" ", "_")
    page_url = f"https://en.wikipedia.org/wiki/{encoded_title}"

    # Fetch HTML fallback
    try:
        html_response = requests.get(page_url, headers=HEADERS, timeout=10)
        html_response.raise_for_status()
        soup = BeautifulSoup(html_response.text, "html.parser")

        # Cleanup
        for tag in soup(["script", "style"]):
            tag.decompose()

        cleaned_html = soup.prettify()

    except Exception as e:
        cleaned_html = ""
        log_error(f"HTML fetch failed: {e}")

    return {
        "title": title,
        "url": page_url,
        "summary": extract,
        "html": cleaned_html,
    }
