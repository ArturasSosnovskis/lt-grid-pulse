# Day 5 (Fri 20 Nov 2026): Git workflow + CLI

Tracker: "Branches, PRs, commit messages, .gitignore. Package the code; typer CLI (--start --end --out);
write Parquet." Deliverable: **tag v0.1**.

**Why:** today `elering.py` runs only one way: `python elering.py`, with a date written inside the code.
Day 10 (2-year backfill), Day 12 (Docker) and Day 22 (Airflow) all need to call the ingest **from outside**,
with parameters, and get a **file** out. That is a command-line interface (CLI). The file format is
Parquet, which the lake (Day 10), DuckDB (Day 14) and Snowflake (Day 57) all read.
And you stop committing straight to `main`: work goes on a branch, comes back through a pull request (PR),
and the result is marked as release `v0.1`.

```
                 ┌──────────── TODAY ─────────────┐
terminal ──► lt-grid-pulse elering --start --end --out ──► elering.py (Day 3, per day) ──► data/raw/*.parquet
                                                                                              └──► Day 10 backfill, Day 14 DuckDB
Git:  main ──► branch feat/elering-cli ──► commits ──► PR ──► merge ──► tag v0.1
```

SQL equivalent of the whole day: a parameterised procedure that exports to a file.
```sql
EXEC ingest.usp_extract_elering @start = '2026-10-01', @end = '2026-10-31',
                                @out = 'data/raw/elering_2026-10.parquet';
-- Snowflake: COPY INTO @stage/elering_2026-10 FROM (SELECT ...) FILE_FORMAT = (TYPE = PARQUET);
```
ODI comparison: the CLI is the "scenario", the options are its variables, and `--help` is its documentation.

## Input -> output

| | What | Expected |
|---|---|---|
| In | `uv run lt-grid-pulse --help` | lists a command `elering` |
| In | `uv run lt-grid-pulse elering --help` | shows `--start`, `--end`, `--out`, each with a one-line help text |
| Out 1 | `elering --start 2026-11-17 --end 2026-11-17 --out data/raw/t1.parquet` | file with **96 rows** |
| Out 2 | `elering --start 2026-10-25 --end 2026-10-25 --out data/raw/t2.parquet` | **100 rows** (autumn clock change) |
| Out 3 | `elering --start 2026-10-01 --end 2026-10-31 --out data/raw/elering_2026-10.parquet` | **2,980 rows**, same as Day 4 |
| Out 4 | `--start 2026-10-31 --end 2026-10-01` | clear error message, exit code not 0, **no file written** |
| File | Columns when read back | `ts_utc` = datetime **with UTC**, `price` = float; first `ts_utc` of Out 3 = `2026-09-30 21:00:00+00:00` |

**Decision made: `--end` is inclusive** (a person types "1 to 31 October"). Inside the code it still becomes
a half-open `[start, end)` window, as on Day 2.

**Decision made: one call per local day**, reusing your Day 3 functions in a loop over the days.
31 small calls instead of Day 4's one big call, but you keep Day 3's per-day completeness check for free.

## Done when

- [x] Work done on branch `feat/elering-cli`, not on `main`
- [x] `typer` and `pyarrow` added with `uv add`; `pyproject.toml` and `uv.lock` changed and committed
- [x] `src/lt_grid_pulse/cli.py` holds the CLI; `uv run lt-grid-pulse --help` works
- [x] Out 1-4 from the table above all behave as expected
- [x] The output folder is created if missing; running the same command twice gives the same file (overwrite)
- [x] A test for the day-range helper (Step 4); `uv run pytest` all green
- [x] At least 3 commits on the branch, messages in the style from the primer
- [ ] Branch pushed, PR opened, reviewed on GitHub, merged into `main`
- [ ] `main` pulled locally, branch deleted, annotated tag `v0.1` created and pushed
- [x] README: a "Usage" section with the command
- [ ] 2 lines in `docs/learning-log.md`; Day 5 set to Done in the tracker; Week 1 practice tasks received

## Plan (about 4 hours)

| Step | What | Kind | Time |
|---|---|---|---|
| 1 | Read the primer (bottom of this file) | read | 25 min |
| 2 | Create the branch, install the 2 packages, first commit | setup | 15 min |
| 3 | Wire up the entry point so `lt-grid-pulse --help` works | setup | 20 min |
| 4 | Day-range helper + its test | coding | 30 min |
| 5 | The `elering` command: options, fetch per day, build the table | coding | 1 h |
| 6 | Write Parquet, read it back, check Out 1-4 | coding | 30 min |
| 7 | README usage, PR, merge, tag | setup | 30 min |
| 8 | Close the day: log, tracker, Week 1 practice tasks | close | 15 min |

