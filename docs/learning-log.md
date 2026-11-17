# Learning log

## Day 1 (Mon 16 – Tue 17 Nov 2026): Python basics

- **Worked:** Tried mapping Python to SQL logic as a start: list comprehensions = SELECT/WHERE, `defaultdict(list)` = GROUP BY, `dict.get()` = LEFT JOIN, looping while storing the previous value = LAG, `+=` in a loop = running SUM. Created a set of functions (avg/max/first-hour-above per hour range) that return `None` for "no data".
- **Broke:** NULL handling is something to remember. `None > an actual number` crashes, and therefore `is not None` is needed first as a first check.
Functions return `None` when a branch of the flow control in it has no `return`. A `for` loop variable named `prices` overwrote a variable outside the for loop because there's no block scope.
