from datetime import datetime

import pytest

import ticket_data as td

OPENED = datetime(2026, 10, 15, 9, 30)


def test_normalise_title_strips_whitespace():
    assert td.normalise_title("  Login page returns 500 \n") == "Login page returns 500"


def test_normalise_title_cuts_to_limit():
    assert td.normalise_title("x" * 60) == "x" * 40
    assert td.normalise_title("  abcdef  ", limit=3) == "abc"


def test_parse_ticket_id_returns_int():
    result = td.parse_ticket_id(" 101 ")
    assert result == 101 and type(result) is int


@pytest.mark.parametrize("bad", ["3.5", "abc", ""])
def test_parse_ticket_id_rejects_non_integers(bad):
    with pytest.raises(ValueError):
        td.parse_ticket_id(bad)


def test_build_queue_sorts_by_rank_then_id():
    rows = [(2, 103, "Wi-Fi drops"), (1, 101, "Login"), (2, 102, "Printer")]
    assert td.build_queue(rows) == [(1, 101, "Login"), (2, 102, "Printer"), (2, 103, "Wi-Fi drops")]


def test_build_queue_returns_new_list_and_keeps_input():
    rows = [(2, 103, "b"), (1, 101, "a")]
    result = td.build_queue(rows)
    assert result is not rows
    assert rows == [(2, 103, "b"), (1, 101, "a")]


def test_unique_reporters_is_a_normalised_set():
    result = td.unique_reporters(["Dana", " dana ", "LEE"])
    assert isinstance(result, set)
    assert result == {"dana", "lee"}


def test_sla_hours_lookup_and_fallback():
    assert td.sla_hours("high") == 4
    assert td.sla_hours(" LOW ") == 72
    assert td.sla_hours("urgent") == 24


def test_deadline_for_adds_sla_hours():
    assert td.deadline_for(OPENED, "high") == datetime(2026, 10, 15, 13, 30)
    assert td.deadline_for(OPENED, "normal") == datetime(2026, 10, 16, 9, 30)


def test_is_breached_is_strictly_after_deadline():
    deadline = datetime(2026, 10, 15, 13, 30)
    assert td.is_breached(OPENED, datetime(2026, 10, 15, 14, 0), "high") is True
    assert td.is_breached(OPENED, deadline, "high") is False
    assert td.is_breached(OPENED, datetime(2026, 10, 15, 14, 0), "normal") is False
