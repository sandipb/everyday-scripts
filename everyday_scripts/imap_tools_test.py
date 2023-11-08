import pytest
from .imap_tools import match_email_against_patterns


@pytest.mark.parametrize(
    "header, patterns, expected_result",
    [
        ("IIM Calcutta <mail@timesjobs.com>", ["timesjobs"], (True, ["timesjobs"])),
        (
            "Swiggy <no-reply@swiggy.in>",
            ["sefindia.org", "dynamicwealthresearch.com", "swiggy.in"],
            (True, ["swiggy.in"]),
        ),
        ("John Doe <mail@example.com>", ["timesjobs"], (False, [])),
        (
            "John Doe <john.doe@example.com>",
            ["example", "john"],
            (True, ["example", "john"]),
        ),
    ],
)
def test_match_email_against_patterns(header, patterns, expected_result):
    result = match_email_against_patterns(header, patterns)
    assert result == expected_result
