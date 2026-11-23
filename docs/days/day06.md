# Day 6 (Mon 23 Nov 2026): Validation with pydantic

Tracker: "Type hints, dataclasses, pydantic models for API records; quarantine bad rows."
Deliverable: **validated Elering client**.

**Why:** today your Elering code trusts whatever the API sends. Three things can go wrong, and none is handled well:

| What the API sends | What happens today |
|---|---|
| `"price": null` | goes straight into the Parquet file as a missing price |
| `"price": "72.4"` (a string) | goes into the file as text; the `price` column type breaks |
| a row with no `"price"` key | `KeyError` crash: the whole 31-day run dies on one row |

Day 15 loads these files into Postgres, Day 32+ builds dbt models on them. A bad value that gets in now
surfaces weeks later in a dashboard. So you put a **contract at the door**: every raw row is checked against a
declared shape; good rows go on, bad rows go to a **quarantine** file with the reason, and the run doesn't die.

```
                         ┌───────────────── TODAY ─────────────────┐
Elering API ──► fetch (Day 3) ──► validate each raw row (pydantic) ──► good ──► window filter ──► data/raw/*.parquet
                                                    └──► bad ──► data/raw/*_quarantine.parquet (row + reason)
```

SQL equivalent: a typed staging table with CHECK constraints, plus an error table for rows that fail them.
```sql
-- ODI: flow control with a CKM sends rows that break constraints to E$_ tables instead of failing the load
-- SSIS: "Redirect row" on a component's error output
-- Snowflake:
COPY INTO raw.elering_price FROM @stage/elering ON_ERROR = CONTINUE;
SELECT * FROM TABLE(VALIDATE(raw.elering_price, JOB_ID => '_last'));   -- the rows that were rejected and why
```

## Input -> output

Raw rows below use `1794866400` = 2026-11-17 00:00 Vilnius = `2026-11-16 22:00:00+00:00`.

| | What | Expected |
|---|---|---|
| In | `{"timestamp": 1794866400, "price": 72.4}` | good row → `ts_utc` 2026-11-16 22:00 UTC, `price` 72.4 |
| In | `{"timestamp": 1794866400, "price": null}` | quarantined, reason mentions `price` |
| Out 1 | `elering --start 2026-10-01 --end 2026-10-31 --out data/raw/elering_2026-10.parquet` | **2,980 rows, identical** to the v0.1 file; summary says 0 quarantined |
| Out 2 | same run | `data/raw/elering_2026-10_quarantine.parquet` exists with **0 rows** but the right columns |
| Out 3 | Out 1 again | same two files, same counts (idempotent) |
| Tests | a fake 96-row day with 1 bad price | 95 good rows, 1 quarantined, **no** error |
| Tests | a fake 95-row day, all good | `ValueError` (incomplete day, as on Day 3) |

**Decisions made:**
- **Strict mode** on the raw model: Elering sends numbers, so a price that arrives as text means the API changed.
  We want to see that, not have it quietly converted. (An integer price like `80` is still fine: becomes `80.0`.)
- **Price sanity bounds: -500 to 4,000 EUR/MWh.** Negative prices are real (windy, sunny days); the bounds are
  roughly the day-ahead market's own floor and cap. It's our choice; write it as a named constant with a comment.
- **Output contract doesn't change:** the good-rows file still has exactly `ts_utc`, `price` (README says so).
- **Completeness check:** good in-window rows + quarantined rows must equal the expected count (96 / 92 / 100).
  A bad row is a row problem (quarantine it); a missing row is a day problem (still a `ValueError`).
  Known simplification: a quarantined row is assumed to belong to the requested day (its timestamp may be the
  broken part). Say so in the docstring.
- **Quarantine file is always written**, even with 0 rows. Otherwise a stale file from an earlier run would stay
  next to a clean new one and mislead the reader.
- **Exit code stays 0** when rows are quarantined; the summary line reports them. (Failing the run on bad data
  comes on Day 26, data quality.)

## Done when

- [ ] Work on branch `feat/elering-validation`; `pydantic` added with `uv add` as a direct dependency
- [ ] Every function in `timez.py` and `elering.py` has type hints on parameters and return value
- [ ] A pydantic model for one raw Elering row; the 9 rows from Step 4 behave as in the table (as tests)
- [ ] A dataclass for one quarantined row
- [ ] The parse step returns good rows **and** quarantined rows; the 2 fake-day tests pass
- [ ] CLI writes both files and prints a quarantine count; Out 1-3 as expected
- [ ] New October file identical to the v0.1 file
- [ ] `uv run pytest` all green; PR opened, reviewed, merged; branch deleted
- [ ] Week 1 practice: at least tasks 3 (exceptions) and 7 (type at the edges) done (they fit today)
- [ ] 2 lines in `docs/learning-log.md`

