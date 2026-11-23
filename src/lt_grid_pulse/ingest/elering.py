import time
from datetime import date, datetime, timezone
import httpx
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


def parse_and_filter(day: date, data: list[dict[str, int | float | None]]) -> list[dict[str, datetime | int | float | None]]:
    """Filter out of bound rows and parse UNIX timestamp values to utc datetime. Also compares expected and received row counts, raises ValueError, if not equal"""
    start_dt, end_dt = local_day_bounds_utc(day)
    converted = []
    for row in data:
        converted_ts = datetime.fromtimestamp(row["timestamp"], tz=timezone.utc)
        if start_dt <= converted_ts < end_dt:
            converted.append({"ts_utc": converted_ts, "price": row["price"]})
    converted_row_cnt = len(converted)
    intervals_in_local_day_cnt = intervals_in_local_day(day)
    if intervals_in_local_day_cnt != converted_row_cnt:
        raise ValueError(
            f"Elering data counts: for {day} expected {intervals_in_local_day_cnt} row counts, got {converted_row_cnt}."
        )
    return converted


def daily_min_max_avg_row_cnt(data: list[dict[str, datetime | int | float | None]]) -> dict[str, int | float | None]:
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
    output = fetch_elering_api_nps_controller(date(2026, 11, 17))
    filtered_output = parse_and_filter(date(2026, 11, 17), output)
    aggregates = daily_min_max_avg_row_cnt(filtered_output)
    aggregates_output = {k: round(v, 2) if v is not None else None for k, v in aggregates.items()}
    print(aggregates_output)