## Step 2: branch and packages (setup: full how)

```bash
git switch main && git pull          # start from an up-to-date main
git switch -c feat/elering-cli       # create the branch and move onto it
git branch                           # the * should be on feat/elering-cli
uv add typer pyarrow                 # both are runtime dependencies (not --dev)
git status                           # expect: pyproject.toml and uv.lock modified
git add pyproject.toml uv.lock
git commit -m "Add typer and pyarrow dependencies"
```
- `pyarrow`: you never import it. pandas uses it behind the scenes to read and write Parquet.
  Without it, pandas raises `ImportError: Unable to find a usable engine`.
- Check: `git log --oneline -3` shows your commit on top; `git log main..feat/elering-cli --oneline` shows only it
  (= "commits on the branch that are not on main").

## Step 3: the entry point (setup: full how)

`pyproject.toml` already has:
```toml
[project.scripts]
lt-grid-pulse = "lt_grid_pulse:main"
```
Read it as: "the terminal command `lt-grid-pulse` runs the object `main` from the package `lt_grid_pulse`".
Today it prints "Hello from lt-grid-pulse!". Try `uv run lt-grid-pulse` now to see it.

What to change:
1. Create `src/lt_grid_pulse/cli.py`. In it you will create a typer app object (the primer's link shows
   the "one app, several commands" layout). Give it a name like `app`.
2. Point the script at it: `lt-grid-pulse = "lt_grid_pulse.cli:app"` (module `lt_grid_pulse.cli`, object `app`).
3. The `main()` in `__init__.py` is no longer used; delete it (leave the file empty, it still marks the package).
4. `uv run lt-grid-pulse --help`. If you get "command not found" or the old hello text, run `uv sync` once:
   it reinstalls your project so the new entry point is registered.

Done when `--help` prints a typer help screen. With no command defined yet typer may complain; that's fine
until Step 5. Commit.

**One-command vs several-command trap:** if your app has only **one** command, typer makes it the whole
program, and `lt-grid-pulse elering --start ...` fails with "Got unexpected extra argument (elering)".
The Day 6+ plan adds more commands (meteo, entsoe), so you want the "several commands" style from the start.
The docs page linked in the primer shows how to force it even with one command.

## Step 4: day-range helper + test (coding: what only)

A small function, in `utils/timez.py`, that takes a start date and an end date (both included) and gives
back every calendar date between them, in order.

| Input | Expected |
|---|---|
| 1 Oct 2026 → 31 Oct 2026 | 31 dates, first 1 Oct, last 31 Oct |
| 17 Nov → 17 Nov | 1 date |
| 28 Mar → 30 Mar 2026 (clock change inside) | 3 dates; dates have no time zone, so DST does not matter here |
| 31 Oct → 1 Oct | `ValueError` with a clear message |

SQL comparison: a calendar/numbers table, `SELECT d FROM dim_date WHERE d BETWEEN @start AND @end`.
Add the 4 rows above as tests in `tests/test_timez.py`. Wrong looks like: 30 dates for October
(end excluded), or an empty result instead of an error for the reversed range. Commit.

## Step 5: the `elering` command (coding: what only)

Split into small pieces; check each before the next.

