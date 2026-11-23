# LT Grid Pulse

A data pipeline for the Lithuanian power grid: it ingests day-ahead electricity prices, grid load and generation, and weather data, models them with dbt into a star schema, and serves them on a dashboard.

**Status: v0.1.** The Elering price ingest runs from the command line and writes Parquet.
More sources, orchestration and modelling come in later versions.


## Data sources

| Source | Data | Status |
|---|---|---|
| [Elering API](https://dashboard.elering.ee/assets/api-doc.html) | LT day-ahead prices, 15-minute intervals | ✅ v0.1 |

## Setup

Requires [uv](https://docs.astral.sh/uv/) (it installs Python 3.12 for you if needed).

```bash
git clone https://github.com/ArturasSosnovskis/lt-grid-pulse.git
cd lt-grid-pulse
uv sync          # creates .venv and installs all dependencies
```

## Usage

Fetch Elering LT prices for a date range and write them to a Parquet file:

```bash
uv run lt-grid-pulse elering --start 2026-10-01 --end 2026-10-31 --out data/raw/elering_2026-10.parquet
```

| Option | Meaning |
|---|---|
| `--start` | first day to fetch, `YYYY-MM-DD`, Vilnius local calendar day |
| `--end` | last day to fetch, **included** |
| `--out` | Parquet file to write; missing folders are created, an existing file is replaced |

Run `uv run lt-grid-pulse elering --help` for the full option list.


### Output

One row per 15-minute interval:

| Column | Type | Meaning |
|---|---|---|
| `ts_utc` | timestamp, UTC | start of the interval |
| `price` | float | day-ahead price, EUR/MWh |

Rows per local day: 96 normally, 92 on the spring clock change, 100 on the autumn one.
October 2026 gives 2,980 rows.

Every raw row is checked before it's kept: the price must be a number between -500 and 4,000 EUR/MWh,
the timestamp a whole number of seconds. Rows that fail never reach the output file; they go to a
**quarantine file** next to it, `<out name>_quarantine.parquet` (e.g. `elering_2026-10_quarantine.parquet`):

| Column | Type | Meaning |
|---|---|---|
| `day` | date | the requested local day the row came with |
| `raw` | text | the original row as JSON, unchanged |
| `reason` | text | why it failed, e.g. `price: Input should be a valid number` |

The quarantine file is written only when at least one row failed; a clean run removes an old one.
A bad row doesn't stop the run: good + quarantined rows must still add up to the day's full count.

### Behaviour on errors

- Start date after end date: the command stops before any API call, exit code 2.
- A day that is incomplete or not yet published: the run fails and **no file is written**
  (all or nothing). Elering publishes the next day's prices around midday CET.
- Temporary API or network errors are retried with a back-off before giving up.

## Development

```bash
uv run pytest      # run the tests
```

Project layout:

```
src/lt_grid_pulse/
├── cli.py           # command-line entry point (typer)
├── ingest/
│   └── elering.py   # Elering client: fetch, filter, completeness check
└── utils/
    └── timez.py     # UTC / Europe/Vilnius helpers, DST-aware day bounds
tests/               # pytest tests
docs/                # learning log and daily notes
```

Secrets (such as the ENTSO-E token) go in `.env`, which is git-ignored. Downloaded data goes in `data/`,
also git-ignored.