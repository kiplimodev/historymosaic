# Source Fetcher — Reference

The source fetcher retrieves and cleans Wikipedia article content for a given historical event title.

## Process
1. Query the Wikipedia REST API (`/w/api.php`) for the plain-text article extract
2. Fetch the full HTML page as a structural fallback
3. Strip `<script>` and `<style>` tags from HTML
4. Return a structured dictionary

## Output Schema
```json
{
  "title": "Exact Wikipedia article title",
  "url": "https://en.wikipedia.org/wiki/Article_Title",
  "summary": "Plain text extract from the Wikipedia API (may be thousands of words)",
  "html": "Cleaned HTML of the full Wikipedia page"
}
```

## Error Response
```json
{
  "error": "Human-readable error message"
}
```

## Rules
- Always include a `User-Agent` header identifying the bot (required by Wikipedia's API policy)
- The `summary` field contains the full plain-text extract — it is the primary input to the event-extraction LLM
- The `html` field is a secondary fallback for structured data (infoboxes, dates, etc.)
- Return an error dict on any failure — never raise an unhandled exception
