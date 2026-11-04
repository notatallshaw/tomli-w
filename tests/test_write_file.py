from datetime import datetime, timezone

import pytest

import tomli_w


def test_dump(tmp_path):
    toml_obj = {"testing": "test\ntest"}
    path = tmp_path / "test.toml"
    with open(path, "wb") as f:
        tomli_w.dump(toml_obj, f)
    assert path.read_bytes().decode() == 'testing = "test\\ntest"\n'


@pytest.mark.parametrize("separator", [" ", "T", "t"])
def test_dump_datetime_separator(tmp_path, separator):
    toml_obj = {"when": datetime(2026, 1, 2, tzinfo=timezone.utc)}
    path = tmp_path / "test.toml"
    with open(path, "wb") as f:
        tomli_w.dump(toml_obj, f, datetime_separator=separator)
    assert path.read_bytes().decode() == f"when = 2026-01-02{separator}00:00:00+00:00\n"
