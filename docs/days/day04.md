# Day 4 (Thu 19 Nov 2026): pandas as SQL

Tracker: "select/filter/groupby/merge/rolling/rank on a month of LT prices: daily avg, priciest
interval, peak vs off-peak." Deliverable: **notebook with 10 SQL -> pandas exercises**.

**Why:** on Day 3 you handled one day (96 rows) as a list of dicts and looped by hand. That does
not scale to a month, let alone the 2-year backfill on Day 10. pandas gives you an in-memory
table you query with methods instead of loops, like a small SQL engine inside Python. You'll use
it again for validation (Days 6, 26) and analysis (Day 44); DuckDB and dbt take over heavy SQL later.

```
Elering API ──(Day 3: elering.py)──► list of dicts ──(TODAY)──► DataFrame ──► daily stats, ranks, rolling avg
                                                                     └──► later: Parquet (Day 5), DuckDB (Day 14)
```

## Input -> output

Month used: **October 2026** (contains the autumn clock change on 25 Oct).

| | What | Expected |
|---|---|---|
| In | Elering JSON for 1-31 Oct 2026 (local days), rows like `{"timestamp": 1790800000, "price": 87.4}` | one API call |
| Out 1 | DataFrame `ts_utc, ts_local, date_local, price` | **2,980 rows** (30 x 96 + 100) |
| Out 2 | Daily table `date_local, n, min, max, avg` | 31 rows; `n = 96`, except **25 Oct = 100** |
| Out 3 | Notebook, 10 cells, each with its SQL as a comment above the pandas | runs top to bottom |

Rows per local day: normal 96, spring clock change (29 Mar 2026) 92, autumn (25 Oct 2026) 100.

SQL equivalent of the whole day:
```sql
SELECT CAST(ts_local AS date) d, COUNT(*), MIN(price), MAX(price), AVG(price)
FROM #prices GROUP BY CAST(ts_local AS date) ORDER BY d;
-- plus WHERE, ROW_NUMBER() OVER (PARTITION BY ...), JOIN, AVG() OVER (ROWS 6 PRECEDING)
```

## Done when

- [x] pandas and ipykernel installed (ipykernel as dev only)
- [x] `notebooks/day04_pandas_sql.ipynb` created, kernel = `.venv` (check: `sys.executable` points into `.venv`)
- [x] Month fetched with one call; row count 2,980 checked
- [x] 10 exercises done, each with its SQL as a comment
- [x] Exercise 5 reconciles with the Day 3 function for one day
- [x] Restart kernel -> Run All works without errors
- [ ] Committed and pushed
- [ ] 2 lines in `docs/learning-log.md`; Day 4 set to Done in the tracker

## Decision made: one monthly call, not 31 daily calls

~3,000 rows is small, so one request is fine (one call, one retry loop).
Trade-off: Day 3 checked completeness **per day**; a monthly call loses that unless you redo it
over the whole month (see exercise 5, the `HAVING COUNT(*) <> expected` idea).

## Exercise 1 in small steps

