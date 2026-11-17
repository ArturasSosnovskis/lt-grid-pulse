from datetime import datetime, timezone, date, time, timedelta
from zoneinfo import ZoneInfo

VILNIUS = ZoneInfo("Europe/Vilnius")


def parse_iso(string_datetime):
    """This function firstly checks datetime format and timezone availability and converts to UTC if it is valid."""
    parsed_datetime = datetime.fromisoformat(string_datetime)

    if parsed_datetime.tzinfo is None:
        raise ValueError(f"No timezone offset in {string_datetime!r}")
    return parsed_datetime.astimezone(timezone.utc)

def to_vilnius(dt):
    """Checks if datetime is timezone aware and converts to Vilnius local time"""

    if dt.tzinfo is None:
        raise ValueError(f"Naive datetime (no timezone): {dt!r}")
    return dt.astimezone(VILNIUS)


def to_utc(dt):
    """Checks if datetime is timezone aware and converts to UTC"""

    if dt.tzinfo is None:
        raise ValueError(f"Naive datetime (no timezone): {dt!r}")
    return dt.astimezone(timezone.utc)


def local_day_bounds_utc(day):
    """Take a local date and converts it to a datetime range equivalent (in UTC)"""
    time_placeholder = time()
    start_dt = to_utc(datetime.combine(day, time_placeholder, tzinfo=VILNIUS))
    end_dt = to_utc(
        datetime.combine(day + timedelta(days=1), time_placeholder, tzinfo=VILNIUS)
    )

    return start_dt, end_dt


def intervals_in_local_day(day, minutes=15):
    """Returns the number of intervals of speficied minutes. Default minutes = 15"""
    if minutes <= 0:
        raise ValueError(f"{minutes} must be > 0")
    start, end = local_day_bounds_utc(day)

    if (end - start) % timedelta(minutes=minutes) != timedelta(seconds=0):
        raise ValueError(f"{minutes} minutes doesn't divide {day} evenly")
    return (end - start) // timedelta(minutes=minutes)


if __name__ == "__main__":
    day = date(2026, 3, 29)
    print(intervals_in_local_day(day))