| # | What | Done when | Wrong looks like |
|---|---|---|---|
| 5a | A command named `elering` with 3 options: `--start`, `--end` (dates) and `--out` (a file path). All 3 required. Each has a help text. For now it only prints what it received | `elering --help` lists the 3 with help; a run prints the 3 values and their **types** | the dates print as strings, or as datetimes with `00:00:00` (you need a `date` for Day 3's functions; see primer 6); missing option gives no error |
| 5b | Reversed range stops the command with a readable message and a non-zero exit code, before any API call | Out 4: one message line, `echo $?` prints a number other than 0 | a long Python traceback (fine for you, not for a user) |
| 5c | For each date from the Step 4 helper: fetch with your Day 3 fetch, then filter with your Day 3 parse; collect all rows of all days into one list | 1-day run: list length 96; 25 Oct: 100 | only the last day's rows survive (the list is rebuilt inside the loop: Day 1/4 "overwritten variable"); rows nested per day (a list of lists) |
| 5d | Print one progress line per day (date + row count) so a long run shows it's alive | 31 lines for October | nothing for 30 seconds, then everything |
| 5e | Turn the list into a DataFrame with exactly the columns `ts_utc`, `price` | 2,980 rows for October; `ts_utc` dtype mentions UTC | an extra index column; `ts_utc` as `object` → the rows held strings, not datetimes |

## Step 6: Parquet out, read back (coding: what only)

| # | What | Done when | Wrong looks like |
|---|---|---|---|
| 6a | Make sure the folder of `--out` exists (create it if not, no error if it does) | `--out data/raw/new_folder/x.parquet` works on a fresh folder | `FileNotFoundError` / `OSError: Cannot save file into a non-existent directory` |
| 6b | Write the DataFrame to `--out` as Parquet, **without** the pandas index | file exists; `git status` does **not** show it (`data/` is ignored) | a column called `__index_level_0__` or `index` when read back |
| 6c | Print a final summary line: rows written + path | `Wrote 2980 rows to data/raw/elering_2026-10.parquet` | — |
| 6d | Read each output file back in a quick check (`uv run python -c "..."` or the Day 4 notebook) | row counts 96 / 100 / 2,980; `ts_utc` still UTC-aware; first value `2026-09-30 21:00:00+00:00` | dtype without UTC → time zone lost on the way |
| 6e | Run Out 3 twice | same row count, file replaced, no error | a "file exists" error, or rows doubled (would mean appending, not overwriting) |

Idempotency (the 6e row) matters on Day 16 and Day 22: Airflow re-runs tasks, and a re-run must give the same
result. SQL comparison: `TRUNCATE + INSERT` (or `MERGE`), never a blind `INSERT` on a re-run.

Commit after 5 and after 6 (at least 3 commits on the branch in total).

## Step 7: README, PR, merge, tag (setup: full how)

1. Add a "Usage" section to `README.md` with the Out 3 command and one sentence on what it writes. Commit.
2. Push the branch (first push of a new branch needs `-u`, which links it to the GitHub copy):
   ```bash
   git push -u origin feat/elering-cli
   ```
3. Open the PR from the terminal (`gh` is already logged in):
   ```bash
   gh pr create --base main --title "Add Elering CLI with Parquet output" --body "What, why, how tested"
   ```
   Fill the body for real: 2-3 lines of what changed, why, and how you tested (the Out 1-4 table).
   It prints the PR URL.
4. Review it like a reviewer would: `gh pr view --web` opens it; click **Files changed** and read your own diff.
   Anything you'd flag in someone else's code? Fix it on the branch, commit, `git push`: the PR updates itself.
5. Merge: `gh pr merge --merge --delete-branch` (keeps your separate commits and deletes the branch on GitHub
   and locally). It switches you to `main`; then `git pull` to get the merge commit.
   Check: `git log --oneline --graph -8` shows the branch joining main.
6. Tag the release on `main`:
   ```bash
   git tag -a v0.1 -m "v0.1: Elering ingest CLI writing Parquet"
   git push origin v0.1        # tags are NOT sent by a normal git push
   git tag                     # v0.1
   ```
   Check on GitHub: the repo's **Tags** list shows v0.1. Optional: `gh release create v0.1 --generate-notes`
   turns it into a Release page.

Common failures: `git push` says "no upstream branch" → you forgot `-u`; `gh pr merge` refuses → uncommitted
changes or the PR is not yet pushed; tag on the wrong commit → you tagged before `git pull`
(fix: `git tag -d v0.1`, pull, tag again; only before pushing it).

## Imports and installs

| Name | Kind | What you need |
|---|---|---|
| `typer` | third-party | `uv add typer` (Step 2), then `import typer` in `cli.py` |
| `pyarrow` | third-party | `uv add pyarrow`; **no import**, pandas uses it for Parquet |
| `pandas` | third-party, already installed | `import pandas as pd` |
| `date`, `datetime`, `timedelta` | standard library | `from datetime import date, datetime, timedelta` |
| `Path` | standard library | `from pathlib import Path` |
| your Day 2 / Day 3 functions | your package | `from lt_grid_pulse.ingest.elering import ...`, `from lt_grid_pulse.utils.timez import ...` |

## Traps

- Committing on `main` by accident: run `git branch` before your first commit. If you have **uncommitted**
  changes on main, `git switch -c feat/elering-cli` simply carries them to the new branch.
- Weak points from this week that fit today: a value computed but not returned or stored (Days 1, 3, 4);
  a variable overwritten inside a loop (Days 1, 3, 4); call vs no call, `()` missing (Days 3, 4);
  type at the edges: the CLI gives you one type, Day 3's functions want another (Days 3, 4).
- Elering publishes tomorrow's prices around midday CET. Asking for a day further ahead fails Day 3's
  completeness check; that's correct behaviour, not a bug.
- A tz-naive `ts_utc` column would be written to Parquet without its zone, and every later reader has to guess.

---

## Primer: what you need to know today

### 1. Branches

A branch is a movable label on a commit. `main` is one; you add your own, commit on it, and `main` stays
untouched until you merge. Cheap to create and delete.

SQL comparison: like working in a `DEV` schema (or a database clone in Snowflake: `CREATE DATABASE dev CLONE prod`)
and promoting to `PROD` only when it's tested, except Git can merge the changes back automatically.

Naming: `feat/...` (new feature), `fix/...` (bug), `docs/...`. One branch = one topic.

[Reference: Git book, branches in a nutshell](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell),
[git switch](https://git-scm.com/docs/git-switch)

### 2. Pull requests

A PR is GitHub's request "merge branch X into main", with the diff, a description and a place for review
comments. Even working alone it's worth it: you read your own change as a whole before it lands, and later
CI (Day 20) runs tests on every PR. SQL comparison: a change request with a code review before deploy to prod.

Merge styles: **merge commit** (keeps every branch commit plus a join point; used today), **squash** (all
branch commits become one), **rebase** (replays commits on top of main, no join point).

[Reference: About pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests),
[gh pr create](https://cli.github.com/manual/gh_pr_create), [merge methods](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges)

### 3. Commit messages

- Subject line: imperative ("Add", "Fix", not "Added"), about 50 characters, no full stop.
  Test: "If applied, this commit will **<subject>**."
- Optional body after a blank line: **why**, not how (the diff shows how).
- One logical change per commit. "Learning log update" is fine; "Day 3 learning log" when the entry
  isn't in it is not (Day 3).

Example: `Add day-range helper with reversed-range check`

[Reference: How to write a Git commit message](https://cbea.ms/git-commit/)

### 4. Tags and versions

A tag is a fixed label on one commit (a branch label moves, a tag doesn't). Annotated tags (`-a`) store who,
when and a message; use them for releases. `v0.1` = "first usable version"; each tracker checkpoint adds one
(v0.2 on Day 15 …). SQL comparison: a named release / deployment label you can roll back to.

[Reference: Git book, tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging)

### 5. .gitignore

Lists file patterns Git never tracks. Yours already ignores `data/`, `.venv`, `.env`, `__pycache__/`.
Check a file: `git check-ignore -v data/raw/t1.parquet` prints the rule that ignores it (nothing printed = not ignored).
Today, after Step 6, run it on your Parquet file. Notebook checkpoints (`.ipynb_checkpoints/`) are worth adding too.

[Reference: gitignore](https://git-scm.com/docs/gitignore)

### 6. A CLI with typer

- **Command**: a verb (`elering`); later others (`meteo`, `entsoe`). **Option**: a named value, `--start 2026-10-01`.
  **Argument**: a positional value with no name. Today: options only.
- typer reads a normal Python function: each **parameter** becomes an option, and its **type hint** tells typer
  how to convert the typed text (text, number, path, date-time …). A docstring becomes the help text.
- Wrong input (bad date, missing required option) gets a clean error and exit code 2 from typer, before your
  code runs. For your own checks (reversed range) typer has a way to raise a "bad parameter" error the same way.
- Small hint for 5a: check which date/time type typer gives you. (Found on the day: typer 0.29 accepts `date`
  directly, so no conversion is needed. Older versions only had `datetime`.)
- Exit codes: `0` = success, anything else = failure. Airflow and Docker (later) decide pass/fail on exactly
  this. SQL comparison: a SQL Agent job step failing on a non-zero return / `RAISERROR` severity ≥ 11.

[Reference: typer first steps](https://typer.tiangolo.com/tutorial/first-steps/),
[options with help](https://typer.tiangolo.com/tutorial/options/help/),
[one or multiple commands](https://typer.tiangolo.com/tutorial/commands/one-or-multiple/),
[datetime type](https://typer.tiangolo.com/tutorial/parameter-types/datetime/),
[path type](https://typer.tiangolo.com/tutorial/parameter-types/path/),
[packaging: entry points](https://packaging.python.org/en/latest/specifications/entry-points/)

### 7. Parquet

A file format that stores a table **by column**, with the types inside the file, compressed.

| | CSV | Parquet |
|---|---|---|
| Types | none, everything is text | stored (`timestamp[UTC]`, `double` …) |
| Time zone | lost unless you write it in the text | kept |
| Read 1 column of 20 | reads the whole file | reads only that column |
| Size | big | ~5-10x smaller |

SQL comparison: Snowflake / Teradata columnar storage; a Snowflake `FILE_FORMAT = (TYPE = PARQUET)` stage file.
pandas writes and reads it with one method call each; the pandas IO page lists them.

[Reference: pandas IO tools, Parquet](https://pandas.pydata.org/docs/user_guide/io.html#parquet),
[What is Parquet](https://parquet.apache.org/docs/overview/)

### 8. Folders from Python

`Path("data/raw/x.parquet").parent` is `data/raw`. A `Path` can create its own folder, including missing
parents, without failing if it already exists (Day 2 primer 5 had one form of this).

[Reference: pathlib Path.mkdir](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.mkdir)
