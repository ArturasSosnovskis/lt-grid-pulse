from datetime import datetime, timezone, time, timedelta
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
    """Return the number of intervals of specified minutes. Default minutes = 15"""
    if minutes <= 0:
        raise ValueError(f"{minutes} must be > 0")
    start, end = local_day_bounds_utc(day)

    if (end - start) % timedelta(minutes=minutes) != timedelta(seconds=0):
        raise ValueError(f"{minutes} minutes doesn't divide {day} evenly")
    return (end - start) // timedelta(minutes=minutes)


def dates_in_period(start_date, end_date):
    """Return every date from start_date to end_date, both included. Raise ValueError if start_date is after end_date."""
    day_count = (end_date - start_date).days + 1
    if day_count <= 0:
        raise ValueError(f"start_date {start_date} comes after end_date {end_date}")

    calendar_start = start_date
    calendar = []

    while day_count > 0:
        calendar.append(calendar_start)
        calendar_start += timedelta(days=1)
        day_count -= 1

    return calendar
