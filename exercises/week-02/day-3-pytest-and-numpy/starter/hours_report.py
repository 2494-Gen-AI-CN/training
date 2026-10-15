"""Resolution-hours report for a ticket desk, built on NumPy arrays."""
import numpy as np

SLA_HOURS = {"high": 4, "normal": 24, "low": 72}


def to_hours(seconds):
    """Turn a list of durations in seconds into a float64 array of hours.

    to_hours([3600, 5400]) -> array([1. , 1.5])

    Args:
        seconds (list of int or float): durations in seconds.

    Returns:
        numpy.ndarray: float64 hours, same length as seconds.
    """
    raise NotImplementedError


def limits_for(priorities):
    """Return an array with the SLA limit in hours for each priority name.

    Look each name up in SLA_HOURS.

    Args:
        priorities (list of str): priority names such as "high" or "low".

    Returns:
        numpy.ndarray: the SLA hours, one per name, in the same order.

    Raises:
        ValueError: a name is not a key of SLA_HOURS; the message contains
            that name.
    """
    raise NotImplementedError


def breach_mask(hours, limits):
    """Return a boolean array: True where hours is strictly above its limit.

    Use one comparison, no loop.

    Args:
        hours (numpy.ndarray): resolution hours, one per ticket.
        limits (numpy.ndarray): SLA hours, same shape as hours.

    Returns:
        numpy.ndarray: bool, same shape; True where hours > limit.
    """
    raise NotImplementedError


def breach_count(hours, limits):
    """Return how many tickets breached their limit.

    Args:
        hours (numpy.ndarray): resolution hours, one per ticket.
        limits (numpy.ndarray): SLA hours, same shape as hours.

    Returns:
        int: a plain Python int, the number of tickets strictly above
            their limit.
    """
    raise NotImplementedError


def mean_hours(hours):
    """Return the mean of the hours array.

    Args:
        hours (numpy.ndarray): resolution hours; may be empty.

    Returns:
        float: a plain Python float; 0.0 when hours is empty.
    """
    raise NotImplementedError
