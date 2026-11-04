import sys

import pytest

import tomli_w
from tomli_w import _writer

if sys.version_info >= (3, 11):
    import tomllib as tomli
else:
    import tomli


@pytest.fixture(params=[False, True], ids=["python-loop", "translate"], autouse=True)
def string_implementation(request, monkeypatch):
    """Check both formatting paths on each supported runtime."""
    monkeypatch.setattr(_writer, "USE_STR_TRANSLATE", request.param)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("", ""),
        ("plain text", "plain text"),
        ("snow 雪 café 😀", "snow 雪 café 😀"),
        ("\x00\x01\x1f\x7f", r"\u0000\u0001\u001f\u007f"),
        (
            "".join(chr(i) for i in range(32) if i != 10) + "\x7f",
            (
                r"\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007"
                "\\b\t\\u000b\\f\\r"
                r"\u000e\u000f\u0010\u0011\u0012\u0013\u0014\u0015"
                r"\u0016\u0017\u0018\u0019\u001a\u001b\u001c\u001d\u001e\u001f\u007f"
            ),
        ),
        ("\b\f\r", r"\b\f\r"),
        ('"\\', r"\"\\"),
        ("\t", "\t"),
        (r"\t", r"\\t"),
    ],
)
@pytest.mark.parametrize("multiline_strings", [False, True])
def test_single_line_string_escaping(value, expected, multiline_strings):
    text = tomli_w.dumps({"value": value}, multiline_strings=multiline_strings)
    assert text == f'value = "{expected}"\n'
    assert tomli.loads(text)["value"] == value


def test_quoted_key_escaping():
    key = 'a"\t\x7f'
    text = tomli_w.dumps({key: "value"})
    assert text == '"a\\"\t\\u007f" = "value"\n'
    assert tomli.loads(text) == {key: "value"}


def test_newlines_without_multiline_strings():
    text = tomli_w.dumps({"value": "a\r\nb\nc"})
    assert text == 'value = "a\\r\\nb\\nc"\n'
    assert tomli.loads(text)["value"] == "a\r\nb\nc"


def test_string_subclass_slicing():
    class UppercaseSlices(str):
        def __getitem__(self, key):
            value = super().__getitem__(key)
            return value.upper() if isinstance(key, slice) else value

    text = tomli_w.dumps({"value": UppercaseSlices("lower")})
    assert text == 'value = "LOWER"\n'


def test_string_subclass_escaping():
    class String(str):
        pass

    value = String('\n"\x00')
    text = tomli_w.dumps({"value": value})
    assert text == 'value = "\\n\\"\\u0000"\n'
    assert tomli.loads(text)["value"] == value
