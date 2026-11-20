# Learning log

## Day 1 (Mon 16 – Tue 17 Nov 2026): Python basics

- **Worked:** Tried mapping Python to SQL logic as a start: list comprehensions = SELECT/WHERE, `defaultdict(list)` = GROUP BY, `dict.get()` = LEFT JOIN, looping while storing the previous value = LAG, `+=` in a loop = running SUM. Created a set of functions (avg/max/first-hour-above per hour range) that return `None` for "no data".
- **Broke:** NULL handling is something to remember. `None > an actual number` crashes, and therefore `is not None` is needed first as a first check.
Functions return `None` when a branch of the flow control in it has no `return`. A `for` loop variable named `prices` overwrote a variable outside the for loop because there's no block scope.

## Day 2 (Tue 17 – Wed 18 Nov 2026): Time module in Python, pytest tests

- **Worked:** Built a time related module `timez.py` with functions to parse ISO strings to UTC, convert from local time to UTC and vice versa, get UTC start and end datetimes for a local timezone date, calculate intervals in minutes for a given day. Wrote pytests, including daylight saving edge cases.
- **Broke:** Problems with timezone conversions and calculating day bounds - firstly, need to find the bound in local time, only then convert to UTC. The test took the longest to work out, especially the part what each test should check and how it should do that.

## Day 3 (Wed 18 – Thu 19 Nov 2026): Elering data ingestion

- **Worked:** Built a module `elering.py` with functions to ingest data from Elering via API call, filter and clean up the received data, with checks for incomplete days, `None` prices and a 200 response that still says `success: false`.
- **Broke:** I still don't quite understand the HTTP part of the code, error handling is still fuzzy in my mind, and edge cases are something I still forget.

## Day 4 (Thu 19 – Fri 20 Nov 2026): Jupyter notebook pandas exercises

- **Worked:** Jupyter notebook setup in the project. Whole month fetch for October 2026 of LT Elering data. 10 SQL -> pandas exercises done, with reconciliation against a DST day with previously created functions.
- **Broke:** Pandas quirks (a lot of them): index specifics, dict with a single row does not become a DataFrame unless index is specified. Took way longer than expected on exercises, rushed through the last ones to save time. I blame pandas syntax, that is very inconsistent. In the age of AI generated code, readability and consistency is key, so I would prioritize investigating easier approaches (like Polars) to use in future projects. Not all on pandas though: some of my old mistakes repeated (calculating results but not storing them, variables overwritten). Jupyter notebook kernel state that needs a full reload introduces errors, and takes time to analyze. Wasted time detouring into an `elering.py` refactoring mid-exercise. Dropped it and reverted, which is a great reminder of prioritization and MVP seeking, rather than code you are happy with. 
