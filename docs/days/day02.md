# Day 2 (Tue 17 Nov 2026): Functions, modules, time zones

Tracker: "Functions, modules, exceptions, file I/O. utils/timez.py: ISO parsing,
UTC <-> Europe/Vilnius, DST days. First pytest tests." Deliverable: **tested time utilities**.

**Why:** on Day 3 you ask Elering for "LT prices for 17 Nov". The API works in UTC, but
"17 Nov" is a Lithuanian calendar day, and twice a year that day is 23 or 25 hours long.
Today you build and test the functions that handle this, once, for every later ingest.

## Done when

- [x] `src/lt_grid_pulse/utils/__init__.py` exists (empty)
- [x] `src/lt_grid_pulse/utils/timez.py` has the 5 functions below, each with a one-line docstring
- [x] `tests/test_timez.py`: `uv run pytest` passes with 10+ tests, including both 2026 DST days
- [x] Bad input raises a clear `ValueError`, and a test checks it
- [x] `drills/day02_io.py`: JSON write/read + missing-file handling
- [x] `data/` added to `.gitignore`
- [x] Committed and pushed (include yesterday's `CLAUDE.md` and `learning-log.md` changes)
- [ ] 2 lines in `docs/learning-log.md`; Day 2 set to Done in the tracker

## Plan (about 4 hours)

| Step | What | Time |
|---|---|---|
| 1 | Read the primer at the bottom of this file, trying examples in `uv run python` | 30 min |
| 2 | Create the `utils/` package folder and empty files | 15 min |
| 3 | Write the 5 functions | 1.5 h |
| 4 | Install pytest, write the tests, make them pass | 1 h |
| 5 | File I/O exercise | 20 min |
| 6 | Close the day: commit, log, tracker | 15 min |

## Step 3: the functions (`src/lt_grid_pulse/utils/timez.py`)

| # | Function | Does | Expected |
|---|---|---|---|
| 1 | `parse_iso(text)` | ISO string -> aware datetime in UTC. Raise `ValueError` if the string has no offset (naive). | `"2026-11-17T10:00:00+02:00"` -> `2026-11-17 08:00 UTC` |
| 2 | `to_vilnius(dt)` | aware datetime -> Vilnius local time | `2026-11-17 08:00 UTC` -> `10:00+02:00`; `2026-07-01 12:00 UTC` -> `15:00+03:00` |
| 3 | `to_utc(dt)` | aware datetime -> UTC | reverse of #2 |
| 4 | `local_day_bounds_utc(day)` | a Vilnius calendar `date` -> `(start_utc, end_utc)`, half-open `[start, end)` | see test table |
| 5 | `intervals_in_local_day(day, minutes=15)` | number of periods of that length in that local day | normal day 96, 29 Mar 2026 92, 25 Oct 2026 100 |

Functions 2 and 3 should also refuse naive input (raise `ValueError`), so a naive datetime can
never slip through silently.

## Step 4: tests (`tests/test_timez.py`)

Install once: `uv add --dev pytest`. Run: `uv run pytest`.
Afterwards, look at what changed in `pyproject.toml` and `uv.lock`.

| Test | Input | Expected |
|---|---|---|
| parse with offset | `"2026-11-17T10:00:00+02:00"` | `2026-11-17 08:00+00:00` |
| parse with Z | `"2026-11-17T08:00:00Z"` | `2026-11-17 08:00+00:00` |
| parse naive raises | `"2026-11-17T10:00:00"` | `ValueError` |
| to Vilnius, winter | `2026-11-17 08:00 UTC` | `10:00`, offset +02:00 |
| to Vilnius, summer | `2026-07-01 12:00 UTC` | `15:00`, offset +03:00 |
| round trip | any aware UTC time -> Vilnius -> UTC | equals the original |
| bounds, normal day | `date(2026, 11, 17)` | `2026-11-16 22:00Z` to `2026-11-17 22:00Z` |
| bounds, summer day | `date(2026, 7, 1)` | `2026-06-30 21:00Z` to `2026-07-01 21:00Z` |
| bounds, spring DST | `date(2026, 3, 29)` | `2026-03-28 22:00Z` to `2026-03-29 21:00Z` |
| bounds, autumn DST | `date(2026, 10, 25)` | `2026-10-24 21:00Z` to `2026-10-25 22:00Z` |
| intervals | normal / 29 Mar / 25 Oct 2026 | 96 / 92 / 100 |
| intervals, hourly | 29 Mar 2026, `minutes=60` | 23 |

## Step 5: file I/O (`drills/day02_io.py`)

1. Write 3 rows of your Day 1 `prices` to `data/sample.json`.
2. Read the file back and print the rows.
3. Try to read `data/missing.json`, catch `FileNotFoundError`, and print a friendly message.
4. Add `data/` to `.gitignore` (raw data never goes in Git).

## Imports and installs

| Name | Kind | What you need |
|---|---|---|
| `datetime`, `timezone`, `timedelta`, `date` | standard library | `from datetime import datetime, timezone, timedelta, date` |
| `ZoneInfo` | standard library | `from zoneinfo import ZoneInfo` |
| `json` | standard library | `import json` |
| `Path` | standard library | `from pathlib import Path` |
| `pytest` | third-party | `uv add --dev pytest` (once), then `import pytest` in test files |

## Traps

- Comparing naive with aware datetimes crashes: `can't compare offset-naive and offset-aware datetimes`.
- Subtracting two times in the **same zone** ignores DST: local midnight 30 Mar minus local
  midnight 29 Mar says `1 day`, though only 23 real hours passed. Convert to UTC first, then subtract.
- `datetime.utcnow()` returns a **naive** datetime. Use `datetime.now(timezone.utc)`.
- Never hard-code `+2` for Lithuania: it is +2 in winter and +3 in summer.

---

## Primer: what you need to know today

### 1. Functions: defaults, keywords, docstrings

```python
def count_intervals(hours, minutes=15):                    # minutes has a default
    """Return how many periods fit in the given hours."""  # docstring
    return hours * 60 // minutes                           # // = whole-number division

count_intervals(24)               # 96, uses the default
count_intervals(24, minutes=60)   # 24, keyword argument makes the 60 clear
```
[Reference](https://docs.python.org/3.12/tutorial/controlflow.html#more-on-defining-functions)

### 2. Modules and packages

- A **module** is a `.py` file. Its functions can be imported elsewhere.
- A **package** is a folder of modules containing an `__init__.py` (can be empty).
- `src/lt_grid_pulse/utils/timez.py` is imported as
  `from lt_grid_pulse.utils.timez import parse_iso` (folders become dots; no `src`, no `.py`).
  Works anywhere in the repo when you run with `uv run`.
- SQL comparison: package ≈ database, module ≈ schema, function ≈ object (`db.schema.object`).

[Reference](https://docs.python.org/3.12/tutorial/modules.html#packages)

### 3. Exceptions

```python
def check_price(p):
    if p is None:
        raise ValueError("price is missing")   # THROW
    return p

try:                                           # BEGIN TRY
    check_price(None)
except ValueError as e:                        # BEGIN CATCH
    print("error:", e)                         # error: price is missing
```
`raise` when your function gets input it can't handle. A clear error beats a wrong answer.
`ValueError` = right kind of thing, bad value.

[Reference](https://docs.python.org/3.12/tutorial/errors.html#raising-exceptions)

### 4. Dates and times: aware vs naive

| | Python | SQL Server |
|---|---|---|
| Naive (no time zone) | `datetime(2026, 11, 17, 10, 0)` | `DATETIME` |
| Aware (knows its offset) | `datetime(2026, 11, 17, 10, 0, tzinfo=timezone.utc)` | `DATETIMEOFFSET` |

```python
vilnius = ZoneInfo("Europe/Vilnius")

a = datetime.fromisoformat("2026-11-17T10:00:00+02:00")   # aware
n = datetime.fromisoformat("2026-11-17T10:00:00")         # naive
a.tzinfo   # UTC+02:00
n.tzinfo   # None  <- how to detect naive

a.astimezone(timezone.utc)                                            # 08:00+00:00 (= AT TIME ZONE)
datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc).astimezone(vilnius)  # 15:00+03:00 (summer)

date(2026, 11, 17) + timedelta(days=1)   # 2026-11-18
```
- Lithuania: UTC+2 in winter, UTC+3 in summer. `ZoneInfo` knows the switch dates.
- DST 2026: clocks forward on 29 Mar (23-hour day), back on 25 Oct (25-hour day).
- Half-open `[start, end)`: start included, end excluded, like `WHERE ts >= @start AND ts < @end`.
  Consecutive days never overlap.

[Reference: aware/naive](https://docs.python.org/3.12/library/datetime.html#aware-and-naive-objects),
[zoneinfo](https://docs.python.org/3.12/library/zoneinfo.html)

### 5. Files and JSON

```python
path = Path("data/sample.json")
path.parent.mkdir(exist_ok=True)           # create data/ if missing

with open(path, "w") as f:                 # "w" = write; "with" closes the file for you
    json.dump([{"hour": 0, "price": 72.4}], f)

with open(path) as f:                      # default mode = read
    rows = json.load(f)                    # back to a list of dicts
```
A missing file raises `FileNotFoundError`.

[Reference](https://docs.python.org/3.12/tutorial/inputoutput.html#reading-and-writing-files)

### 6. pytest

- Test files are `test_*.py`, test functions are `test_*`. pytest finds them automatically.
- `assert` checks that something is true; if not, the test fails and shows the values.

```python
# tests/test_example.py
import pytest

def test_addition():
    assert 2 + 2 == 4

def test_bad_price_raises():
    with pytest.raises(ValueError):   # passes only if a ValueError happens inside
        check_price(None)
```
Run with `uv run pytest`: `.` = passed, `F` = failed.
SQL comparison: like tSQLt or dbt tests, checking your logic on every run.

[Reference](https://docs.pytest.org/en/stable/getting-started.html)
