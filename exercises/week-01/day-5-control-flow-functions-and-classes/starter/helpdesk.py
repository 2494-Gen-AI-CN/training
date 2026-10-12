"""Help desk: tickets, a status check, and a desk that owns and iterates tickets."""

from collections.abc import Iterator
from datetime import datetime, timedelta

SLA_HOURS = {"high": 4, "normal": 24, "low": 72}
PRIORITY_RANK = {"high": 1, "normal": 2, "low": 3}
STATUSES = ("closed", "breached", "at risk", "on time")
AT_RISK_WINDOW = timedelta(hours=2)


class Ticket:
    """One support ticket and the rules that belong to it."""

    def __init__(self, ticket_id: int, title: str, priority: str, opened_at: datetime) -> None:
        """Store the four arguments as attributes of the same names.

        Also set the attribute `is_open` to True: a new ticket is open.

        Args:
            ticket_id: the ticket's number, a positive int.
            title: a short description of the problem.
            priority: one of the SLA_HOURS keys: "high", "normal" or "low".
            opened_at: when the ticket was opened.

        Returns:
            None.
        """
        raise NotImplementedError

    def deadline(self) -> datetime:
        """Work out when this ticket breaches its SLA.

        Returns:
            `opened_at` plus the SLA_HOURS entry for this ticket's priority,
            as a datetime.
        """
        raise NotImplementedError

    def close(self) -> None:
        """Mark the ticket as no longer open.

        Returns:
            None. Afterwards `is_open` is False.
        """
        raise NotImplementedError


class UrgentTicket(Ticket):
    """A ticket that gets half the usual time."""

    def deadline(self) -> datetime:
        """Work out the deadline of an urgent ticket.

        Reuse the parent's rule through `super()`; do not look up SLA_HOURS
        again here.

        Returns:
            The datetime halfway between `opened_at` and the deadline a plain
            Ticket with the same priority would get.
        """
        raise NotImplementedError


def status(ticket: Ticket, now: datetime) -> str:
    """Name the state a ticket is in at the moment `now`.

    Write it with guard clauses (early returns) and no nested `if`. Check the
    cases in this order:
    a ticket that is not open is "closed";
    a ticket whose deadline is before `now` is "breached";
    a ticket with less than AT_RISK_WINDOW left is "at risk";
    anything else is "on time".

    The edges follow from the wording: a ticket exactly at its deadline is not
    breached yet, so it is "at risk"; a ticket with exactly AT_RISK_WINDOW left
    is "on time".

    Args:
        ticket: a Ticket or an UrgentTicket.
        now: the moment to judge the ticket at.

    Returns:
        One of the four labels in STATUSES.
    """
    raise NotImplementedError


class Desk:
    """A desk owns its tickets and hands them out one at a time.

    Class attribute (you add it to the class body):
        next_id: an int, the id the next `open_ticket` call will use. It
            starts at 1 and belongs to the class, so every Desk shares the
            one counter.
    """

    def __init__(self) -> None:
        """Start with no tickets.

        Returns:
            None.
        """
        raise NotImplementedError

    def add(self, ticket: Ticket) -> None:
        """Add an existing ticket to the end of the desk.

        Also keep the shared counter ahead of the ids in use: after the call
        `Desk.next_id` is greater than `ticket.ticket_id`. The counter never
        goes down.

        Args:
            ticket: the Ticket (or UrgentTicket) to add.

        Returns:
            None.
        """
        raise NotImplementedError

    def open_ticket(
        self, title: str, priority: str, opened_at: datetime, urgent: bool = False
    ) -> Ticket:
        """Create a ticket numbered `Desk.next_id`, add it to this desk, return it.

        The counter moves on, so the next ticket opened on ANY desk gets the
        following id.

        Args:
            title: a short description of the problem.
            priority: "high", "normal" or "low".
            opened_at: when the ticket was opened.
            urgent: when True the new ticket is an UrgentTicket, otherwise a
                plain Ticket.

        Returns:
            The new ticket, which is now the last one on this desk.
        """
        raise NotImplementedError

    def __len__(self) -> int:
        """Count the tickets, so that `len(desk)` works.

        Returns:
            The number of tickets the desk holds, as an int.
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[Ticket]:
        """Make `for ticket in desk` work.

        Returns:
            A fresh iterator over the tickets in the order they were added.
            Each call starts again from the first ticket.
        """
        raise NotImplementedError

    def by_priority(self) -> list[Ticket]:
        """List the tickets in the order the team should work on them.

        Sort with a lambda key built from PRIORITY_RANK and `opened_at`.

        Returns:
            A NEW list: high before normal before low, and the oldest
            `opened_at` first within one priority. The order the desk itself
            iterates in stays as it was.
        """
        raise NotImplementedError

    def overdue(self, now: datetime) -> list[Ticket]:
        """Find the tickets that need attention first.

        Args:
            now: the moment to judge the tickets at.

        Returns:
            A new list of the OPEN tickets whose deadline is before `now`, in
            the order they were added. A ticket exactly at its deadline is not
            overdue. An empty list when there are none.
        """
        raise NotImplementedError

    def count_by_status(self, now: datetime) -> dict[str, int]:
        """Tally the desk's tickets by the label `status` gives them.

        Args:
            now: the moment to judge the tickets at.

        Returns:
            A dict with every label in STATUSES as a key and the number of
            tickets in that state as the value. A label no ticket has still
            appears, with 0.
        """
        raise NotImplementedError
