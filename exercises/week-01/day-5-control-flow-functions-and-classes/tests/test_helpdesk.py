from datetime import datetime, timedelta

from helpdesk import Desk, Ticket, UrgentTicket, status

T0 = datetime(2026, 10, 15, 9, 0)


def test_ticket_deadline_uses_priority_sla():
    assert Ticket(1, "a", "high", T0).deadline() == T0 + timedelta(hours=4)
    assert Ticket(2, "b", "normal", T0).deadline() == T0 + timedelta(hours=24)
    assert Ticket(3, "c", "low", T0).deadline() == T0 + timedelta(hours=72)


def test_ticket_starts_open_and_close_works():
    t = Ticket(1, "a", "normal", T0)
    assert (t.ticket_id, t.title, t.priority, t.opened_at) == (1, "a", "normal", T0)
    assert t.is_open is True
    t.close()
    assert t.is_open is False


def test_urgent_ticket_halves_the_time():
    t = UrgentTicket(1, "a", "normal", T0)
    assert isinstance(t, Ticket)
    assert t.deadline() == T0 + timedelta(hours=12)
    assert UrgentTicket(2, "b", "high", T0).deadline() == T0 + timedelta(hours=2)


def test_desk_len_and_for_loop_keep_insertion_order():
    desk = Desk()
    assert len(desk) == 0
    a, b = Ticket(1, "a", "low", T0), Ticket(2, "b", "high", T0)
    desk.add(a)
    desk.add(b)
    assert len(desk) == 2
    assert [t for t in desk] == [a, b]
    assert [t for t in desk] == [a, b]  # iterating twice works


def test_desk_supports_manual_iter_and_next():
    desk = Desk()
    a, b = Ticket(1, "a", "low", T0), Ticket(2, "b", "low", T0)
    desk.add(a)
    desk.add(b)
    it = iter(desk)
    assert next(it) is a
    assert next(it) is b
    assert next(iter(desk)) is a  # a second iterator starts from the first ticket


def test_by_priority_sorts_rank_then_opened_at_without_mutating():
    desk = Desk()
    low = Ticket(1, "low", "low", T0)
    late_high = Ticket(2, "late", "high", T0 + timedelta(hours=1))
    early_high = Ticket(3, "early", "high", T0)
    normal = Ticket(4, "normal", "normal", T0)
    for t in (low, late_high, early_high, normal):
        desk.add(t)
    assert desk.by_priority() == [early_high, late_high, normal, low]
    assert list(desk) == [low, late_high, early_high, normal]


def test_overdue_skips_closed_and_on_time_tickets():
    desk = Desk()
    late_low = Ticket(1, "late low", "low", T0 - timedelta(days=4))
    closed = Ticket(2, "closed", "high", T0)
    closed.close()
    fine = Ticket(3, "fine", "low", T0)
    late_high = Ticket(4, "late high", "high", T0)
    for t in (late_low, closed, fine, late_high):
        desk.add(t)
    # order added, not priority order
    assert desk.overdue(T0 + timedelta(hours=5)) == [late_low, late_high]
    # exactly at its deadline, late_high is not overdue yet
    assert desk.overdue(T0 + timedelta(hours=4)) == [late_low]
    assert desk.overdue(T0 - timedelta(days=2)) == []


def test_status_covers_all_four_outcomes():
    now = T0 + timedelta(hours=3)
    breached = Ticket(1, "a", "high", T0 - timedelta(hours=2))
    at_risk = Ticket(2, "b", "high", T0)  # 1 hour left
    on_time = Ticket(3, "c", "low", T0)
    closed = Ticket(4, "d", "high", T0 - timedelta(hours=9))
    closed.close()
    assert status(breached, now) == "breached"
    assert status(at_risk, now) == "at risk"
    assert status(on_time, now) == "on time"
    assert status(closed, now) == "closed"
    # the two edges the docstring names
    at_deadline = Ticket(5, "e", "high", T0 - timedelta(hours=1))
    two_hours_left = Ticket(6, "f", "high", T0 + timedelta(hours=1))
    assert status(at_deadline, now) == "at risk"
    assert status(two_hours_left, now) == "on time"
    # an UrgentTicket is judged by its own, shorter deadline
    assert status(UrgentTicket(7, "g", "high", T0), now) == "breached"


def test_open_ticket_numbers_from_the_shared_class_counter():
    assert "next_id" in vars(Desk)  # declared on the class, not on one desk
    Desk.next_id = 1  # reset the shared counter so this test stands alone
    front, back = Desk(), Desk()
    first = front.open_ticket("a", "low", T0)
    second = back.open_ticket("b", "normal", T0, urgent=True)
    assert (first.ticket_id, second.ticket_id) == (1, 2)  # one counter, two desks
    assert (first.title, first.priority, first.opened_at) == ("a", "low", T0)
    assert type(first) is Ticket
    assert type(second) is UrgentTicket
    assert list(front) == [first]
    assert list(back) == [second]
    back.add(Ticket(7, "imported", "low", T0))  # add() keeps the counter ahead
    assert Desk.next_id == 8
    assert front.open_ticket("c", "high", T0).ticket_id == 8
    front.add(Ticket(3, "old", "low", T0))  # a lower id never moves it back
    assert Desk.next_id == 9


def test_count_by_status_tallies_every_label():
    now = T0 + timedelta(hours=3)
    desk = Desk()
    assert desk.count_by_status(now) == {"closed": 0, "breached": 0, "at risk": 0, "on time": 0}
    desk.add(Ticket(1, "a", "high", T0 - timedelta(hours=2)))  # breached
    desk.add(Ticket(2, "b", "high", T0))  # at risk
    desk.add(UrgentTicket(3, "c", "high", T0))  # breached: half the window
    done = Ticket(4, "d", "low", T0)
    done.close()
    desk.add(done)
    assert desk.count_by_status(now) == {"closed": 1, "breached": 2, "at risk": 1, "on time": 0}
