# Exercise - Collections and pandas

Week 2 · Day 4 · `w02d4` · Thu 2026-10-22 · ~60–90 min
Notes: [weeks/week-02/day-4-collections-and-pandas.html](https://2494-gen-ai-cn.github.io/training/weeks/week-02/day-4-collections-and-pandas.html) · Demos: [demos/ticket-desk](https://github.com/2494-Gen-AI-CN/demos/tree/main/ticket-desk)

## Task

Build `ticket_report.py`, a small reporting module for the ticket desk. Count tickets per status with `Counter`, give each ticket a named row type with `namedtuple`, keep an ordered work queue in an `OrderedDict`, group ticket ids per agent with a `defaultdict`, then load the same tickets from a JSON file into a pandas DataFrame and show that its status counts equal the `Counter`'s.

## Acceptance criteria

- [ ] `test_status_counts_is_counter`: `status_counts` returns a `Counter`, and a missing status counts 0
- [ ] `test_status_counts_empty`: an empty list gives an empty `Counter`
- [ ] `test_to_rows_are_named_tuples`: `to_rows` returns `TicketRow` values; a missing assignee becomes `None`
- [ ] `test_work_queue_order_and_type`: `work_queue` returns an `OrderedDict` ordered high, normal, low, then by id
- [ ] `test_work_queue_leaves_out_closed`: closed tickets are not in the queue
- [ ] `test_ids_by_agent_groups_and_skips_unassigned`: ids per assignee, unassigned left out, a plain `dict` returned
- [ ] `test_load_frame_reads_json`: `load_frame` returns a DataFrame with one row per ticket
- [ ] `test_status_table_matches_counter`: `status_table(df)` is a plain `dict` equal to `dict(status_counts(...))`
- [ ] All tests pass: `python -m pytest -q`

## Getting started

Run these from your clone of the training repo. They copy this exercise into your own repository (`<FirstnameLastname>`, the one you created in the Week 1 Git exercise) at the same path, and you work in that copy. The paths assume the two repositories sit side by side; adjust `..` if yours do not.

```
git pull
mkdir -p ../<FirstnameLastname>/week-02/day-4-collections-and-pandas
cp -r exercises/week-02/day-4-collections-and-pandas/* ../<FirstnameLastname>/week-02/day-4-collections-and-pandas/
cd ../<FirstnameLastname>/week-02/day-4-collections-and-pandas
python -m pip install pandas==3.0.6
python -m pytest -q          # everything fails until you implement starter/ticket_report.py
```

Implement the functions in `starter/ticket_report.py` (each has a docstring and currently raises `NotImplementedError`). Run the tests as you go.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `week-02/day-4-collections-and-pandas/` there.
When the tests pass, run these from `week-02/day-4-collections-and-pandas/` in your `<FirstnameLastname>` repository:

```
git add .
git commit -m "w02d4 exercise: ticket reports"
git push origin main
```

## Hints

- `Counter` takes any iterable: `Counter(t["status"] for t in tickets)`.
- A dict's `.get("assignee")` returns `None` when the key is missing, where `d["assignee"]` raises `KeyError`.
- `sorted(items, key=...)` accepts a function that returns a tuple; a dict such as `{"high": 0, "normal": 1, "low": 2}` turns a priority into a number to sort on.
- `defaultdict(list)` creates an empty list the first time a key is used, so `groups[name].append(x)` needs no check. Wrap the result in `dict(...)` before returning.
- `pd.read_json(path)` reads a JSON list of objects into a DataFrame; `df["status"].value_counts().to_dict()` gives a plain dict.
