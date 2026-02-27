# Autopost Scheduler — Reference

The scheduler runs the full post pipeline automatically on a cron schedule.

## Posting Schedule (UTC)
| Slot | Time  | Reason                     |
|------|-------|----------------------------|
| AM   | 09:00 | Morning engagement window  |
| PM   | 14:00 | Afternoon peak traffic     |
| EVE  | 19:00 | Evening peak traffic       |

## Pipeline Per Post (autopost.py)
1. Load `events/posted_log.json` to get the list of already-posted filenames
2. Scan `events/` for all `.json` files not in the posted log
3. Select the next unposted event (sorted by filename = chronological order)
4. Validate the event schema
5. Rewrite the event as a tweet using `rewrite_for_x`
6. Post the tweet to X via `post_to_x`
7. Append the filename to `posted_log.json`
8. Log the result

## Posted Log Format
`events/posted_log.json` — a JSON array of posted filenames:
```json
[
  "1963-08-28-march-on-washington.json",
  "1969-07-20-moon-landing.json"
]
```

## Deduplication Rules
- Never post the same event twice
- If all events have been posted, log a warning and skip the cycle (do not repeat)
- Future: optionally reset the log and cycle through events again after a set period

## Error Handling
| Scenario              | Action                                              |
|-----------------------|-----------------------------------------------------|
| X API rate limit      | Back off 15 minutes, then retry once                |
| X API post failure    | Log error, mark event as `failed`, continue         |
| LLM failure           | Log error, skip cycle entirely                      |
| No unposted events    | Log warning, skip cycle                             |
| Invalid event schema  | Attempt LLM repair, skip if repair also fails       |
