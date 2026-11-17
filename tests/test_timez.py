from lt_grid_pulse.utils.timez import parse_iso, to_vilnius
from datetime import datetime, timezone, timedelta
import pytest

@pytest.mark.parametrize(
    "text, expected",
    [
        ("2010-10-10T10:10:10+10:00", datetime(2010, 10, 10, 0, 10, 10, tzinfo=timezone.utc)),
        ("2026-11-17T08:00:00Z", datetime(2026, 11, 17, 8, 0, tzinfo=timezone.utc))
    ]
)
def test_parse_iso_returns_utc(text, expected):
    result = parse_iso(text)
    assert result == expected
    assert result.utcoffset() == timedelta(0) 


@pytest.mark.parametrize(
    "text",
    [
        "2026-11-17T08:00:00",
        "2022-11-13T12:36:52"
    ]
)
def test_parse_iso_rejects_naive_text(text):
    with pytest.raises(ValueError, match="No timezone offset"):
        parse_iso(text)


@pytest.mark.parametrize(
    "text",
    [
        "BANNNNAAANA",
        "",
        "2026-13-17T08:00:00Z"
    ]
)
def test_parse_iso_rejects_invalid_text(text):
    with pytest.raises(ValueError):
        parse_iso(text)


@pytest.mark.parametrize(
    "dt, expected_hour, expected_offset",
    [
        (datetime(2026, 11, 17, 8, 0, tzinfo=timezone.utc), 10, timedelta(hours=2)),
        (datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc), 15, timedelta(hours=3)),
    ]
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
    ]
)
def test_to_vilnius_rejects_naive_dt (dt):
    with pytest.raises(ValueError, match = "Naive datetime"):
        to_vilnius(dt)
