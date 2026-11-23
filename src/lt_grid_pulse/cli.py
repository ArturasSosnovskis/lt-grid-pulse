import typer
import pandas as pd
from pathlib import Path
from datetime import date
from typing import Annotated
from lt_grid_pulse.utils.timez import dates_in_period
from lt_grid_pulse.ingest.elering import (
    fetch_elering_api_nps_controller,
    parse_and_filter,
)

app = typer.Typer()


@app.command()
def elering(
    start: Annotated[
        date,
        typer.Option(help="Start date (Vilnius Local Time) of the requested period."),
    ],
    end: Annotated[
        date,
        typer.Option(
            help="End date (inclusive, also Vilnius Local Time) of the requested period."
        ),
    ],
    out: Annotated[Path, typer.Option(help="Path to which the output file is saved.")],
):
    """Fetch Elering LT electricity prices for a date range and store them to a Parquet file."""

    try:
        days = dates_in_period(start, end)
    except ValueError as exc:
        raise typer.BadParameter(message=str(exc))

    out.parent.mkdir(exist_ok=True, parents=True)

    all_good_rows = []
    all_quarantined_rows = []
    for day in days:
        daily_dataset = fetch_elering_api_nps_controller(day)
        good_rows, quarantined_rows = parse_and_filter(day, daily_dataset)
        all_good_rows.extend(good_rows)
        all_quarantined_rows.extend(quarantined_rows)
        print(f"{day}: {len(good_rows)} rows returned, {len(quarantined_rows)} rows quarantined")

    all_good_rows_df = pd.DataFrame(all_good_rows)
    all_good_rows_df.to_parquet(out, index=False)
    print(f"Wrote {len(all_good_rows_df)} rows to: {out}")

    quarantine_out = out.with_stem(f"{out.stem}_quarantine")
    if len(all_quarantined_rows) > 0:
        all_quarantined_rows_df = pd.DataFrame(all_quarantined_rows)
        all_quarantined_rows_df.to_parquet(quarantine_out, index=False)
        print(f"Quarantined {len(all_quarantined_rows_df)} rows to: {quarantine_out}")
    else:
        quarantine_out.unlink(missing_ok=True)  # remove a stale file from an earlier run
        print("No rows quarantined")


@app.callback()
def callback():
    """LT Grid Pulse: ingest Lithuanian grid, price and weather data."""
    pass
