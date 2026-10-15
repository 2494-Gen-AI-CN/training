import numpy as np
import pytest

from hours_report import (
    breach_count,
    breach_mask,
    limits_for,
    mean_hours,
    to_hours,
)


def test_to_hours_is_float_array():
    hours = to_hours([3600, 5400])
    assert isinstance(hours, np.ndarray)
    assert hours.dtype == np.float64
    assert hours.shape == (2,)
    assert np.allclose(hours, [1.0, 1.5])


def test_limits_for_maps_priorities():
    assert np.array_equal(limits_for(["high", "low", "normal"]), [4, 72, 24])


def test_limits_for_unknown_priority_raises():
    with pytest.raises(ValueError, match="urgent"):
        limits_for(["high", "urgent"])


def test_breach_mask_is_boolean_and_strict():
    hours = np.array([3.0, 30.0, 24.0])
    limits = np.array([4, 24, 24])
    mask = breach_mask(hours, limits)
    assert mask.dtype == np.bool_
    assert np.array_equal(mask, [False, True, False])


def test_breach_count_is_plain_int():
    count = breach_count(np.array([5.0, 30.0, 1.0]), np.array([4, 24, 72]))
    assert count == 2
    assert type(count) is int


def test_mean_hours_is_plain_float():
    result = mean_hours(np.array([3.0, 30.0]))
    assert result == pytest.approx(16.5)
    assert type(result) is float


def test_mean_hours_empty_is_zero():
    assert mean_hours(to_hours([])) == 0.0
