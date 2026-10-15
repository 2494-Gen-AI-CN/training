import logging
import pathlib
import subprocess
import sys
from datetime import datetime

import deskkit

T0 = datetime(2026, 10, 19, 8, 0)


def test_days_open_rounds_up_to_whole_days():
    assert deskkit.days_open(T0, datetime(2026, 10, 19, 8, 0)) == 0
    assert deskkit.days_open(T0, datetime(2026, 10, 19, 20, 0)) == 1
    assert deskkit.days_open(T0, datetime(2026, 10, 20, 8, 0)) == 1
    assert deskkit.days_open(T0, datetime(2026, 10, 20, 8, 1)) == 2
    assert deskkit.days_open(T0, datetime(2026, 10, 23, 8, 0)) == 4


def test_is_past_sla_is_strict_at_the_deadline():
    assert deskkit.is_past_sla("high", T0, datetime(2026, 10, 19, 12, 0)) is False
    assert deskkit.is_past_sla("high", T0, datetime(2026, 10, 19, 12, 1)) is True
    assert deskkit.is_past_sla("low", T0, datetime(2026, 10, 22, 8, 0)) is False
    assert deskkit.is_past_sla("low", T0, datetime(2026, 10, 22, 8, 1)) is True


def test_module_level_logger_is_named_after_the_module():
    assert isinstance(deskkit.log, logging.Logger)
    assert deskkit.log.name == "deskkit"


def test_check_sla_warns_once_for_a_late_ticket(caplog):
    with caplog.at_level(logging.INFO, logger="deskkit"):
        late = deskkit.check_sla(7, "high", T0, datetime(2026, 10, 19, 13, 0))
    assert late is True
    records = [r for r in caplog.records if r.name == "deskkit"]
    assert len(records) == 1
    assert records[0].levelno == logging.WARNING
    assert records[0].getMessage() == "TD-7 is past its SLA"
    assert records[0].args, "pass the id as a %s argument instead of building an f-string"


def test_check_sla_is_silent_when_on_time(caplog):
    with caplog.at_level(logging.DEBUG, logger="deskkit"):
        late = deskkit.check_sla(8, "normal", T0, datetime(2026, 10, 19, 9, 0))
    assert late is False
    assert [r for r in caplog.records if r.name == "deskkit"] == []


def test_ticket_refs_finds_numbers_in_order():
    assert deskkit.ticket_refs("Same as TD-2 and TD-15, also TD-2") == [2, 15, 2]
    assert deskkit.ticket_refs("nothing here") == []


def test_ticket_refs_ignores_near_misses():
    assert deskkit.ticket_refs("XTD-3 TD- TD-x TD-4x") == []
    assert deskkit.ticket_refs("(TD-9).") == [9]


def test_patterns_are_compiled_at_module_level():
    assert hasattr(deskkit.TICKET_REF, "finditer")
    assert hasattr(deskkit.EMAIL, "sub")


def test_redact_replaces_every_email():
    text = "write dana@example.com or lee.k+help@mail.co.uk today"
    assert deskkit.redact(text) == "write [email] or [email] today"
    assert deskkit.redact("no address") == "no address"


def test_importing_prints_nothing_but_running_the_file_does():
    here = pathlib.Path(deskkit.__file__).resolve()
    imported = subprocess.run([sys.executable, "-c", "import deskkit"],
                              capture_output=True, text=True, cwd=str(here.parent))
    assert imported.returncode == 0
    assert imported.stdout == "" and imported.stderr == ""
    ran = subprocess.run([sys.executable, str(here)], capture_output=True, text=True)
    assert ran.returncode == 0
    assert ran.stdout.strip() == "[2, 5]"
