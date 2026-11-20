# Day 3 (Wed 18 - Thu 19 Nov 2026): HTTP + Elering API

Tracker: "httpx: fetch LT day-ahead prices for one day, parse JSON, min/max/avg. Params, status
codes, timeouts, retries." Deliverable: **`ingest/elering.py` v1**.

*(Written afterwards as a record; the day's brief lived in the chat session.)*

**Why:** the first piece of the pipeline that pulls real data. It fetches one Lithuanian calendar
day of day-ahead prices, using the Day 2 time utilities to turn the local day into a UTC window.

```
date(2026, 11, 17) ─► local_day_bounds_utc ─► GET /api/nps/price?start=..&end=.. ─► data["data"]["lt"]
   ─► parse_and_filter (UTC datetimes, in-window rows, row-count check) ─► daily min/max/avg
```

## Input -> output

| In | Out |
|---|---|
| `date(2026, 11, 17)` | 96 rows `{"ts_utc": datetime, "price": float}` |
| a clock-change day (29 Mar / 25 Oct 2026) | 92 / 100 rows |
| incomplete day | `ValueError` (expected vs received count) |
| 200 response with `success: false` | `ValueError` |
| 5xx, 429, network error, timeout | retried with backoff (0.5 s doubling), up to 5 attempts, then the last error is raised |
| other 4xx | raised at once, no retry |

## Done

- [x] `src/lt_grid_pulse/ingest/elering.py`: `fetch_elering_api_nps_controller`, `parse_and_filter`, `daily_min_max_avg_row_cnt`
- [x] Params, timeout, `raise_for_status`, retry loop with exception types
- [x] DST-aware filtering and row-count check
- [x] Daily min/max/avg with `None` prices counted separately
- [x] Committed (`cea2769`), learning log written

## Imports and installs

| Name | Kind | What you need |
|---|---|---|
| `httpx` | third-party | `uv add httpx`, then `import httpx` |
| `time` | standard library | `import time` (for `time.sleep`) |
| `datetime`, `timezone`, `date` | standard library | `from datetime import date, datetime, timezone` |

## Links

- [Elering API docs (Swagger)](https://dashboard.elering.ee/assets/api-doc.html)
- [httpx quickstart](https://www.python-httpx.org/quickstart/)
- [httpx exceptions](https://www.python-httpx.org/exceptions/)
- [Python errors and exceptions](https://docs.python.org/3.12/tutorial/errors.html)

## Open points (from the learning log)

HTTP basics, error handling (raise vs except, exception hierarchy) and edge cases still feel
fuzzy. They are on the Week 1 practice list.
