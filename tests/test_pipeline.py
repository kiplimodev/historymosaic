# tests/test_pipeline.py
import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


# =============================================================================
# Schema Validation
# =============================================================================
class TestValidateEventSchema:
    def test_valid_event_passes(self):
        from src.validate_event import validate_event_schema
        event = {
            "title": "Moon Landing",
            "date": "1969-07-20",
            "summary": "Apollo 11 was the first crewed mission to land on the Moon.",
            "sources": ["https://en.wikipedia.org/wiki/Apollo_11"],
        }
        assert validate_event_schema(event) is True

    def test_empty_sources_list_is_valid(self):
        from src.validate_event import validate_event_schema
        event = {
            "title": "Moon Landing",
            "date": "1969-07-20",
            "summary": "Apollo 11 landed on the Moon.",
            "sources": [],
        }
        assert validate_event_schema(event) is True

    def test_missing_title_fails(self):
        from src.validate_event import validate_event_schema
        event = {
            "date": "1969-07-20",
            "summary": "Apollo 11 landed on the Moon.",
            "sources": [],
        }
        assert validate_event_schema(event) is False

    def test_missing_date_fails(self):
        from src.validate_event import validate_event_schema
        event = {
            "title": "Moon Landing",
            "summary": "Apollo 11 landed on the Moon.",
            "sources": [],
        }
        assert validate_event_schema(event) is False

    def test_missing_summary_fails(self):
        from src.validate_event import validate_event_schema
        event = {
            "title": "Moon Landing",
            "date": "1969-07-20",
            "sources": [],
        }
        assert validate_event_schema(event) is False

    def test_sources_not_a_list_fails(self):
        from src.validate_event import validate_event_schema
        event = {
            "title": "Moon Landing",
            "date": "1969-07-20",
            "summary": "Apollo 11 landed on the Moon.",
            "sources": "https://en.wikipedia.org/wiki/Apollo_11",
        }
        assert validate_event_schema(event) is False

    def test_sources_containing_non_string_fails(self):
        from src.validate_event import validate_event_schema
        event = {
            "title": "Moon Landing",
            "date": "1969-07-20",
            "summary": "Apollo 11 landed on the Moon.",
            "sources": [123, "https://en.wikipedia.org"],
        }
        assert validate_event_schema(event) is False

    def test_wrong_type_for_title_fails(self):
        from src.validate_event import validate_event_schema
        event = {
            "title": 999,
            "date": "1969-07-20",
            "summary": "Apollo 11 landed on the Moon.",
            "sources": [],
        }
        assert validate_event_schema(event) is False


# =============================================================================
# Date Normalization
# =============================================================================
class TestNormalizeDate:
    def test_iso_date_passes_through(self):
        from src.utils.filename import normalize_date
        assert normalize_date("1969-07-20") == "1969-07-20"

    def test_long_month_format(self):
        from src.utils.filename import normalize_date
        assert normalize_date("July 20, 1969") == "1969-07-20"

    def test_short_month_format(self):
        from src.utils.filename import normalize_date
        assert normalize_date("Aug 28, 1963") == "1963-08-28"

    def test_slash_format(self):
        from src.utils.filename import normalize_date
        assert normalize_date("08/28/1963") == "1963-08-28"

    def test_unparseable_date_returns_original(self):
        from src.utils.filename import normalize_date
        assert normalize_date("unknown-date") == "unknown-date"

    def test_empty_string_returns_empty(self):
        from src.utils.filename import normalize_date
        assert normalize_date("") == ""


# =============================================================================
# Filename Builder
# =============================================================================
class TestBuildEventFilename:
    def test_iso_date_event(self):
        from src.utils.filename import build_event_filename
        event = {"title": "Moon Landing", "date": "1969-07-20"}
        assert build_event_filename(event) == "1969-07-20-moon-landing.json"

    def test_non_iso_date_is_normalized(self):
        from src.utils.filename import build_event_filename
        event = {"title": "Moon Landing", "date": "July 20, 1969"}
        assert build_event_filename(event) == "1969-07-20-moon-landing.json"

    def test_special_chars_in_title_are_slugified(self):
        from src.utils.filename import build_event_filename
        event = {"title": "March on Washington!", "date": "1963-08-28"}
        assert build_event_filename(event) == "1963-08-28-march-on-washington.json"

    def test_missing_fields_produce_safe_fallback(self):
        from src.utils.filename import build_event_filename
        result = build_event_filename({})
        assert result.endswith(".json")
        assert len(result) > 5


# =============================================================================
# Slugify
# =============================================================================
class TestSlugify:
    def test_lowercase(self):
        from src.utils.filename import slugify
        assert slugify("Moon Landing") == "moon-landing"

    def test_strips_special_chars(self):
        from src.utils.filename import slugify
        assert slugify("March on Washington!") == "march-on-washington"

    def test_collapses_multiple_separators(self):
        from src.utils.filename import slugify
        assert slugify("The  Great   War") == "the-great-war"

    def test_strips_leading_trailing_dashes(self):
        from src.utils.filename import slugify
        assert slugify("  event  ") == "event"


