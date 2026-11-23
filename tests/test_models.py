import pytest
from pydantic import ValidationError
from lt_grid_pulse.ingest.models import EleringRawRow


@pytest.mark.parametrize(
    "row",
    [
        # price checks
        {"timestamp": 1794866400, "price": None},
        {"timestamp": 1794866400, "price": "72.4"},
        {"timestamp": 1794866400, "price": 99999},
        {"timestamp": 1794866400, "price": -500.01},
        {"timestamp": 1794866400, "price": 4000.01},
        # timestamp checks
        {"price": 72.4},
        {"timestamp": "1794866400", "price": 72.4},
        {"timestamp": -1, "price": 72.4},
        {"timestamp": None, "price": None},
    ],
)
def test_elering_input_model_fails_on_invalid_rows(row):
    with pytest.raises(ValidationError):
        EleringRawRow.model_validate(row)


@pytest.mark.parametrize(
    "row, expected_result",
    [
        # price checks
        ({"timestamp": 1794866400, "price": 72.4}, 72.4),
        ({"timestamp": 1794866400, "price": -12.5}, -12.5),
        ({"timestamp": 1794866400, "price": 80}, 80.0),

        ({"timestamp": 1794866400, "price": 4000}, 4000.0),
        ({"timestamp": 1794866400, "price": -500}, -500.0),
        ({"timestamp": 1794866400, "price": 0.0}, 0.0),
    ],
)
def test_elering_input_model_accepts_valid_price_in_rows(row, expected_result):
    result = EleringRawRow.model_validate(row)
    assert result.price == expected_result
    assert isinstance(result.price, float)


@pytest.mark.parametrize(
    "row, expected_result",
    [
        ({"timestamp": 0, "price": 0.0}, 0),
        ({"timestamp": 1794866400, "price": 0.0}, 1794866400),
    ],
)
def test_elering_input_model_accepts_valid_timestamp_in_rows(row, expected_result):
    result = EleringRawRow.model_validate(row)
    assert result.timestamp == expected_result
    assert isinstance(result.timestamp, int)


@pytest.mark.parametrize(
    "row, expected_result",
    [
        ({"timestamp": 1794866400, "price": 72.4, "extra": 1}, {"timestamp", "price"}),
    ],
)
def test_elering_input_model_ignore_extra_columns(row, expected_result):
    result = EleringRawRow.model_validate(row).model_dump()
    assert result.keys() == expected_result
