# Week 1 practice tasks (set Sun 22 Nov 2026)

Built from the Week 1 weak points (Days 1–5). Small tasks, about 10–15 minutes each.
Do them in `drills/week01_practice.py` alongside Day 6, in plain Python and pandas, not the project code.
**Write the expected output as a comment before you run each one.**

## Checklist

- [ ] 1. A value created but not kept
- [ ] 2. Overwritten variables, `append` vs `extend`
- [ ] 3. Exceptions end to end
- [ ] 4. Reading a signature
- [ ] 5. Rows vs columns
- [ ] 6. Edge cases first
- [ ] 7. Type at the edges
- [ ] 8. Git habit (next 5 commits)

## 1. A value created but not kept (Days 1, 3, 4, 5)

Write `cheapest_hour(prices)` for a list like `[{"hour": 0, "price": 72.4}, ...]` that returns the cheapest row.
Then write it again with three deliberate bugs, one at a time:
- no `return`;
- the result not stored at the call site;
- an exception built without `raise`.

Predict what each bug prints before you run it.
SQL comparison: a procedure that forgets `SELECT` or `RETURN`.

## 2. Overwritten variables (Days 1, 3, 4, 5)

Write a loop over 3 days that collects their rows into one list, and get it wrong in two ways on purpose:
- create the list *inside* the loop;
- give the loop variable the same name as the list.

Predict the final length for each version (expected right answer: 3 × 4 = 12, with 4 rows per day), then fix it.
Also do it once with `append` and once with `extend`, and explain the difference in one comment.

## 3. Exceptions end to end (Days 3, 5; the biggest gap in your log)

Write `safe_divide(a, b)` that raises `ValueError` for `b == 0`. Call it in three ways:
- (a) with no `try`: read the traceback and find your own line;
- (b) catch it and print a friendly message;
- (c) catch it and raise a different error that includes the original message.

For each one, write down the exit code you expect from `python drills/week01_practice.py; echo $?`, then check it.

## 4. Reading a signature (Day 5)

Without searching for an example, open the docs for
[`str.split`](https://docs.python.org/3.12/library/stdtypes.html#str.split) and
[`round`](https://docs.python.org/3.12/library/functions.html#round).
From the signature alone, write down what these return, then run them:
- `"a,b,,c".split(",")`
- `"a,b,,c".split(",", 1)`
- `round(2.675, 2)`

One of the three will surprise you; write a one-line comment on why.

## 5. Rows vs columns (Days 4, 5)

Build a 3-row DataFrame with columns `ts`, `price` and `zone`. In SQL terms, get each of these:
- one column;
- one row by position;
- one cell;
- all column names;
- all column data types.

Write the matching SQL as a comment next to each.

## 6. Edge cases first (Days 2, 3, 5)

For a function `hours_between(start_date, end_date)`, list at least 5 test inputs **before** writing any code:
a normal case, the boundaries, a reversed range, a range containing a DST change, and the same date twice.
Then implement it and make the tests pass.

## 7. Type at the edges (Days 3, 4, 5)

Parse the strings `"2026-10-25"` and `"2026-10-25T00:00:00+03:00"` into the right Python types, and convert
back to strings only when you print. Then answer in a comment: in the Day 5 CLI, which type did the user type,
which type did typer give you, and which type did the Day 3 functions want?

## 8. Git habit (Days 3, 5)

For your next 5 commits, run `git log --oneline -1` right after each one and fix any typo with `--amend`
before pushing. Note how many needed fixing: ___ / 5
