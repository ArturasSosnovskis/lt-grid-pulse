"""Tests for parse_and_filter: window filter, row validation, quarantine and the completeness check.

All tests use fake rows (no HTTP), shaped like Elering's real response for one day.
"""

import pytest
from datetime import date
from lt_grid_pulse.ingest.elering import parse_and_filter

# A normal day (no clock change): 96 quarter-hour intervals in Vilnius time.
TEST_DAY = date(2026, 11, 17)


def make_fake_day():
    """Return a NEW list of 97 valid raw rows, like Elering sends for TEST_DAY.

    Row 0 is 2026-11-17 00:00 Vilnius time, each next row is 15 minutes (900 s) later.
    Rows 0-95 are the full day. Row 96 is the next day's first interval,
    which Elering includes because the end of the requested window is inclusive.
    A fresh list on every call, so one test changing a row can't affect another test.
    """
    result = []
    for i in range(97):
        result.append({"timestamp": 1794866400 + 900 * i, "price": 50.0})
    return result


@pytest.mark.parametrize(
    "bad_index, expected_good, expected_quarantined",
    [
        (None, 96, 0),   # clean day: row 96 (next day) is filtered out, 96 rows kept
        (9, 95, 1),      # bad price inside the day → quarantined, the run carries on
        (96, 96, 0),     # bad price on the next day's row → skipped by the window, not counted
    ],
    ids=["clean", "bad_in_day", "bad_next_day"],
)
def test_parse_and_filter_counts(bad_index, expected_good, expected_quarantined):
    """Good and quarantined row counts for a day with zero or one bad row."""
    rows = make_fake_day()
    if bad_index is not None:
        rows[bad_index]["price"] = None  # break one row: a missing price
    good, quarantined = parse_and_filter(TEST_DAY, rows)
    assert len(good) == expected_good
    assert len(quarantined) == expected_quarantined


def test_parse_and_filter_quarantine_reason_names_the_field():
    """The quarantine reason names the field that failed."""
    rows = make_fake_day()
    rows[9]["price"] = None
    good, quarantined = parse_and_filter(TEST_DAY, rows)
    assert "price" in quarantined[0].reason


def test_parse_and_filter_rejects_incomplete_day():
    """A missing row in a day: good + quarantined < 96. Raises ValueError."""
    rows = make_fake_day()[:95]  # only the first 95 intervals of the day
    with pytest.raises(ValueError):
        parse_and_filter(TEST_DAY, rows)
