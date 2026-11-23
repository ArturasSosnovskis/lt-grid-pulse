import time
import json
import httpx
from pydantic import ValidationError
from datetime import date, datetime, timezone
from lt_grid_pulse.ingest.models import EleringRawRow, QuarantinedRow
from lt_grid_pulse.utils.timez import local_day_bounds_utc, intervals_in_local_day

BASE_URL = "https://dashboard.elering.ee/api/nps/price"
LOCATION_CODE = "lt"


def fetch_elering_api_nps_controller(day: date) -> list[dict[str, int | float | None]]:
    """Fetch Elering day-ahead prices for one Vilnius calendar day; return the raw LT rows."""
    start_dt, end_dt = local_day_bounds_utc(day)
    params = {"start": start_dt.isoformat(), "end": end_dt.isoformat()}

    attempts = 0
    max_attempts = 5
    last_error = None
    retry_time = 0.5

    while attempts < max_attempts:
        try:
            r = httpx.get(BASE_URL, params=params, timeout=2)
            r.raise_for_status()
            break

        except (httpx.NetworkError, httpx.TimeoutException) as exc:
            print(f"Attempt {attempts + 1}: network issue ({exc}), retrying...")
            last_error = exc

        except httpx.HTTPStatusError as exc:
            if exc.response.is_client_error and exc.response.status_code != 429:
                raise
            print(
                f"Attempt {attempts + 1}: got {exc.response.status_code}, retrying..."
            )
            last_error = exc

        attempts += 1
        retry_time *= 2
        if attempts == max_attempts:
            raise last_error
        time.sleep(retry_time)

    data = r.json()

    if not data.get("success"):
        raise ValueError(
            f"Success response: {data.get("success")} for Elering API call for {day.isoformat()!r} load"
        )

    return data["data"][LOCATION_CODE]


def parse_and_filter(
    day: date, data: list[dict[str, int | float | None]]
) -> tuple[list[dict[str, datetime | int | float]], list[QuarantinedRow]]:
    """Split one day's raw Elering rows into good rows and quarantined rows.

    Rows outside the day's window are filtered out, not quarantined.
    In-window rows are checked against EleringRawRow. Validated rows become {"ts_utc", "price"},
    bad ones go to quarantine.

    A row with a missing timestamp, or one that is not an int, goes into quarantine
    on the assumption that it belongs to `day`.

    Return (good_rows, quarantined_rows).
    Raise ValueError if the sum of both differs from the expected interval count.
    """

    start_dt, end_dt = local_day_bounds_utc(day)

    converted = []
    quarantined = []
    for row in data:
        if not isinstance(row.get("timestamp"), int):
            quarantined.append(
                QuarantinedRow(
                    day=day,
                    raw=json.dumps(row),
                    reason="timestamp: missing or not an int.",
                )
            )
            continue
        converted_ts = datetime.fromtimestamp(row["timestamp"], tz=timezone.utc)
        if start_dt <= converted_ts < end_dt:
            try:
                checked = EleringRawRow.model_validate(row)
                converted.append({"ts_utc": converted_ts, "price": checked.price})
            except ValidationError as exc:
                quarantined.append(
                    QuarantinedRow(
                        day=day,
                        raw=json.dumps(row),
                        reason="; ".join(
                            f"{err['loc'][0]}: {err['msg']}" for err in exc.errors()
                        ),
                    )
                )

    converted_row_cnt = len(converted)
    quarantined_row_cnt = len(quarantined)
    overall_row_cnt = converted_row_cnt + quarantined_row_cnt
    intervals_in_local_day_cnt = intervals_in_local_day(day)
    if intervals_in_local_day_cnt != overall_row_cnt:
        raise ValueError(
            f"Elering data counts: for {day} expected {intervals_in_local_day_cnt} row counts, got {overall_row_cnt}."
        )
    return converted, quarantined


def daily_min_max_avg_row_cnt(
    data: list[dict[str, datetime | int | float]],
) -> dict[str, int | float | None]:
    """Return min, max, and avg aggregates and valid/invalid price row for Elering batch"""
    data_with_nones_filtered = [row for row in data if row["price"] is not None]
    data_with_nones_filtered_cnt = len(data_with_nones_filtered)

    if len(data_with_nones_filtered) == 0:
        min_price = None
        max_price = None
        avg_price = None

    else:
        min_price = min(row["price"] for row in data_with_nones_filtered)
        max_price = max(row["price"] for row in data_with_nones_filtered)
        avg_price = (
            sum(row["price"] for row in data_with_nones_filtered)
            / data_with_nones_filtered_cnt
        )

    valid_price_row_cnt = data_with_nones_filtered_cnt
    invalid_price_row_cnt = len(data) - data_with_nones_filtered_cnt

    return {
        "min_price": min_price,
        "max_price": max_price,
        "avg_price": avg_price,
        "valid_price_row_cnt": valid_price_row_cnt,
        "invalid_price_row_cnt": invalid_price_row_cnt,
    }


if __name__ == "__main__":
    run_day = date(2026, 11, 17)
    output = fetch_elering_api_nps_controller(run_day)
    good_rows, quarantined_rows = parse_and_filter(run_day, output)
    aggregates = daily_min_max_avg_row_cnt(good_rows)
    aggregates_output = {
        k: round(v, 2) if v is not None else None for k, v in aggregates.items()
    }
    print(aggregates_output)
    print(f"{len(quarantined_rows)} rows quarantined.")
