# Learning log

## Day 1 (Mon 16 – Tue 17 Nov 2026): Python basics

- **Worked:** Tried mapping Python to SQL logic as a start: list comprehensions = SELECT/WHERE, `defaultdict(list)` = GROUP BY, `dict.get()` = LEFT JOIN, looping while storing the previous value = LAG, `+=` in a loop = running SUM. Created a set of functions (avg/max/first-hour-above per hour range) that return `None` for "no data".
- **Broke:** NULL handling is something to remember. `None > an actual number` crashes, and therefore `is not None` is needed first as a first check.
Functions return `None` when a branch of the flow control in it has no `return`. A `for` loop variable named `prices` overwrote a variable outside the for loop because there's no block scope.

## Day 2 (Tue 17 – Wed 18 Nov 2026): Time module in Python, pytest tests

- **Worked:** Built a time related module `timez.py` with functions to parse ISO strings to UTC, convert from local time to UTC and vice versa, get UTC start and end datetimes for a local timezone date, calculate intervals in minutes for a given day. Wrote pytests, including daylight saving edge cases.
- **Broke:** Problems with timezone conversions and calculating day bounds - firstly, need to find the bound in local time, only then convert to UTC. The test took the longest to work out, especially the part what each test should check and how it should do that.
