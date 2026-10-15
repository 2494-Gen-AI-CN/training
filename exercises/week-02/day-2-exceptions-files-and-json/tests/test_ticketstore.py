import json
from datetime import datetime

import pytest

from ticketstore import append_ticket, delete_file, load_tickets, save_tickets

OPENED = datetime(2026, 10, 20, 9, 0)


def make(ticket_id=1, closed_at=None):
    return {"ticket_id": ticket_id, "title": "Reset password",
            "priority": "high", "opened_at": OPENED, "closed_at": closed_at}


def test_round_trip_restores_the_same_tickets(tmp_path):
    path = tmp_path / "tickets.json"
    tickets = [make(1), make(2, closed_at=datetime(2026, 10, 20, 11, 30))]
    save_tickets(tickets, path)
    assert load_tickets(path) == tickets


def test_dates_are_written_as_iso_text_and_none_as_null(tmp_path):
    path = tmp_path / "tickets.json"
    save_tickets([make()], path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw[0]["opened_at"] == "2026-10-20T09:00:00"
    assert raw[0]["closed_at"] is None


def test_save_does_not_change_the_dicts_passed_in(tmp_path):
    tickets = [make()]
    save_tickets(tickets, tmp_path / "t.json")
    assert tickets[0]["opened_at"] == OPENED


def test_save_replaces_an_existing_file(tmp_path):
    path = tmp_path / "t.json"
    save_tickets([make(1), make(2)], path)
    save_tickets([make(3)], path)
    assert [t["ticket_id"] for t in load_tickets(path)] == [3]


def test_missing_file_gives_empty_list_and_is_not_created(tmp_path):
    path = tmp_path / "nope.json"
    assert load_tickets(path) == []
    assert not path.exists()


def test_corrupt_file_raises_value_error_chained_to_decode_error(tmp_path):
    path = tmp_path / "t.json"
    path.write_text('[{"ticket_id": 1}', encoding="utf-8")
    with pytest.raises(ValueError, match="is not valid JSON") as info:
        load_tickets(path)
    assert isinstance(info.value.__cause__, json.JSONDecodeError)


def test_append_creates_the_file_then_adds(tmp_path):
    path = tmp_path / "t.json"
    append_ticket(path, make(1))
    append_ticket(path, make(2))
    assert [t["ticket_id"] for t in load_tickets(path)] == [1, 2]


def test_append_to_corrupt_file_raises_and_leaves_it_alone(tmp_path):
    path = tmp_path / "t.json"
    path.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError):
        append_ticket(path, make())
    assert path.read_text(encoding="utf-8") == "not json"


def test_delete_file_returns_true_then_false(tmp_path):
    path = tmp_path / "t.json"
    path.write_text("[]", encoding="utf-8")
    assert delete_file(path) is True
    assert not path.exists()
    assert delete_file(path) is False
