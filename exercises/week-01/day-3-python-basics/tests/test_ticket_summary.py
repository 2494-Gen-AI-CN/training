import ticket_summary as ts


def test_age_days_is_floor_division():
    assert ts.age_days(50) == 2
    assert ts.age_days(23.5) == 0


def test_hours_left_goes_negative_when_late():
    assert ts.hours_left(4, 1.5) == 2.5
    assert ts.hours_left(4, 5.5) == -1.5


def test_is_breached_open_and_late():
    assert ts.is_breached(True, 4, 5.5) is True
    assert ts.is_breached(True, 4, 3) is False
    # exactly zero hours left is not a breach yet
    assert ts.is_breached(True, 4, 4) is False
    # a closed ticket is never breached, however late it was
    assert ts.is_breached(False, 4, 100) is False


def test_priority_ok_accepts_three_values_and_rejects_other_text():
    assert ts.priority_ok("high") is True
    assert ts.priority_ok("normal") is True
    assert ts.priority_ok("low") is True
    # the `== "high" or "normal"` pitfall returns a truthy string here
    assert ts.priority_ok("urgent") is False
    assert ts.priority_ok("") is False


def test_is_first_day_bounds():
    assert ts.is_first_day(0) is True
    assert ts.is_first_day(23.9) is True
    assert ts.is_first_day(24) is False
    assert ts.is_first_day(-1) is False


def test_escalate_every_third_id():
    assert ts.escalate(9) is True
    assert ts.escalate(101) is False


def test_sla_used_percent_rounds_to_one_decimal():
    assert ts.sla_used_percent(4, 5.5) == 137.5
    assert ts.sla_used_percent(24, 5) == 20.8
    assert ts.sla_used_percent(72, 1) == 1.4
    # 6.25 sits exactly between 6.2 and 6.3; round goes to the even one
    assert ts.sla_used_percent(4, 0.25) == 6.2


def test_summary_line_alignment_and_long_title():
    line = ts.summary_line(7, "Login bug", "high", 5.5, "Ada")
    assert line == "#7 Login bug               high   5.5h Ada"
    # a title wider than its column pushes the line out; it is not cut
    title = "Login page returns 500 error"
    line = ts.summary_line(101, title, "low", 12.5, "Ada")
    assert line == "#101 Login page returns 500 error     low  12.5h Ada"


def test_print_board_header_and_row_on_stdout(capsys):
    result = ts.print_board(101, "Login bug", "high", 5.5, 4)
    out, err = capsys.readouterr()
    assert result is None
    assert err == ""
    assert out == (
        "  ID | Title                | Priority |  Hours |  SLA % |\n"
        " 101 | Login bug            |     high |    5.5 |  137.5 |\n"
    )


def test_warn_breach_writes_one_line_to_stderr_only(capsys):
    ts.warn_breach(101, True, 4, 5.5)
    out, err = capsys.readouterr()
    assert out == ""
    assert err == "warning: ticket 101 breached=True hours_left=-1.5\n"
    ts.warn_breach(7, True, 4, 3)
    out, err = capsys.readouterr()
    assert out == ""
    assert err == "warning: ticket 7 breached=False hours_left=1.0\n"
