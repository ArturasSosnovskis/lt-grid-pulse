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
        calendar = dates_in_period(start, end)
    except ValueError as exc:
        raise typer.BadParameter(message=str(exc))

    out.parent.mkdir(exist_ok=True, parents=True)

    all_rows = []
    for day in calendar:
        daily_dataset = fetch_elering_api_nps_controller(day)
        filtered_dataset = parse_and_filter(day, daily_dataset)
        all_rows.extend(filtered_dataset)
        print(f"{day}: {len(filtered_dataset)} rows returned")

    all_rows_df = pd.DataFrame(all_rows)

    all_rows_df.to_parquet(out,index=False)
    print(f"Wrote {len(all_rows_df)} rows to: {out}")

@app.callback()
def callback():
    """Placeholder for high-level description."""
    pass
