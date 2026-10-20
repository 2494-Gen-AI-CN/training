# Exercise — Resolution hours with NumPy, checked by pytest

Week 2 · Day 3 · `w02d3` · Wed 2026-10-21 · ~60–90 min
Notes: [weeks/week-02/day-3-pytest-and-numpy.html](https://2494-gen-ai-cn.github.io/training/weeks/week-02/day-3-pytest-and-numpy.html) · Demos: [demos/ticket-desk](https://github.com/2494-Gen-AI-CN/demos/tree/main/ticket-desk)

## Task

Build `starter/hours_report.py`, a small module that turns ticket durations into a NumPy array of hours, compares them with SLA limits in a single vectorised comparison to get a breach mask, and reports a count and a mean. Then write two tests of your own in `tests/test_mine.py`, so you practise reading and writing pytest checks for array results.

## Acceptance criteria

- [ ] `test_to_hours_is_float_array`: `to_hours` returns a float64 array of hours with the right shape
- [ ] `test_limits_for_maps_priorities`: `limits_for` returns the SLA hours per priority name
- [ ] `test_limits_for_unknown_priority_raises`: an unknown priority raises `ValueError` naming it
- [ ] `test_breach_mask_is_boolean_and_strict`: `breach_mask` gives a boolean array, `True` only when strictly above the limit
- [ ] `test_breach_count_is_plain_int`: `breach_count` returns a plain `int`
- [ ] `test_mean_hours_is_plain_float`: `mean_hours` returns a plain `float`
- [ ] `test_mean_hours_empty_is_zero`: an empty array gives `0.0`
- [ ] `tests/test_mine.py` holds two tests you wrote, both passing
- [ ] All tests pass: `python -m pytest -q`

## Getting started

Run these from your clone of the training repo. They copy this exercise into your own repository (`<FirstnameLastname>`, the one you created in the Week 1 Git exercise) at the same path, and you work in that copy. The paths assume the two repositories sit side by side; adjust `..` if yours do not.

```
git pull
mkdir -p ../<FirstnameLastname>/week-02/day-3-pytest-and-numpy
cp -r exercises/week-02/day-3-pytest-and-numpy/* ../<FirstnameLastname>/week-02/day-3-pytest-and-numpy/
cd ../<FirstnameLastname>/week-02/day-3-pytest-and-numpy
python -m pip install numpy==2.5.4 pytest==9.1.1
python -m pytest -q          # everything fails until you implement starter/hours_report.py
```

Implement the functions in `starter/hours_report.py` (each has a docstring and currently raises `NotImplementedError`). Run the tests as you go.

For your own two tests, create `tests/test_mine.py` starting with `from hours_report import breach_count, to_hours`, then add two functions whose names start with `test_`. Ideas: two tickets exactly at their limit give a count of `0`; `to_hours([7200])` has shape `(1,)`.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `week-02/day-3-pytest-and-numpy/` there.

## Hints

- Dividing a NumPy array by a number divides every element: `np.array([7200]) / 3600` gives `array([2.])`. No loop is needed.
- `array_a > array_b` compares element by element and returns a boolean array; `.sum()` on a boolean array counts the `True` values.
- NumPy results are `np.float64` or `np.int64`, not plain Python numbers; wrap them with `float(...)` or `int(...)` when the docstring asks for a plain one.
- Never write `assert array == [..]`; use `np.array_equal(array, [...])` or `np.allclose(...)` for floats, as in the tests here.
