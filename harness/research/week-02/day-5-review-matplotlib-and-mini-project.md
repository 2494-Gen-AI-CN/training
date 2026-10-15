# w02d5 — Review, Matplotlib & mini-project

gate: light
verified: 2026-10-15
week: 2 · Python advanced
day: 5 · review-matplotlib-and-mini-project

version-stamps:
  - python: 3.15 (verified 2026-10-15)
  - matplotlib: 3.11.2 (verified 2026-10-15)   # Python 3.15 wheel on PyPI: matplotlib-3.11.2-cp315-cp315-win_amd64.whl
  - pandas: 3.0.6 (verified 2026-10-15)   # Python 3.15 wheel on PyPI: pandas-3.0.6-cp315-cp315-win_amd64.whl
  - numpy: 2.5.4 (verified 2026-10-15)   # Python 3.15 wheel on PyPI: numpy-2.5.4-cp315-cp315-win_amd64.whl
  - pytest: 9.1.1 (verified 2026-10-15)

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- `matplotlib.pyplot.subplots()` returns a `(Figure, Axes)` pair; the Figure is the whole canvas and the Axes is one plot area drawn on it — [Matplotlib: Quick start guide](https://matplotlib.org/stable/users/explain/quick_start.html)
- `Axes.bar(x, height)` draws one bar per category, and `Axes.set_title`, `set_xlabel` and `set_ylabel` label the chart — [Axes.bar](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar.html)
- `Figure.savefig(path)` writes the figure to a file, and the format is chosen from the file extension, so `status.png` gives a PNG — [Figure.savefig](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.savefig.html)
- `plt.show()` opens a window and blocks until it is closed, so a script run unattended (a test, a scheduled job) must save to a file instead — [matplotlib.pyplot.show](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html)
- `plt.close(fig)` releases a figure; pyplot keeps every open figure in memory, and opening many without closing them raises a warning — [matplotlib.pyplot.close](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.close.html)
- `Figure.tight_layout()` adjusts padding so labels and titles are not clipped — [Figure.tight_layout](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.tight_layout.html)
- Matplotlib documents two interfaces: the explicit object-oriented one (`fig, ax = plt.subplots()`, then `ax.method()`) and the implicit pyplot one (`plt.bar(...)` acting on the "current" axes); the guide recommends the explicit form for anything beyond a quick sketch — [Matplotlib: Quick start guide](https://matplotlib.org/stable/users/explain/quick_start.html)
- `Axes.scatter(x, y, marker=, s=)` draws markers at points; a `"_"` marker with a large `s` renders as a short horizontal mark, usable as a per-bar reference line — [Axes.scatter](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.scatter.html)
- `Axes.legend()` builds a legend from the `label=` arguments of the artists already drawn — [Axes.legend](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.legend.html)
- `Series.map(dict)` replaces each value with the dict entry for that value, giving NaN for missing keys — [pandas.Series.map](https://pandas.pydata.org/docs/reference/api/pandas.Series.map.html)
- `Series.value_counts()` counts occurrences per distinct value and returns a Series indexed by the values, which can be passed straight to `ax.bar` — [pandas.Series.value_counts](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html)
- `Series.notna()` gives a boolean mask of non-missing values, used to filter a DataFrame to rows that have a value — [pandas.Series.notna](https://pandas.pydata.org/docs/reference/api/pandas.Series.notna.html)
- pytest's built-in `tmp_path` fixture gives each test a fresh temporary directory as a `pathlib.Path`, so a chart test never writes into the project — [pytest: tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
- A fixture is requested by naming it as a test parameter; pylint's W0621 (redefined-outer-name) fires on that pattern even though pytest relies on it — [pytest: About fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)
- `pathlib.Path.stat().st_size` returns a file's size in bytes, enough to assert a written file is not empty — [pathlib: Path.stat](https://docs.python.org/3/library/pathlib.html#pathlib.Path.stat)
- `git log --oneline -- .` lists commits that touched files under the current directory — [git-log](https://git-scm.com/docs/git-log)
- When the x values passed to a plotting call are strings that all parse as numbers or dates (for example `"1"`, `"2"`, `"3"`), Matplotlib still treats them as categories but logs an INFO message through the `matplotlib.category` logger: "Using categorical units to plot a list of strings that are all parsable as floats or dates. If these strings should be plotted as numbers, cast to the appropriate data type before plotting." A program whose root logger is configured at INFO (the desk's `logging.basicConfig(level=logging.INFO)`) prints that line; labels such as `"TD-1"` do not trigger it. Confirmed in matplotlib 3.11.2's `lib/matplotlib/category.py` (`StrCategoryConverter._validate_unit`/`update`) — [matplotlib/category.py source](https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/category.py), [Matplotlib: Plotting categorical variables](https://matplotlib.org/stable/gallery/lines_bars_and_markers/categorical_variables.html)
- pylint's R1705 `no-else-return` fires on an `else` (or `elif`) that follows a block ending in `return`; the message text is `Unnecessary "else" after "return", remove the "else" and de-indent the code inside it`, and the fix is to delete the `else:` and de-indent its body, which leaves behaviour unchanged. In a `try`/`except`/`else` whose `except` returns, pylint 4.0.0 raises it on the `else:` of the `try` — [pylint: no-else-return / R1705](https://pylint.readthedocs.io/en/stable/user_guide/messages/refactor/no-else-return.html)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Overview of data visualization
- Interview questions: Which chart type would you use for categories, for change over time, for a distribution, and why?; Why should a bar chart's value axis start at zero?; What makes a chart misleading, and how would you review a colleague's chart for it?
- Adjacent concept: Choosing a chart from the question being asked (comparison, trend, distribution, relationship) — it belongs here because the overview is a decision about which chart answers which question, made before any code.
- Trade-off or limit: Bars encode value by length, so truncating the axis exaggerates differences; lines imply continuity between points and so suit ordered data such as time, not unrelated categories — [Matplotlib: Quick start guide](https://matplotlib.org/stable/users/explain/quick_start.html)
- Recognise on sight: A bar chart whose y-axis starts at 95 rather than 0, or a line joining unrelated categories; also `df.plot(kind="bar")` as a one-line shortcut over Matplotlib.
- Claims:
  - A chart should carry one message, stated in its title, with labelled axes and units — [Matplotlib: Quick start guide](https://matplotlib.org/stable/users/explain/quick_start.html)
  - A bar chart suits comparing a value across discrete categories, a histogram a distribution of one numeric variable — [Matplotlib: Plot types](https://matplotlib.org/stable/plot_types/index.html)
  - A scatter plot shows the relationship between two numeric variables and each point is one observation — [Axes.scatter](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.scatter.html)
  - pandas offers plotting on Series and DataFrames through `.plot`, built on Matplotlib — [pandas: Chart visualization](https://pandas.pydata.org/docs/user_guide/visualization.html)
  - A chart that must be reproducible in a pipeline or test is saved to a file rather than shown on screen — [matplotlib.pyplot.show](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html)

### Matplotlib
- Interview questions: What are a Figure and an Axes?; What is the difference between the pyplot interface and the object-oriented interface?; Why do you call `plt.close(fig)` after saving, and what happens in a long-running program if you do not?
- Adjacent concept: Testing code that produces files — a chart function is checked by writing into `tmp_path` and asserting the file exists and is non-empty, which ties the library to the week's pytest habits.
- Trade-off or limit: `plt.show()` blocks until the window closes and needs a display, so it suits exploration but not scripts, tests or servers; `savefig` works anywhere — [matplotlib.pyplot.show](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html)
- Recognise on sight: `fig, ax = plt.subplots(figsize=(6, 4))` followed by `ax.bar(...)`, `ax.set_title(...)`, `fig.savefig("x.png")`; versus the older `plt.figure(); plt.bar(...); plt.show()` pyplot style.
- Claims:
  - `plt.subplots(figsize=(w, h))` sets the figure size in inches — [matplotlib.pyplot.subplots](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html)
  - Passing a pandas Series to `ax.bar` uses its index as labels and its values as heights when given as `counts.index, counts.values` — [Axes.bar](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar.html)
  - Each call to `plt.subplots()` creates a new, separate figure, so two chart functions should each create their own — [matplotlib.pyplot.subplots](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html)
  - Pin the version in `requirements.txt` (`matplotlib==3.11.2`) so every machine installs the same release — [pip: Requirements File Format](https://pip.pypa.io/en/stable/reference/requirements-file-format/)
  - `savefig` accepts a `dpi` argument that sets resolution for raster formats such as PNG — [Figure.savefig](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.savefig.html)
  - Generated images such as `*.png` are build outputs and belong in `.gitignore` rather than in version control — [gitignore](https://git-scm.com/docs/gitignore)

### Python review
- Interview questions: Walk me through how you would structure a small Python program into modules and why; How do you handle a missing or malformed input file, and what do you test?; What is the difference between a list, a NumPy array and a DataFrame column, and when would you reach for each?
- Adjacent concept: Reviewing a codebase as a team does (tests green, linter clean, small commits, a merged branch) — it belongs with the review because the mini-project is marked against that rubric.
- Trade-off or limit: A linter message is advice, not an error; the fixture-parameter W0621 is left and named because pytest requires that pattern, while most other messages are fixed — [pytest: About fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)
- Recognise on sight: `if __name__ == "__main__": main()` at the foot of a script; `try: ... except FileNotFoundError:` around a `json.load`; `def test_x(tmp_path, sample_desk):` in a test file.
- Claims:
  - `import` loads a module once and binds its name; a file that defines functions can be imported by another without running its `if __name__ == "__main__"` block — [Python tutorial: Modules](https://docs.python.org/3/tutorial/modules.html)
  - `try`/`except` catches a named exception class; catching a specific class such as `FileNotFoundError` is preferred over a bare `except` — [Python tutorial: Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
  - `json.load` parses a file object into dicts and lists and `json.dump` writes them back; a malformed file raises `json.JSONDecodeError` — [json module](https://docs.python.org/3/library/json.html)
  - A NumPy array holds items of one dtype and supports whole-array arithmetic without a Python loop — [NumPy: Quickstart](https://numpy.org/doc/stable/user/quickstart.html)
  - `pandas.DataFrame` is a two-dimensional labelled table, and `groupby` plus an aggregation summarises it by a column — [pandas: Intro to data structures](https://pandas.pydata.org/docs/user_guide/dsintro.html)
  - A list comprehension is a shorter form of a `for` loop that appends to a new list — [Python tutorial: List Comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
  - pytest discovers files named `test_*.py` and functions named `test_*`, and a bare `assert` reports the failing values — [pytest: Get started](https://docs.pytest.org/en/stable/getting-started.html)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Matplotlib: Quick start guide — https://matplotlib.org/stable/users/explain/quick_start.html
- Matplotlib: Plot types — https://matplotlib.org/stable/plot_types/index.html
- Matplotlib: Axes.bar — https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar.html
- Matplotlib: Figure.savefig — https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.savefig.html
- Matplotlib: pyplot.show — https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html
- Matplotlib: pyplot.subplots — https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
- pandas: Chart visualization — https://pandas.pydata.org/docs/user_guide/visualization.html
- pandas: Series.map — https://pandas.pydata.org/docs/reference/api/pandas.Series.map.html
- NumPy: Quickstart — https://numpy.org/doc/stable/user/quickstart.html
- pytest: tmp_path — https://docs.pytest.org/en/stable/how-to/tmp_path.html
- Python tutorial: Modules — https://docs.python.org/3/tutorial/modules.html
- Python tutorial: Errors and Exceptions — https://docs.python.org/3/tutorial/errors.html
- Python json module — https://docs.python.org/3/library/json.html
- Git: git-log — https://git-scm.com/docs/git-log
- Matplotlib: category.py source (categorical units INFO log) — https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/category.py
- Matplotlib: Plotting categorical variables — https://matplotlib.org/stable/gallery/lines_bars_and_markers/categorical_variables.html
- pylint: no-else-return / R1705 — https://pylint.readthedocs.io/en/stable/user_guide/messages/refactor/no-else-return.html

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- figure | The whole Matplotlib canvas that holds one or more plot areas and is what gets saved to an image file. | aka: Figure, plt.figure
- axes | One plot area inside a figure, with its own x and y axis, title, labels and drawn marks. | aka: Axes, ax, subplot
- data visualization | Turning data into a chart so that one comparison or trend can be seen at a glance. | aka: dataviz, charting, plotting
- bar chart | A chart that draws one bar per category with the bar's length showing its value. | aka: bar graph, bar plot
- DataFrame | A two-dimensional labelled table of columns, each holding values of one type, provided by pandas. | aka: data frame, DataFrames
- fixture | A pytest function that prepares something a test needs, such as sample data, and is passed in by naming it as a test parameter. | aka: fixtures, pytest fixture
- linter | A tool that reads source code without running it and reports style problems and likely mistakes. | aka: linting, pylint

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Leaving `plt.show()` in a script: it blocks waiting for a window, so an unattended run, a test or a remote shell hangs; save with `fig.savefig` and close the figure.
- Drawing the second chart on the first chart's figure (using `plt.bar` on the "current" axes, or skipping `plt.subplots()`), which stacks both charts into one image; each chart function creates its own figure and calls `plt.close(fig)`.
- Calling `savefig` after `plt.show()` and getting a blank image, or saving before titles and labels are set; save last, once the chart is complete.
- Committing `status.png` and `hours.png`, or forgetting `*.png` in `.gitignore`, so generated files appear in every `git status`.
- Truncated or unlabelled axes: a bar chart whose axis does not start at zero, or with no title, axis labels or legend, so the chart cannot be read on its own.
- Mini-project scope slide: starting with the chart instead of the load-and-test spine, then finishing with no tests, a failing pylint run or an unmerged branch, all of which the rubric marks.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Run `python ticket_desk.py`, then open `status.png` and compare each bar with the status table the DataFrame printed, so the chart is visibly the same numbers.
- Type `plt.show()` once, show the window blocking the terminal, close it, then delete the line and rely on `savefig` and `plt.close(fig)`.
- In `hours_chart`, show that `.map(SLA_HOURS)` gives each bar its own ticket's limit, and count the bars rising past a black mark against the breach count `summary()` prints.
- Run `pytest` with `test_charts_write_png` green, deliberately point one path at a missing folder to see it fail, then finish with pylint, the merge to `main`, `git push origin main` and `git log --oneline -- .`.
