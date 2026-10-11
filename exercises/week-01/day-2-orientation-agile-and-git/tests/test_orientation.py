"""Tests for the w01d2 orientation exercise. Deterministic, stdlib + pytest only."""

import pytest

from orientation import (
    STORY_POINT_SCALE,
    add_tax,
    branch_name,
    commit_line,
    greet,
    is_story_point,
    sprint_window,
)


def test_greet_builds_welcome_sentence():
    assert greet("Ana") == "Hello, Ana! Welcome to the Gen AI cohort."
    assert greet("Chen") == "Hello, Chen! Welcome to the Gen AI cohort."


def test_add_tax_uses_hst_by_default():
    assert add_tax(100) == pytest.approx(113.0)
    assert add_tax(19.99) == pytest.approx(22.59)


def test_add_tax_accepts_a_custom_rate():
    assert add_tax(200, 0.05) == pytest.approx(210.0)
    assert add_tax(50, 0) == pytest.approx(50.0)


def test_sprint_window_returns_first_and_last_week():
    assert sprint_window(1) == (1, 2)
    assert sprint_window(3) == (5, 6)
    assert sprint_window(2, sprint_weeks=3) == (4, 6)


def test_is_story_point_accepts_only_scale_values():
    for value in STORY_POINT_SCALE:
        assert is_story_point(value) is True
    assert is_story_point(4) is False
    assert is_story_point(0) is False


def test_branch_name_slugs_title_for_git():
    assert branch_name(42, "Add hello script") == "feature/42-add-hello-script"
    assert branch_name(7, "  Set Up The Shared Team Repo ") == "feature/7-set-up-the-shared-team-repo"


def test_commit_line_shortens_hash_to_seven_chars():
    full = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
    assert commit_line(full, "add hello script") == "a1b2c3d add hello script"
    assert len(commit_line(full, "x").split(" ")[0]) == 7
