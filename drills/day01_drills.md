# Day 1 drills: Python basics mapped to SQL

Source: tracker Day 1, "20 Python drills mapped to SQL ideas".
The drill list itself was written for this project; it is not from an external course.

## How to work

- All code goes in `drills/day01_basics.py`, one drill after another.
- Before each drill, a comment: `# Drill N: <name> (SQL: <equivalent>)`.
- Each drill ends with a `print(...)` of its result.
- Run after every drill: `uv run python drills/day01_basics.py`
- Plain Python only: no imports except where a drill says so.
- Stuck more than 15 minutes on one drill: ask for a hint with the drill number.

Reading: Python tutorial
[ch. 3](https://docs.python.org/3.12/tutorial/introduction.html),
[ch. 4](https://docs.python.org/3.12/tutorial/controlflow.html),
[ch. 5](https://docs.python.org/3.12/tutorial/datastructures.html).

## The data

Drills 4 to 20 all use one table: hourly LT day-ahead prices for one day.

- Variable name: `prices`
- 24 rows, one per hour, `hour` 0 to 23
- Columns: `hour` (int), `price` (float, EUR/MWh, make up values between 40 and 200)
- Exactly 2 rows have `price` = `None` (NULL)
- At least 1 price above 150, so drill 18 has something to find

SQL equivalent:

```sql
CREATE TABLE prices (hour INT, price FLOAT);
INSERT INTO prices VALUES (0, 72.4), (1, 68.1), (2, NULL), ... (23, 80.5);
```

## Drills

### Part A: values and text

| # | Drill | SQL equivalent |
|---|---|---|
| 1 | Store the zone code `10YLT-1001A0008Q` in `zone`, a price `85.3` in `price`, an hour `14` in `hour`. Print each value with its `type()`. | column data types |
| 2 | From `zone`, slice out the text `LT`. | `SUBSTRING(zone, 4, 2)` |
| 3 | Using `hour` and `price`, print exactly `Hour 14: 85.30 EUR/MWh`. | `FORMAT` / `CONCAT` |

### Part B: the table

| # | Drill | SQL equivalent |
|---|---|---|
| 4 | Build `prices` as described above: a list of 24 dicts. | `CREATE TABLE` + `INSERT` |
| 5 | Print the number of rows. | `SELECT COUNT(*) FROM prices` |
| 6 | Print every row, one per line, as `hour price`. | `SELECT * FROM prices` |
| 7 | Build a list of just the price values (24 items, NULLs included). | `SELECT price FROM prices` |
| 8 | Build a list of the rows where price > 100. Watch out for `None`. | `SELECT * FROM prices WHERE price > 100` |

### Part C: NULLs and aggregates

| # | Drill | SQL equivalent |
|---|---|---|
| 9 | Count the rows where price is not NULL. | `COUNT(price)` |
| 10 | Min, max and average price, ignoring NULLs. Look up `min()`, `max()`, `sum()`. | `MIN`, `MAX`, `AVG` |
| 11 | Build a new list of rows where NULL prices become `0`. Do not change `prices` itself. | `COALESCE(price, 0)` |
| 12 | Add a `period` value to each row: `"peak"` for hours 8 to 19, otherwise `"off-peak"`. | `CASE WHEN hour BETWEEN 8 AND 19 THEN 'peak' ELSE 'off-peak' END` |

### Part D: sorting, grouping, joining

| # | Drill | SQL equivalent |
|---|---|---|
| 13 | The 3 most expensive hours (skip NULLs). Look up `sorted()` with `key=` and `reverse=`. | `SELECT TOP 3 ... ORDER BY price DESC` |
| 14 | Average price per `period` (peak vs off-peak), ignoring NULLs. | `GROUP BY period` |
| 15 | The distinct `period` values. Look up `set`. | `SELECT DISTINCT period` |
| 16 | Make a dict `temps` of hour -> temperature for only 6 of the hours. Attach `temp` to every row, `None` where missing. Look up `dict.get()`. | `LEFT JOIN temps ON ...` |

### Part E: functions and windows

| # | Drill | SQL equivalent |
|---|---|---|
| 17 | Write a function `avg_price(rows, start_hour, end_hour)` that returns the average non-NULL price for that hour range. Call it twice with different ranges. | scalar UDF |
| 18 | Find the first hour with price > 150. If none exists, print a message instead. | `SELECT TOP 1 ... WHERE price > 150 ORDER BY hour` |
| 19 | For each hour, the price change versus the previous hour (`None` for hour 0 or when either price is NULL). | `price - LAG(price) OVER (ORDER BY hour)` |
| 20 | For each hour, the running total of price (treat NULL as 0). | `SUM(price) OVER (ORDER BY hour)` |

## Done when

- [x] All 20 drills run top to bottom with no errors
- [x] `docs/learning-log.md` has today's 3 lines (what worked, what broke)
- [x] `.env` is in `.gitignore`
- [x] Committed and pushed
- [x] Day 1 set to Done in the tracker