## Plan (about 4 hours)

| Step | What | Kind | Time |
|---|---|---|---|
| 1 | Read the primer (bottom of this file) | read | 25 min |
| 2 | Branch, `uv add pydantic`, save a copy of the v0.1 output | setup | 15 min |
| 3 | Type hints on existing functions | coding | 35 min |
| 4 | The raw-row model + its 9 tests | coding | 1 h |
| 5 | Quarantine record + the split in the parse step + 2 fake-day tests | coding | 50 min |
| 6 | CLI: write the quarantine file, summary line, regression check | coding | 35 min |
| 7 | PR, review, merge | setup | 20 min |
| 8 | Close the day | close | 10 min |

## Step 2: branch, package, baseline (setup: full how)

```bash
git switch main && git pull
git fetch --prune                     # removes the stale origin/feat/elering-cli label from Day 5
git branch -a                         # origin/feat/elering-cli should be gone
git switch -c feat/elering-validation
uv add pydantic
git status                            # expect: pyproject.toml and uv.lock modified
git add pyproject.toml uv.lock
git commit -m "Add pydantic dependency"
git log --oneline -1                  # Week 1 task 8: check the message
```
- **Why `uv add` if it already works?** `uv run python -c "import pydantic"` already succeeds, because typer
  depends on pydantic. That's a *transitive* dependency: if typer ever drops it, your code breaks. Anything you
  `import` yourself must be listed in your own `pyproject.toml`. See it: `uv tree --depth 1` before and after.
  SQL comparison: relying on a view that happens to expose a column you need, instead of reading the base table.
- If `git branch -a` still shows `origin/feat/elering-cli`, it still exists on GitHub: `git push origin --delete feat/elering-cli`.

Baseline for the regression check in Step 6 (data files are ignored by Git, so copy it by hand):
```bash
cp data/raw/elering_2026-10.parquet data/raw/elering_2026-10_v01.parquet
```

## Step 3: type hints (coding: what only)

Add hints to every function in `utils/timez.py` and `ingest/elering.py`: each parameter and the return value.
Nothing should behave differently.

| Function kind | What to describe |
|---|---|
| takes a `date`, gives back two aware datetimes | both parts of what comes back |
| gives back a list of rows, each row a dict | a list *of* dicts |
| gives back a number of intervals | the number's type |
| aggregates that can be missing (empty day) | "a float **or** None" |

Done when: hovering a function name in VS Code shows the hints; `uv run pytest` still green.
Wrong looks like: `datetime` where Day 2's functions take a `date` (check the callers); a return hint of one
type when the function returns two values; a hint on a dict that says `list`.
Optional editor setting (setup, full how): VS Code → Settings → search "type checking mode" →
Python › Analysis: Type Checking Mode → `basic`. Wrong types now get a squiggle. Look at what it flags in your
code before changing anything. Commit.

## Step 4: the raw-row model (coding: what only)

A pydantic model in a new module `src/lt_grid_pulse/ingest/models.py` that describes **one raw Elering row**,
exactly as the API sends it: a timestamp (whole seconds since 1970) and a price. Strict mode, price inside the
bounds. The conversion to `ts_utc` stays in your Day 3 code; the model only says "this raw row is well formed".

Tests in `tests/test_models.py`. Write down what you expect for each row **before** running (Week 1 habit):

| # | Raw row | Expected |
|---|---|---|
| 1 | `{"timestamp": 1794866400, "price": 72.4}` | valid |
| 2 | `{"timestamp": 1794866400, "price": -12.5}` | valid (negative prices are real) |
| 3 | `{"timestamp": 1794866400, "price": 80}` | valid, price is `80.0` (a float) |
| 4 | `{"timestamp": 1794866400, "price": None}` | error |
| 5 | `{"timestamp": 1794866400, "price": "72.4"}` | error (strict) |
| 6 | `{"timestamp": 1794866400, "price": 99999}` | error (above 4,000) |
| 7 | `{"price": 72.4}` | error (missing timestamp) |
| 8 | `{"timestamp": 1794866400, "price": 72.4, "extra": 1}` | valid, `extra` ignored |
| 9 | `{"timestamp": "1794866400", "price": 72.4}` | error (strict) |

