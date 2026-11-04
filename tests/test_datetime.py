from datetime import date, datetime, time, timedelta, timezone
from io import BytesIO
import sys

import pytest

import tomli_w

if sys.version_info >= (3, 11):
    import tomllib as tomli
else:
    import tomli


@pytest.mark.parametrize(
    "value,expected",
    [
        (datetime(2026, 1, 2, 3, 4, 5), "2026-01-02T03:04:05"),
        (
            datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
            "2026-01-02T03:04:05+00:00",
        ),
        (
            datetime(2026, 1, 2, 3, 4, 5, 1, tzinfo=timezone.utc),
            "2026-01-02T03:04:05.000001+00:00",
        ),
        (
            datetime(
                2026,
                1,
                2,
                3,
                4,
                5,
                123456,
                tzinfo=timezone(timedelta(hours=5, minutes=30)),
            ),
            "2026-01-02T03:04:05.123456+05:30",
        ),
        (
            datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=-7))),
            "2026-01-02T03:04:05-07:00",
        ),
        (datetime.min, "0001-01-01T00:00:00"),
        (datetime.max, "9999-12-31T23:59:59.999999"),
    ],
)
@pytest.mark.parametrize("separator", [" ", "T", "t"])
def test_datetime_separator(value, expected, separator):
    document = {"when": value}
    text = tomli_w.dumps(document, datetime_separator=separator)
    assert text == f"when = {expected.replace('T', separator)}\n"
    assert tomli.loads(text) == document


def test_datetime_in_inline_table():
    value = datetime(2026, 1, 2, tzinfo=timezone.utc)
    document = {"events": [{"when": value}]}

    text = tomli_w.dumps(document, datetime_separator="T")
    assert text == "events = [\n    { when = 2026-01-02T00:00:00+00:00 },\n]\n"
    assert tomli.loads(text) == document


@pytest.mark.parametrize("separator", [" ", "T", "t"])
def test_date_and_time_with_datetime_separator(separator):
    document = {"date": date(2026, 1, 2), "time": time(3, 4, 5, 123456)}
    text = tomli_w.dumps(document, datetime_separator=separator)
    assert text == "date = 2026-01-02\ntime = 03:04:05.123456\n"
    assert tomli.loads(text) == document


def test_default_datetime_separator():
    value = datetime(2026, 1, 2, tzinfo=timezone.utc)
    assert tomli_w.dumps({"when": value}) == "when = 2026-01-02 00:00:00+00:00\n"


def test_default_datetime_subclass_format():
    class LowercaseDatetime(datetime):
        def __str__(self) -> str:
            return self.isoformat(sep="t")

    value = LowercaseDatetime(2026, 1, 2)
    assert tomli_w.dumps({"when": value}) == "when = 2026-01-02t00:00:00\n"
    assert (
        tomli_w.dumps({"when": value}, datetime_separator="T")
        == "when = 2026-01-02T00:00:00\n"
    )


@pytest.mark.parametrize("separator", ["", "TT", "x", "\n"])
def test_invalid_datetime_separator(separator):
    with pytest.raises(ValueError, match="Datetime separator"):
        tomli_w.dumps({}, datetime_separator=separator)
    with pytest.raises(ValueError, match="Datetime separator"):
        tomli_w.dump({}, BytesIO(), datetime_separator=separator)
