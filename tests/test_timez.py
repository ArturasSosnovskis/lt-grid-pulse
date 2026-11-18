from lt_grid_pulse.utils.timez import (
    parse_iso,
    to_vilnius,
    to_utc,
    local_day_bounds_utc,
    intervals_in_local_day,
    VILNIUS,
)
from datetime import datetime, timezone, timedelta, date
import pytest


@pytest.mark.parametrize(
    "text, expected",
    [
        (
            "2010-10-10T10:10:10+10:00",
            datetime(2010, 10, 10, 0, 10, 10, tzinfo=timezone.utc),
        ),
        ("2026-11-17T08:00:00Z", datetime(2026, 11, 17, 8, 0, tzinfo=timezone.utc)),
    ],
)
def test_parse_iso_returns_utc(text, expected):
    result = parse_iso(text)
    assert result == expected
    assert result.utcoffset() == timedelta(0)


@pytest.mark.parametrize("text", ["2026-11-17T08:00:00", "2022-11-13T12:36:52"])
def test_parse_iso_rejects_naive_text(text):
    with pytest.raises(ValueError, match="No timezone offset"):
        parse_iso(text)


@pytest.mark.parametrize("text", ["BANNNNAAANA", "", "2026-13-17T08:00:00Z"])
def test_parse_iso_rejects_invalid_text(text):
    with pytest.raises(ValueError):
        parse_iso(text)


@pytest.mark.parametrize(
    "dt, expected_hour, expected_offset",
    [
        (datetime(2026, 11, 17, 8, 0, tzinfo=timezone.utc), 10, timedelta(hours=2)),
        (datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc), 15, timedelta(hours=3)),
    ],
)
def test_to_vilnius_convert_to_local(dt, expected_hour, expected_offset):
    result = to_vilnius(dt)
    assert result.hour == expected_hour
    assert result.utcoffset() == expected_offset


@pytest.mark.parametrize(
    "dt",
    [
        datetime(2026, 11, 17, 8, 0),
        datetime(2026, 7, 1, 12, 0, 0),
    ],
)
def test_to_vilnius_rejects_naive_dt(dt):
    with pytest.raises(ValueError, match="Naive datetime"):
        to_vilnius(dt)


@pytest.mark.parametrize(
    "dt",
    [
        datetime(2026, 11, 17, 8, 0),
        datetime(2026, 7, 1, 12, 0, 0),
    ],
)
def test_to_utc_rejects_naive_dt(dt):
    with pytest.raises(ValueError, match="Naive datetime"):
        to_utc(dt)


@pytest.mark.parametrize(
    "dt, expected_hour",
    [
        (datetime(2026, 11, 17, 8, 0, tzinfo=timezone(timedelta(hours=-2))), 10),
        (datetime(2026, 7, 1, 12, 0, tzinfo=timezone(timedelta(hours=5))), 7),
        (datetime(2026, 7, 1, 15, 0, tzinfo=VILNIUS), 12),
    ],
)
def test_to_utc_conversion(dt, expected_hour):
    result = to_utc(dt)
    assert result.hour == expected_hour
    assert result.utcoffset() == timedelta(0)


@pytest.mark.parametrize(
    "day, expected_start_dt, expected_end_dt",
    [
        (
            date(2026, 11, 7),
            datetime(2026, 11, 6, 22, 0, tzinfo=timezone.utc),
            datetime(2026, 11, 7, 22, 0, tzinfo=timezone.utc),
        ),
        (
            date(2026, 7, 1),
            datetime(2026, 6, 30, 21, 0, tzinfo=timezone.utc),
            datetime(2026, 7, 1, 21, 0, tzinfo=timezone.utc),
        ),
        (
            date(2026, 3, 29),
            datetime(2026, 3, 28, 22, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 29, 21, 0, tzinfo=timezone.utc),
        ),
        (
            date(2026, 10, 25),
            datetime(2026, 10, 24, 21, 0, tzinfo=timezone.utc),
            datetime(2026, 10, 25, 22, 0, tzinfo=timezone.utc),
        ),
    ],
    ids=["normal", "summer", "spring-dst", "autumn-dst"],
)
def test_local_day_bounds_utc_period_validity(day, expected_start_dt, expected_end_dt):
    start_dt, end_dt = local_day_bounds_utc(day)
    assert (start_dt, end_dt) == (expected_start_dt, expected_end_dt)
    assert start_dt.utcoffset() == timedelta(0)
    assert end_dt.utcoffset() == timedelta(0)


@pytest.mark.parametrize(
    "day, expected_intervals, minutes",
    [
        (date(2026, 11, 17), 96, 15),
        (date(2026, 3, 29), 92, 15),
        (date(2026, 10, 25), 100, 15),
        (date(2026, 3, 29), 23, 60),
    ],
    ids=["normal", "spring-dst", "autumn-dst", "spring-dst-hourly"],
)
def test_intervals_in_local_day_validity(day, expected_intervals, minutes):
    assert intervals_in_local_day(day, minutes=minutes) == expected_intervals


@pytest.mark.parametrize("minutes", [7, 0, -3])
def test_intervals_in_local_day_rejects_uneven_intervals(minutes):
    with pytest.raises(ValueError):
        intervals_in_local_day(date(2026, 10, 10), minutes=minutes)