| Step | What | Done when | Wrong looks like |
|---|---|---|---|
| B1 | One imports cell at the top: pandas, the date type, the HTTP library, your day-bounds helper | runs, prints nothing | `ModuleNotFoundError` for `lt_grid_pulse` → kernel is not `.venv` |
| B2 | The month window in UTC: start of 1 Oct local to end of 31 Oct local, half-open `[start, end)` | `2026-09-30 21:00:00+00:00` to `2026-10-31 22:00:00+00:00` | both at 21:00 or both at 22:00 → one offset used for the whole month, the 25 Oct change ignored |
| B3 | One request for that window, made directly in the notebook (the Day 3 fetch function is daily-only; use it as a reference, don't call it). No retry loop needed | HTTP 200, `success` is true | params passed as datetimes, not strings ("type at the edges", Day 3); timeout too short for a month-sized response |
| B4 | From the response, take only the LT list of rows | a list of dicts with `timestamp`, `price`; first `timestamp` = `1790802000` | length 2 (top level) or ~4 (country level) → wrong level of the JSON; `KeyError` → key spelling/case |
| B5a | Build the DataFrame straight from the raw LT list | 2,980 or 2,981 rows; `timestamp` int64, `price` float64 | 1 row → wrong JSON level; `price` as `object`/`str` → non-numeric values |
| B5b | New column `ts_utc`: the whole `timestamp` column converted to UTC-aware datetimes, no loop | dtype mentions UTC; first value `2026-09-30 21:00:00+00:00` | dates in 1970 → unit misread; no time zone → naive |
| B6 | Filter to `start_dt <= ts_utc < end_dt` with a boolean mask on the column, no loop | **2,980** rows; last `ts_utc` = `2026-10-31 21:45:00+00:00` | 2,981 → end included (`<=`); "truth value of a Series is ambiguous" → `and` instead of `&` or missing parentheses |
| B7 | Reconcile: compare the pandas result with the Day 3-style loop version | same rows, same `ts_utc` and prices | a mismatch caused by column names/order or the index, not the data → line them up first |

Finding from B5a: the raw response had 2,981 rows; the extra one is exactly `end_dt` (2026-10-31 22:00 UTC, the first
quarter-hour of 1 Nov). Elering's `end` is **inclusive** (like `BETWEEN`), which is why the filter is needed.

## The 10 exercises

Write the SQL as a comment first, then the pandas.

| # | Topic | Task |
|---|---|---|
| 1 | Load | Fetch Oct 2026, build the DataFrame, check row count and column types (steps above) |
| 2 | Derived columns | Add `ts_local`, `date_local`, `hour_local`, `weekday` |
| 3 | WHERE | Count intervals with price < 0 and with price > 200 EUR/MWh |
| 4 | TOP 10 | 10 priciest intervals of the month, shown in local time |
| 5 | GROUP BY | Daily n/min/max/avg. 25 Oct has n = 100. Find any day whose n is not as expected. Reconcile one day with Day 3's function |
| 6 | RANK | Priciest interval per day. Solve it two different ways and compare the results |
| 7 | CASE WHEN | Peak (Mon-Fri 08:00-20:00 local) vs off-peak: avg of each and the spread |
| 8 | Hourly profile | Avg price by local hour (24 rows); cheapest hour |
| 9 | Rolling | 7-day moving average of the daily avg (from exercise 5's table) |
| 10 | JOIN | Small calendar table (`date_local`, `is_weekend`), join it, weekday vs weekend avg |

## Imports and installs

| Name | Kind | What you need |
|---|---|---|
| `pandas` | third-party | `uv add pandas` (done), then `import pandas as pd` |
| `numpy` | third-party, installed together with pandas | `import numpy as np`, only if you need it |
| `ipykernel` | third-party, dev only | `uv add --dev ipykernel` (done); no import, it runs the notebook |
| `sys` | standard library | `import sys` (for the kernel check) |
| your Day 3/Day 2 code | own package | `from lt_grid_pulse.ingest.elering import ...`, `from lt_grid_pulse.utils.timez import ...` |

## Notebook kernel in one table

| SSMS | Notebook |
|---|---|
| Query window | `.ipynb` file |
| Run highlighted block (F5) | Run cell (Shift+Enter) |
| Connection/session | **Kernel** (a background Python process) |
| `#temp` table survives between runs | Variables (`df`) survive between cells |
| Choosing the server | **Select Kernel** -> `.venv` |
| Reconnect: temp tables gone | **Restart kernel**: all variables gone |

`ipykernel` must be installed **in** `.venv` so VS Code can use that Python (with pandas and your
package) as the kernel. VS Code also needs the Jupyter extension.
Notebooks live in `notebooks/` at the repo root, not inside `src/` (that is the installable package).

## Traps

- **JSON -> rows:** iterating a dict gives keys only (Day 3). Find which level of the response holds the list.
- **Local vs UTC day:** group by the **local** date, not the UTC date (Day 2 lesson), or every day boundary is off by 2-3 hours.
- **Types at the edges:** keep timestamps as datetimes inside the DataFrame, not strings.
- **After grouping, the group column is no longer a normal column** (see primer #2). Expect it when you join or filter on it later.
- **Filters:** combine conditions with `&` / `|`, each in its own parentheses. Python's `and` / `or` raise an error on columns.
- **pandas 3.x:** text columns show dtype `str` (older guides say `object`). Copy-on-write is always on, so chained assignment (`df[mask]["x"] = 1`) silently does nothing. Assign in one step instead. [What's new in 3.0](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
- **Out-of-order cells:** before committing, Restart -> Run All.

---

## Primer: what you need to know today

Main lookup page: [pandas: Comparison with SQL](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html).
Code examples only for the basics; the concepts the exercises test are explained, not shown.

### 1. DataFrame and Series (code)
DataFrame = table, Series = one column. A list of dicts becomes a table directly, no loop.

```python
import pandas as pd
df = pd.DataFrame([
    {"city": "Vilnius", "t": 3},
    {"city": "Kaunas",  "t": 5},
])
df.dtypes     # column types
len(df)       # row count
df.head()     # first rows, like SELECT TOP 5
```
[10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)

### 2. The index is not a primary key (code)
Every DataFrame has row labels, the index (`0, 1, 2…` by default). It's not a key: it can repeat
and enforces nothing. After grouping, the group column **moves into the index**, so it disappears
from the normal columns. Expect that, and find how to turn it back into a column.

```python
df.index      # RangeIndex(start=0, stop=2, step=1)
```
[Indexing basics](https://pandas.pydata.org/docs/user_guide/indexing.html)

### 3. SELECT / WHERE (code)
```python
df[["city"]]                                     # SELECT city
df[df["t"] > 3]                                  # WHERE t > 3
df[(df["t"] > 3) & (df["city"] == "Vilnius")]    # AND: & with parentheses
df["t2"] = df["t"] * 2                           # SELECT ..., t * 2 AS t2
```
The part inside `df[...]` is a True/False column (a "boolean mask"); rows where it's True are kept.

### 4. Time (exercise 2): explained, not shown
- Elering timestamps are Unix seconds (an integer). pandas has its own datetime column type, with time zones.
- SQL comparison: Unix int -> `DATETIMEOFFSET` in UTC, then `AT TIME ZONE` to Vilnius local, then `DATEPART`/`CAST(... AS date)` for parts.
- A datetime column has a special accessor that gives date parts (hour, weekday, date) for the whole column at once.
- [Time series guide](https://pandas.pydata.org/docs/user_guide/timeseries.html), especially [time zone handling](https://pandas.pydata.org/docs/user_guide/timeseries.html#time-zone-handling)

### 5. GROUP BY (exercises 5, 8): explained
- Same idea as SQL: split rows into groups, apply aggregates, one row per group.
- Several aggregates at once (`COUNT`, `MIN`, `MAX`, `AVG`) is one call in pandas, not one per aggregate.
- Remember primer #2: the group key ends up in the index.
- [Group by guide](https://pandas.pydata.org/docs/user_guide/groupby.html)

### 6. ORDER BY / TOP (exercise 4): explained
- Sorting and "first N rows" are separate steps, like `ORDER BY` + `TOP`; there's also a shortcut that does both.
- [Comparison with SQL: TOP n rows](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#top-n-rows-with-offset)

### 7. ROW_NUMBER / RANK (exercise 6): explained
- SQL: `ROW_NUMBER() OVER (PARTITION BY d ORDER BY price DESC)`. pandas can rank within groups too.
- Ties: pandas lets you choose how ties are numbered, matching ROW_NUMBER, RANK or DENSE_RANK.
- Another route: ask each group for the **label of its max row**, then fetch those rows.
- [Comparison with SQL: top n rows per group](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#top-n-rows-per-group)

### 8. CASE WHEN (exercise 7): explained
- Goal: a new column whose value depends on a condition (`'peak'` / `'off-peak'`).
- Build the condition as a boolean mask (primer #3), then choose a value per row from it.
- [Comparison with SQL: WHERE](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#where) (for the masks)

### 9. JOIN (exercise 10): explained
- One function covers INNER / LEFT / RIGHT / FULL joins; you name the key column(s) and the join type.
- Same pitfalls as SQL: duplicate keys multiply rows, and key types must match (a date vs a datetime won't match).
- [Merge guide](https://pandas.pydata.org/docs/user_guide/merging.html)

### 10. Window frames (exercise 9): explained
- SQL: `AVG(x) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`.
- pandas has a "rolling window" for exactly this. Rows must be in the right order first.
- The first rows have fewer than 7 values behind them: pandas gives NaN there unless you allow smaller windows.
- [Windowing operations](https://pandas.pydata.org/docs/user_guide/window.html)

### Setup docs
[uv + Jupyter in VS Code](https://docs.astral.sh/uv/guides/integration/jupyter/#using-jupyter-from-vs-code),
[VS Code Jupyter notebooks](https://code.visualstudio.com/docs/datascience/jupyter-notebooks#_setting-up-your-environment)