Done when all 9 pass. Rows 4-7 and 9: the test must check that the **right kind** of error is raised, not just
"something went wrong" (pytest has a way to say "this block must raise X"; you used it on Day 5 for the reversed range).
Wrong looks like: row 5 passes (strict mode not on); row 3 fails (you typed price as int); row 6 passes (bounds missing).
Commit.

## Step 5: quarantine record + the split (coding: what only)

**5a. The quarantine record.** A dataclass (not pydantic: it's our own data, already trusted) with:
the day requested, the raw row as **text** (so a broken row of any shape fits in one column), and a short reason.
Wrong looks like: the raw row stored as a dict: Parquet then needs one type per column and a row with
`"price": "abc"` next to one with `72.4` breaks the write.

**5b. The split.** Change `parse_and_filter` (or add a function beside it) so that for one day it:
1. checks every raw row against the Step 4 model;
2. good rows → converted and window-filtered as before; bad rows → a quarantine record with a short reason;
3. runs the completeness check with the rule from "Decisions made";
4. gives back **both** lists.

| Input (day 2026-11-17) | Good rows | Quarantined | Error? |
|---|---|---|---|
| fake day: 96 good rows | 96 | 0 | no |
| fake day: 96 rows, row 10 has price `None` | 95 | 1, reason mentions price | no |
| fake day: 95 good rows | — | — | `ValueError` |

Build the fake days inside the test (96 timestamps, 900 seconds apart, from `1794866400`). No HTTP in these tests.
Wrong looks like: the call site keeps only one of the two returned lists (Week 1 "value created but not kept");
the error catch is so broad it also hides a bug in your own code (catch only the validation error);
the 95+1 case raises because the check counts only good rows.

Then fix the `__main__` block at the bottom of `elering.py`: it calls the old signature. Commit.

## Step 6: CLI (coding: what only)

| # | What | Done when | Wrong looks like |
|---|---|---|---|
| 6a | Collect quarantined rows from all days into one list, like the good rows | October: 0 | only the last day's survive (overwritten list) |
| 6b | Write them to `<out name>_quarantine.parquet` beside `--out`, always, even with 0 rows | file exists, 0 rows, 3 named columns | no file on a clean run; a 0-row file with **no** columns |
| 6c | Summary line: rows written, rows quarantined, both paths | `Wrote 2980 rows to ...; quarantined 0 rows to ...` | — |
| 6d | Regression: read the new October file and the `_v01` copy, check they're identical | identical | different dtypes (e.g. UTC lost) or a different row order |

Hint for 6b: the quarantine path is built from the `--out` path (it has parts for the folder, the name without
extension, and the extension; see primer 6). Hint for 6d: pandas has a one-call "are these two tables exactly equal"
check. SQL equivalent: `(SELECT * FROM a EXCEPT SELECT * FROM b)` and the reverse both return 0 rows.

Update README's output contract with the quarantine file. Commit.

## Step 7: PR, merge (setup: full how)

```bash
uv run pytest
git push -u origin feat/elering-validation
gh pr create --base main --title "Validate Elering rows and quarantine bad ones" --body "What, why, how tested"
gh pr view --web          # Files changed: read your own diff, fix, push
gh pr merge --merge --delete-branch
git pull
git log --oneline --graph -8
```
No tag today (v0.2 is Day 15).

## Imports and installs

| Name | Kind | What you need |
|---|---|---|
| `pydantic` | third-party | `uv add pydantic` (Step 2), then `from pydantic import BaseModel, ValidationError` (+ the strict-mode and field-constraint helpers from the doc pages in primer 3, also from `pydantic`) |
| `dataclass` | standard library | `from dataclasses import dataclass` |
| `json` | standard library | `import json` (turning a dict into text) |
| `date`, `datetime` | standard library | `from datetime import date, datetime` (for hints too) |
| `Path` | standard library | `from pathlib import Path` |

Type hints themselves (`int`, `list[dict]`, `float | None`, `tuple[...]`) need **no import** in Python 3.12.

## Traps

- Type hints are **not checked when the code runs**. `def f(x: int)` happily accepts `"abc"`. Only the editor
  (and pydantic, for its models) looks at them.
- Lax mode (pydantic's default) turns `"72.4"` into `72.4` silently. Today we chose strict.
- Out of the day's window is **not** bad data: those rows are filtered as on Day 3, not quarantined.
- Catching `Exception` instead of the validation error would also swallow your own typos (`NameError` …) and
  put them in quarantine as "bad data". (Week 1 exceptions gap.)
- The full validation error text is several lines long. For the reason column, a short form is nicer: the error
  object can also give you its problems as a list (see the validation errors page).
- Weak points that fit today: returning two values and keeping **both** (Days 1, 3, 4, 5); a list rebuilt inside the
  loop (Days 1, 3, 4, 5); type at the edges: raw int timestamp vs aware datetime (Days 3, 4, 5); edge cases in tests
  first (Days 2, 3, 5): write the 9-row table into tests before the model.

---

## Primer: what you need to know today

### 1. Type hints

A hint says what type a parameter or return value should be. Python itself ignores them when running;
they're for you, the reader, and the editor.
```python
def add_vat(price: float, rate: float = 0.21) -> float:
    return price * (1 + rate)

def first_word(text: str) -> str | None: ...        # str or None
def counts() -> dict[str, int]: ...                 # dict with str keys, int values
def pair() -> tuple[int, int]: ...                  # exactly two ints
```
SQL comparison: Python variables are like Snowflake `VARIANT` columns: anything goes. Hints are like a
column comment saying "this should be a DATE": documented, read by tools, **not** enforced.

[Reference: typing module](https://docs.python.org/3.12/library/typing.html),
[mypy cheat sheet (the clearest one-page summary)](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

### 2. Dataclasses

A class that is just a set of named, typed fields. You get a constructor, a readable print and `==` for free.
```python
from dataclasses import dataclass

@dataclass
class Station:
    name: str
    lat: float

s = Station(name="Vilnius", lat=54.68)
print(s)              # Station(name='Vilnius', lat=54.68)
print(s.lat)          # 54.68   (a field, not s["lat"])
Station(name=5, lat="north")   # no error! dataclasses do NOT check types
```
SQL comparison: a user-defined table type / a row definition. Use it for data **you** create.

[Reference: dataclasses](https://docs.python.org/3.12/library/dataclasses.html)

### 3. pydantic models

Looks like a dataclass, but **checks and converts** the values when the object is created. If anything is
wrong it raises one `ValidationError` that lists every problem (field, what was wrong, the input). Use it for
data **from outside** (APIs, files, users).
```python
from pydantic import BaseModel, ValidationError

class Station(BaseModel):
    name: str
    lat: float

Station(name="Vilnius", lat="54.68")      # lax (default): lat becomes 54.68
try:
    Station(name="Vilnius")               # lat missing
except ValidationError as exc:
    print(exc.error_count())              # 1
```
Three ideas you need today, no code here since they are the exercise:
- **From a dict:** the API gives you dicts; the Models page shows a class method that builds a model from one.
- **Strict mode:** turns off the conversions (`"54.68"` → error). Can be set for the whole model.
  SQL: lax = SQL Server implicit conversion; strict = a typed column with no implicit conversion.
- **Field constraints:** a number field can carry "greater than or equal to / less than or equal to" limits.
  SQL: a `CHECK (price BETWEEN -500 AND 4000)` constraint.
- Unknown extra keys are **ignored** by default (configurable).

[Reference: Models](https://docs.pydantic.dev/latest/concepts/models/),
[Strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/),
[Numeric constraints](https://docs.pydantic.dev/latest/concepts/fields/#numeric-constraints),
[Conversion table (what lax/strict accept)](https://docs.pydantic.dev/latest/concepts/conversion_table/),
[Validation errors](https://docs.pydantic.dev/latest/errors/validation_errors/)

### 4. dict vs dataclass vs pydantic

| | dict | dataclass | pydantic model |
|---|---|---|---|
| Fields declared | no | yes | yes |
| Types checked | no | no | yes, on creation |
| Typo in a field name | silent new key | error | error |
| Use for | quick, loose data | your own records | data crossing the border into your code |

### 5. The quarantine pattern

Don't fail the whole load for one bad row, and don't let it in silently either. Keep it, with the reason, where
someone can look. What a quarantine row needs: which load (the day), the original row **unchanged**, and why it
failed. SQL comparison: ODI's `E$_` error tables, SSIS error output, Snowflake `ON_ERROR = CONTINUE` + `VALIDATE()`.

[Reference: Snowflake COPY INTO ON_ERROR](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table#copy-options-copyoptions)
(only for the comparison)

### 6. Returning two things, and path parts

A function can give back two values at once, and the caller unpacks them into two names. Your own Day 2
`local_day_bounds_utc` already does this: look at how `fetch_elering_api_nps_controller` receives its result.
The trap is keeping only one of them.

A `Path` knows its parts: `Path("data/raw/x.parquet")` has a folder (`data/raw`), a name without extension
(`x`) and an extension (`.parquet`).

[Reference: pathlib, methods and properties](https://docs.python.org/3.12/library/pathlib.html#methods-and-properties)
