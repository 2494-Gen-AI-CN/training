# Exercise - Review, Matplotlib and mini-project

Week 2 · Day 5 · `w02d5` · ~60–90 min · marked against a rubric (no automated tests)
Notes: [weeks/week-02/day-5-review-matplotlib-and-mini-project.html](https://2494-gen-ai-cn.github.io/training/weeks/week-02/day-5-review-matplotlib-and-mini-project.html) · Demos: [demos/week-02/day-5-review-matplotlib-and-mini-project](https://github.com/2494-Gen-AI-CN/demos/tree/main/week-02/day-5-review-matplotlib-and-mini-project)

## Task

Build `ticket-report/`, a small ticket-report codebase that pulls the whole fortnight together. It reads a JSON file of support tickets, with errors handled, and splits the work across modules. It computes the resolution hours with a NumPy array, loads the tickets into a pandas DataFrame, and draws a Matplotlib bar chart of tickets per status, saved as a PNG. It has pytest tests, including one that writes the chart into a temporary folder, and `pylint` runs over every file. You write the data file yourself (at least eight tickets, each with an `id`, a `priority` of `high`, `normal` or `low`, a `status` of `open`, `assigned` or `closed`, and `hours` set to a number for closed tickets and `null` for the rest). Choose your own module names and your own report; what is marked is the shape of the codebase, not a particular answer.

## Deliverable

Inside your own public `<FirstnameLastname>` repository in the cohort organisation (the one from the Week 1 Git exercise), the folder `week-02/day-5-review-matplotlib-and-mini-project/ticket-report/` pushed to `main`. It holds the Python modules, `tickets.json`, `test_*.py`, `requirements.txt` and `.gitignore`. Do not commit the generated `.png` or the `.venv/` folder. The commit history shows at least three commits made while you worked. No new repository and no personal-account repository.

## Acceptance criteria

- [ ] Structure: at least three `.py` modules besides the tests (for example loading, statistics, charting), plus a small entry script (for example `report.py`) guarded by `if __name__ == "__main__":`; running it with `python` from inside `ticket-report/` exits without an error and prints a report
- [ ] JSON and errors: tickets are read from `tickets.json` with `json`; a missing file and a corrupt file are each caught by name (`FileNotFoundError`, `json.JSONDecodeError`) and print a message instead of a traceback
- [ ] NumPy: the closed tickets' hours become a NumPy array, and at least one figure (mean, maximum or a count over a limit) is computed from the array without a Python loop
- [ ] pandas: the tickets load into a DataFrame, and a status count comes from the DataFrame (`value_counts` or `groupby`)
- [ ] Matplotlib: a function takes the DataFrame and a path, draws tickets per status with `fig, ax = plt.subplots()` and `ax.bar`, sets a title and both axis labels, saves a PNG, and closes the figure; running the entry script leaves the PNG on disk
- [ ] Tests: `pytest` passes with at least five tests, one of them writing the chart into `tmp_path` and asserting the file exists and is not empty, and one of them covering the missing-file or corrupt-file path
- [ ] Lint: `pylint` over every `.py` file reports no message other than ones named in a comment or the README (a fixture-parameter `W0621` is acceptable when named)
- [ ] Hygiene: `requirements.txt` pins the libraries with `==`, `.gitignore` lists `*.png` and `.venv/`, and the history has at least three commits whose messages name the change

## Rubric

| Criterion | Meets | Partial | Missing |
|---|---|---|---|
| Structure | 3+ non-test modules; entry script has the `__main__` guard, exits 0 and prints a report; each module's name matches the functions inside it | 2 modules, or one module holding both loading and charting code, or no `__main__` guard | One file holds everything |
| JSON and errors | `except FileNotFoundError` and `except json.JSONDecodeError` both present; a missing and a corrupt file each print a message and no `Traceback` | One of the two caught by name, or a bare `except:` / `except Exception` | A missing or corrupt file prints a `Traceback` |
| NumPy | `np.array` of closed hours, and a figure from `.mean()`, `.max()` or a comparison such as `(arr > 24).sum()` | Array built, but the figure comes from a `for` loop or `sum()` over a list | No `numpy` import |
| pandas | `pd.DataFrame` built from the file; status counts from `value_counts` or `groupby` | DataFrame built, but counts from a manual loop or `Counter` | No DataFrame |
| Matplotlib | `plt.subplots`, `ax.bar`, `set_title`, `set_xlabel`, `set_ylabel`, `savefig` and `plt.close(fig)` present; a non-empty PNG appears after a run | PNG saved, but a title or label is missing, or the figure is never closed | No PNG after a run, or `plt.show()` with no save |
| Tests | `pytest` reports 5+ passed, including a chart test in `tmp_path` and an error-path test | All pass, but fewer than 5, or the chart test or error-path test is absent | No tests, or any test fails |
| Lint | pylint prints no message, or each remaining message ID is named in a comment or the README | 1 to 5 messages not named anywhere | More than 5 unnamed messages |
| Hygiene | `==` pins in `requirements.txt`, `*.png` and `.venv/` in `.gitignore`, 3+ commits whose messages name the change | One of the three missing (for example messages like `update`) | Two or more missing, or a `.png` or `.venv/` committed |

## Getting started

The commands below work in both Windows PowerShell and Git Bash, except the activate step, where you run only the line for your shell. Run them from the folder that holds your clone of your own `<FirstnameLastname>` repository (not the training repo). Wherever you see `<FirstnameLastname>`, type your own repository's name without the angle brackets; `report.py` stands for your entry script, so use your own file's name.

```
cd <FirstnameLastname>
git pull
mkdir -p week-02/day-5-review-matplotlib-and-mini-project/ticket-report
cd week-02/day-5-review-matplotlib-and-mini-project/ticket-report
python -m venv .venv
.venv\Scripts\Activate.ps1          # PowerShell on Windows
source .venv/Scripts/activate       # Git Bash on Windows
source .venv/bin/activate           # macOS
# create requirements.txt and .gitignore in your editor (contents below), then:
python -m pip install -r requirements.txt
# write tickets.json, then your modules, then test_*.py
python report.py                    # use your own entry script's name
python -m pytest -q
python -m pylint --recursive=y --ignore=.venv .
git add .
git commit -m "Load tickets from JSON with error handling"
git push origin main
```

Once the environment is active, your prompt starts with `(.venv)`. If PowerShell refuses to run `Activate.ps1` because running scripts is disabled, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once in that window and try again.

`requirements.txt` (the versions the week's demos pinned):

```
matplotlib==3.11.2
numpy==2.5.4
pandas==3.0.6
pylint==4.0.0
pytest==9.1.1
```

`.gitignore`:

```
.venv/
__pycache__/
.pytest_cache/
*.png
```

The pylint line checks every `.py` file in the folder and its subfolders and skips `.venv`; without `--ignore=.venv` it would lint the installed libraries too. Commit after each step with a message that names what changed, then push.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `week-02/day-5-review-matplotlib-and-mini-project/ticket-report/` there.

## Hints

- Build in the order of the data: `tickets.json`, then the loader, then the NumPy figure, then the DataFrame, then the chart. Commit after each step.
- `json.load` raises `json.JSONDecodeError` on a corrupt file and `open` raises `FileNotFoundError` on a missing one; catch each by name, print a message, and decide what the function returns.
- `np.array(list_of_hours)` builds the array; `arr.mean()`, `arr.max()` and `(arr > 24).sum()` need no loop.
- `pd.DataFrame(tickets)` accepts a list of dicts; `df["status"].value_counts()` returns a Series whose `.index` and `.values` go straight into `ax.bar`.
- Test the chart without a window: `status_chart(df, tmp_path / "status.png")`, then `assert (tmp_path / "status.png").stat().st_size > 0`. To test an error path, write bad text to a file in `tmp_path` and use `pytest.raises` or check the returned message.
- pylint flags a test parameter that shares a fixture's name (`W0621`); that one may stay if you name it in a comment. Fix the rest.
