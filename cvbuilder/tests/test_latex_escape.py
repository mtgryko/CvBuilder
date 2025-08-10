import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.latex import escape_latex

@pytest.mark.parametrize(
    "raw, escaped",
    [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("_", r"\_"),
        ("\\", r"\textbackslash{}"),
    ],
)
def test_escape_special_chars(raw, escaped):
    assert escape_latex(raw) == escaped

@pytest.mark.parametrize("value", [123, None, ["list"]])
def test_non_string_returns_input_unchanged(value):
    assert escape_latex(value) is value