# =============================================================================
# Wikipedia Fetcher (mocked)
# =============================================================================
class TestFetchWikipediaPage:
    def _make_api_mock(self, api_data):
        mock = MagicMock()
        mock.raise_for_status = MagicMock()
        mock.json = MagicMock(return_value=api_data)
        return mock

    def _make_html_mock(self, html="<html><body>content</body></html>"):
        mock = MagicMock()
        mock.raise_for_status = MagicMock()
        mock.text = html
        return mock

    def test_successful_fetch_returns_expected_keys(self):
        from src.fetch_source import fetch_wikipedia_page
        api_data = {
            "query": {
                "pages": {
                    "12345": {
                        "title": "Apollo 11",
                        "extract": "Apollo 11 was the first crewed lunar landing.",
                    }
                }
            }
        }
        with patch("src.fetch_source.requests.get") as mock_get:
            mock_get.side_effect = [
                self._make_api_mock(api_data),
                self._make_html_mock(),
            ]
            result = fetch_wikipedia_page("Apollo 11")

        assert result["title"] == "Apollo 11"
        assert "summary" in result
        assert "url" in result
        assert "html" in result
        assert "error" not in result

    def test_missing_page_returns_error(self):
        from src.fetch_source import fetch_wikipedia_page
        api_data = {
            "query": {
                "pages": {"-1": {"missing": "", "title": "Nonexistent Page"}}
            }
        }
        with patch("src.fetch_source.requests.get", return_value=self._make_api_mock(api_data)):
            result = fetch_wikipedia_page("Nonexistent Page")

        assert "error" in result

    def test_network_failure_returns_error(self):
        from src.fetch_source import fetch_wikipedia_page
        with patch("src.fetch_source.requests.get", side_effect=Exception("Timeout")):
            result = fetch_wikipedia_page("Apollo 11")

        assert "error" in result
        assert "Timeout" in result["error"]


# =============================================================================
# Validate or Fix Event (async, mocked LLM)
# =============================================================================
class TestValidateOrFixEvent:
    async def test_valid_event_returns_unchanged(self):
        from src.validate_event import validate_or_fix_event
        event = {
            "title": "Moon Landing",
            "date": "1969-07-20",
            "summary": "Apollo 11 was the first crewed mission to land on the Moon.",
            "sources": ["https://en.wikipedia.org/wiki/Apollo_11"],
        }
        result = await validate_or_fix_event(event)
        assert result == event

    async def test_invalid_event_triggers_llm_repair(self):
        from src.validate_event import validate_or_fix_event
        broken = {"title": "Moon Landing"}
        repaired = {
            "title": "Moon Landing",
            "date": "1969-07-20",
            "summary": "Apollo 11 landed on the Moon.",
            "sources": [],
        }
        with patch("src.validate_event.run_openai", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = json.dumps(repaired)
            result = await validate_or_fix_event(broken)

        assert result["title"] == "Moon Landing"
        assert "date" in result
        assert "summary" in result
        assert "sources" in result

    async def test_llm_returns_invalid_json_falls_back_to_original(self):
        from src.validate_event import validate_or_fix_event
        broken = {"title": "Moon Landing"}
        with patch("src.validate_event.run_openai", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "not valid json {{{"
            result = await validate_or_fix_event(broken)

        # Falls back to the original broken event
        assert result["title"] == "Moon Landing"


# =============================================================================
# Rewrite for X (async, mocked LLM)
# =============================================================================
class TestRewriteForX:
    async def test_returns_string_under_280_chars(self):
        from src.rewrite_x import rewrite_for_x
        event = {
            "title": "Moon Landing",
            "date": "1969-07-20",
            "summary": "Apollo 11 was the first crewed mission to land on the Moon.",
            "sources": ["https://en.wikipedia.org/wiki/Apollo_11"],
        }
        mock_tweet = (
            "July 20, 1969: Humanity touched the Moon. "
            "Neil Armstrong's first steps changed history. "
            "#Apollo11 #MoonLanding"
        )
        with patch("src.rewrite_x.run_openai", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_tweet
            result = await rewrite_for_x(event)

        assert isinstance(result, str)
        assert 0 < len(result) <= 280

    async def test_llm_failure_returns_error_string(self):
        from src.rewrite_x import rewrite_for_x
        event = {
            "title": "Moon Landing",
            "date": "1969-07-20",
            "summary": "Apollo 11 landed on the Moon.",
            "sources": [],
        }
        with patch("src.rewrite_x.run_openai", new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = Exception("LLM unavailable")
            result = await rewrite_for_x(event)

        assert "ERROR" in result
