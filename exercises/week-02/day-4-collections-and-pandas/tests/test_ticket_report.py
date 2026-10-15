import json
from collections import Counter, OrderedDict

import pytest

from ticket_report import (
    TicketRow,
    ids_by_agent,
    load_frame,
    status_counts,
    status_table,
    to_rows,
    work_queue,
)

TICKETS = [
    {"ticket_id": 1, "priority": "high", "status": "closed", "assignee": "Priya"},
    {"ticket_id": 2, "priority": "low", "status": "open"},
    {"ticket_id": 3, "priority": "normal", "status": "assigned", "assignee": "Marcus"},
    {"ticket_id": 4, "priority": "high", "status": "assigned", "assignee": "Priya"},
    {"ticket_id": 5, "priority": "normal", "status": "open"},
    {"ticket_id": 6, "priority": "normal", "status": "closed", "assignee": "Marcus"},
    {"ticket_id": 7, "priority": "high", "status": "open"},
]


@pytest.fixture
def json_path(tmp_path):
    path = tmp_path / "tickets.json"
    path.write_text(json.dumps(TICKETS))
    return path


def test_status_counts_is_counter():
    counts = status_counts(TICKETS)
    assert isinstance(counts, Counter)
    assert counts == {"open": 3, "assigned": 2, "closed": 2}
    assert counts["escalated"] == 0


def test_status_counts_empty():
    assert status_counts([]) == Counter()


def test_to_rows_are_named_tuples():
    rows = to_rows(TICKETS)
    assert len(rows) == 7
    assert rows[0] == TicketRow(1, "high", "closed", "Priya")
    assert rows[1].assignee is None
    assert rows[2].status == "assigned"
    assert TicketRow._fields == ("ticket_id", "priority", "status", "assignee")


def test_work_queue_order_and_type():
    queue = work_queue(to_rows(TICKETS))
    assert isinstance(queue, OrderedDict)
    assert list(queue) == [4, 7, 3, 5, 2]
    assert queue[4].assignee == "Priya"


def test_work_queue_leaves_out_closed():
    assert 1 not in work_queue(to_rows(TICKETS))
    assert work_queue([]) == OrderedDict()


def test_ids_by_agent_groups_and_skips_unassigned():
    groups = ids_by_agent(to_rows(TICKETS))
    assert groups == {"Priya": [1, 4], "Marcus": [3, 6]}
    assert type(groups) is dict


def test_load_frame_reads_json(json_path):
    df = load_frame(json_path)
    assert df.shape[0] == 7
    assert list(df["ticket_id"]) == [1, 2, 3, 4, 5, 6, 7]
    assert "status" in df.columns


def test_status_table_matches_counter(json_path):
    df = load_frame(json_path)
    table = status_table(df)
    assert type(table) is dict
    assert table == dict(status_counts(TICKETS))
