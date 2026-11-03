# w05d4 — AI tooling: optimization, analysis & security

gate: full
verified: 2026-11-03
week: 5 · Gen AI introduction
day: 4 · ai-tooling-review-and-security

version-stamps:
  - python: 3.15 (verified 2026-11-03)
  - pandas: 3.0.6 (verified 2026-11-03) — pandas-3.0.6-cp315-cp315-win_amd64.whl; the desk's pin in `ticket-desk/requirements.txt` at 55f65d7; latest on PyPI is 3.1.0 and the live docs pages are the 3.1.0 build (the behaviour cited below is unchanged between them and was run under 3.0.6 on `py`)
  - mysql-connector-python: 26.7.0 (verified 2026-11-03) — mysql_connector_python-26.7.0-py2.py3-none-any.whl; the desk's pin; latest on PyPI is 26.10.0; the connection-arguments page (current build) still lists `ssl_disabled` default `False` and `ssl_verify_cert` default `False`
  - pytest: 9.1.1 (verified 2026-11-03) — pytest-9.1.1-py3-none-any.whl; the desk's pin; latest 9.2.0
  - pylint: 4.0.0 (verified 2026-11-03) — pylint-4.0.0-py3-none-any.whl; the desk's pin; latest 4.1.3 (C0116 `missing-function-docstring` unchanged)
  - bandit: 1.9.4 (verified 2026-11-03) — bandit-1.9.4-py3-none-any.whl; latest on PyPI (2026-02-25); not a desk dependency, installed in a scratch venv on `py` 3.15 only to check which planted lines it flags; no page asks a learner to install it
  - LLM config: `claude-haiku-4-5` (verified 2026-11-03) — FLAG: the Models overview lists Claude Haiku 4.5 under "Legacy models (still available)"; the current Haiku is `claude-haiku-5-5` (the Models overview's Compare models table, Claude Haiku 5.5 column, reads "Claude API ID | `claude-haiku-5-5`" and "Claude API alias | `claude-haiku-5-5`", retirement "Not sooner than October 7, 2027"; its closing line reads "Legacy models (still available): ... Claude Haiku 4.5" — [Models overview (Claude Platform docs)](https://platform.claude.com/docs/en/about-claude/models/overview)). No page, runbook or task this week calls an API, so nothing breaks; update the week-6 config before any call is made
  - DEPRECATION FLAG (Python 3.15): the pure-Python `profile` module is deprecated in 3.15 (removal in 3.17); 3.15 adds the `profiling` package (`profiling.tracing`, with `cProfile` kept as an alias, and `profiling.sampling`). If the optimisation step names a profiler, name `profiling`, never `import profile`
  - PRODUCT RENAME FLAG (Windsurf): `windsurf.com` now 308-redirects to `devin.ai/desktop`, whose FAQ says "Devin Desktop is the new name for Windsurf"; `docs.windsurf.com` 307-redirects into `docs.devin.ai`; the Windsurf JetBrains plugin page says it "is in maintenance mode". The plan's convention "Codeium (now Windsurf)" is a stale chain; suggested wording: "Codeium (later Windsurf, now Devin Desktop)", cited from [Devin Desktop](https://devin.ai/desktop) and [Welcome to Windsurf Plugins](https://docs.devin.ai/windsurf/plugins/getting-started). Name it at most once, as the category example; never as a tool a learner must open

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- Refactoring restructures existing code, "altering its internal structure without changing its external behavior" — [Refactoring (Martin Fowler)](https://refactoring.com/)
- In pandas, `None == None` is `True` but `np.nan == np.nan` is `False`; an equality comparison against a missing value "does not provide the same information as `isna()`", so missing values are tested with `isna()` — [Working with missing data (pandas)](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- Run under pandas 3.0.6 on `py` (2026-11-03): two `str` Series `[None, "CA"]` compared with `==` give `[False, True]`, so a `merge`-then-compare rewrite of `apply_scd2` sees an unchanged missing tracked value as changed, while the loop's plain `None == None` is `True` — [Working with missing data (pandas)](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- `DataFrame.merge(how="left")` keeps every left key ("similar to a SQL left outer join"), filling the right side's columns with `NaN`; overlapping column names get the suffixes `_x` and `_y` by default; `indicator=True` adds a `_merge` column of `left_only`, `right_only`, `both` — [pandas.DataFrame.merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)
- Run under pandas 3.0.6: after `events.merge(tickets, how="left")`, an event whose `ticket_id` has no ticket gets `opened_at` `NaT`, and `created_at < opened_at` is `False`, so `clean_events` passes it as clean — [pandas.DataFrame.merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)
- `DataFrame.duplicated` defaults to `keep="first"`: "Mark duplicates as True except for the first occurrence"; only `keep=False` marks every copy — [pandas.DataFrame.duplicated](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html)
- MySQL "rejects any INSERT or UPDATE operation that attempts to create a foreign key value in a child table if there is no matching candidate key value in the parent table", and `ON DELETE CASCADE` deletes the matching child rows with the parent, so `ticket_events` holds no orphan at the source — [FOREIGN KEY Constraints (MySQL 8.4 Reference Manual)](https://dev.mysql.com/doc/refman/8.4/en/create-table-foreign-keys.html)
- pylint C0116 `missing-function-docstring` is "Used when a function or method has no docstring" — [missing-function-docstring / C0116 (Pylint)](https://pylint.readthedocs.io/en/stable/user_guide/messages/convention/missing-function-docstring.html)
- `cursor.execute(operation, params)` binds the values in the tuple or dict `params` "to the variables in the operation", written `%s` or `%(name)s`; a one-value tuple needs its comma, `('abc',)` — [MySQLCursor.execute() (MySQL Connector/Python)](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html)
- Parameterised queries "define the SQL structure separately from its data values"; "parameter markers represent data values, not table names, column names, or SQL keywords", so an identifier is fixed in code or mapped from an allow-list — [SQL Injection Prevention Cheat Sheet (OWASP)](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- CWE-89 is "Improper Neutralization of Special Elements used in an SQL Command": the product builds an SQL command from externally influenced input — [CWE-89 (MITRE)](https://cwe.mitre.org/data/definitions/89.html)
- OWASP's LLM05:2025 Improper Output Handling lists "LLM-generated SQL queries are executed without proper parameterization, leading to SQL injection" and advises treating the model as a user (zero trust) and using parameterised queries — [LLM05:2025 Improper Output Handling (OWASP GenAI)](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/)
- Connector/Python "attempts to establish a secure (encrypted) connection by default" when the server supports TLS; `ssl_disabled=True` "disables SSL/TLS usage"; `ssl_verify_cert` already defaults to `False` — [Connector/Python Connection Arguments (MySQL)](https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html)
- CWE-798 Use of Hard-coded Credentials: "The product contains hard-coded credentials, such as a password or cryptographic key." — [CWE-798 (MITRE)](https://cwe.mitre.org/data/definitions/798.html)
- `os.environ` is a mapping of the process environment; `os.getenv(key, default=None)` returns the default when the variable is missing (so a default string in `.get` is a fallback the code uses silently, while `os.environ["KEY"]` raises `KeyError` by mapping semantics) — [os — Miscellaneous operating system interfaces (Python)](https://docs.python.org/3/library/os.html)
- CWE-1188 Initialization of a Resource with an Insecure Default; CWE-489 Active Debug Code: "The product is released with debugging code still enabled or active." — [CWE-1188 (MITRE)](https://cwe.mitre.org/data/definitions/1188.html), [CWE-489 (MITRE)](https://cwe.mitre.org/data/definitions/489.html)
- Logging levels: `DEBUG` 10, `INFO` 20, `WARNING` 30; `basicConfig(level=...)` sets the root logger's level, and the root logger starts at `WARNING` — [logging (Python)](https://docs.python.org/3/library/logging.html)
- CWE-532 Insertion of Sensitive Information into Log File: "The product writes sensitive information to a log file"; OWASP lists PII, passwords, access tokens and database connection strings among data that "should usually not be recorded directly in the logs" — [CWE-532 (MITRE)](https://cwe.mitre.org/data/definitions/532.html), [Logging Cheat Sheet (OWASP)](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- CWE-319 Cleartext Transmission of Sensitive Information: data sent in cleartext "in a communication channel that can be sniffed by unauthorized actors" — [CWE-319 (MITRE)](https://cwe.mitre.org/data/definitions/319.html)
- Bandit's B608 `hardcoded_sql_expressions` "looks for strings that resemble SQL statements that are involved in some form of string building operation"; B106 "looks for all function calls being passed a keyword argument that is a string literal" whose name is password-like — [B608: hardcoded_sql_expressions (Bandit)](https://bandit.readthedocs.io/en/latest/plugins/b608_hardcoded_sql_expressions.html), [B106: hardcoded_password_funcarg (Bandit)](https://bandit.readthedocs.io/en/latest/plugins/b106_hardcoded_password_funcarg.html)
- Run with Bandit 1.9.4 on `py` 3.15 (2026-11-03, `bandit -l -i`, every severity and confidence) against a mock `export_tickets.py` holding the five planted lines: only B608 fires (Medium/Medium, the f-string query, also when the f-string is split over three lines); `password=os.environ.get("DESK_DB_PASSWORD", "deskapp")`, `ssl_disabled=True`, `logging.basicConfig(level=logging.DEBUG)` and the logged row raise nothing; a control copy with `password="deskapp"` does raise B106. So Bandit finds one of the five, and an empty Bandit report is not a clean review — [B608: hardcoded_sql_expressions (Bandit)](https://bandit.readthedocs.io/en/latest/plugins/b608_hardcoded_sql_expressions.html), [B106: hardcoded_password_funcarg (Bandit)](https://bandit.readthedocs.io/en/latest/plugins/b106_hardcoded_password_funcarg.html)
- OWASP LLM09:2025 Misinformation: "Overreliance occurs when users place excessive trust in LLM-generated content, failing to verify its accuracy"; a model "suggests insecure or non-existent code libraries", and attackers publish packages under commonly hallucinated names — [LLM09:2025 Misinformation (OWASP GenAI)](https://genai.owasp.org/llmrisk/llm092025-misinformation/)
- GitHub's Copilot Chat card: generated code "may generate code that appears valid but is not semantically or syntactically correct", "can potentially expose sensitive information or vulnerabilities if not reviewed carefully", users "are responsible for reviewing and validating responses", and training data "may contain biases and errors that can be perpetuated by the tool" — [Application card: GitHub Copilot Chat](https://docs.github.com/en/copilot/responsible-use/chat-in-your-ide)
- Copilot's best practices: review suggestions for functionality and security, readability and maintainability, and add linting and code scanning; it is strong at "Writing tests and repetitive code" — [Best practices for using GitHub Copilot](https://docs.github.com/en/copilot/get-started/best-practices)
- GitHub's own feature overview splits Copilot into "Assistive" ("Copilot responds while you work, suggesting code, answering questions, or explaining code") and "Agentic" ("You describe a goal, and Copilot can work through multiple steps") — [About GitHub Copilot features (GitHub Docs)](https://docs.github.com/en/copilot/get-started/features)
- Copilot code referencing checks a suggestion against "code in public repositories on GitHub.com" and, by policy, blocks matches or shows them with "licensing information, if found" — [GitHub Copilot code referencing](https://docs.github.com/en/copilot/concepts/completions/code-referencing)
- MIT is "a short and simple permissive license with conditions only requiring preservation of copyright and license notices"; GPLv3 is a "strong copyleft license" whose conditions include disclose source and same license — [Licenses (choosealicense.com)](https://choosealicense.com/licenses/); the OSI texts: MIT grants the right "to deal in the Software without restriction" provided "The above copyright notice and this permission notice shall be included in all copies or substantial portions", and GPLv3 "is a free, copyleft license" whose section 5(c) reads "You must license the entire work, as a whole, under this License to anyone who comes into possession of a copy" — [The MIT License (Open Source Initiative)](https://opensource.org/license/mit), [GNU General Public License version 3 (Open Source Initiative)](https://opensource.org/license/gpl-3-0)
- Copyleft requires "all modified and extended versions of the program to be free as well" — [What is Copyleft? (GNU)](https://www.gnu.org/licenses/copyleft.en.html)
- The U.S. Copyright Office (Part 2, Jan 29 2025): outputs are protected "only where a human author has determined sufficient expressive elements", including creative arrangements or modifications, "but not the mere provision of prompts"; Part 3 (training) exists only as a pre-publication version (May 9 2025) — [NewsNet 1060 (U.S. Copyright Office)](https://www.copyright.gov/newsnet/2025/1060.html), [Copyright and Artificial Intelligence (U.S. Copyright Office)](https://www.copyright.gov/ai/)
- Anthropic's consumer terms (effective Oct 8 2025): "we assign to you all of our right, title, and interest—if any—in Outputs"; "Outputs may not always be accurate" and should not be relied on "without independently confirming their accuracy" — [Consumer Terms of Service (Anthropic)](https://www.anthropic.com/legal/consumer-terms)
- A profile "is a set of statistics that describes how often and for how long various parts of a program execute"; profilers are not for benchmarking, which is `timeit`'s job; `profiling` is new in 3.15 — [profiling — Python profilers](https://docs.python.org/3/library/profiling.html), [timeit (Python)](https://docs.python.org/3/library/timeit.html)
- NIST's AI RMF 1.0 (Jan 26 2023) is voluntary; its Generative AI Profile NIST-AI-600-1 (Jul 26 2024) helps organisations "identify unique risks posed by generative AI" — [AI Risk Management Framework (NIST)](https://www.nist.gov/itl/ai-risk-management-framework)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Code optimization
- Interview questions: You ask an assistant to make a function faster. What do you check before you accept the rewrite, and why do the tests come first? (qc3.genai-in-development.P03); What is refactoring, and how would you prove a refactor kept the behaviour? (qc3.genai-in-development.P03); Follow-up (a level beyond): the existing tests pass against the faster version, yet it is wrong. How can that happen, and what test do you add? (qc3.genai-in-development.R08)
- Adjacent concept: Measure before optimising — an interviewer asks how you know a function is slow at all; a profiler shows where time goes and `timeit` times a small snippet, which is what makes "worth it at six tickets or at 100,000 rows" a measured answer rather than a guess.
- Trade-off or limit: a vectorised pandas rewrite can change semantics at the edges (missing values compare unequal, `None == None` is `True` in Python but a missing value is never equal to itself in a pandas comparison) — [Working with missing data (pandas)](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- Recognise on sight: `merged[f"{col}_x"] != merged[f"{col}_y"]` used as "changed" without an `isna()` guard; a refactor diff that touches tests in the same commit; "this is faster" with no timing shown. Desk note (repo file, not a web source): `ticket-desk/sql/schema.sql` at 55f65d7 declares `name`, `email`, `country` (`CHAR(2) NOT NULL DEFAULT 'CA'`) and `monthly_fee` (`NOT NULL DEFAULT 0`) NOT NULL, so the divergence is latent on the desk and live on any nullable source (P0's dataset of 100,000 rows or more).
- Claims:
  - A refactor is a behaviour-preserving change to internal structure — [Refactoring (Martin Fowler)](https://refactoring.com/)
  - Copilot Chat "can suggest ways to speed up slow-running code" (the vendor names optimisation as a use, and its card says output must be reviewed) — [Refactor code (GitHub Docs)](https://docs.github.com/en/copilot/tutorials/refactor-code)
  - `merge` on a key aligns two frames row by row and suffixes overlapping columns `_x` and `_y` — [pandas.DataFrame.merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)
  - Use `isna()`/`notna()` to test for missing values; `==` does not — [Working with missing data (pandas)](https://pandas.pydata.org/docs/user_guide/missing_data.html)
  - A profile shows how often and how long parts of a program run; benchmark small snippets with `timeit` — [profiling — Python profilers](https://docs.python.org/3/library/profiling.html)

### Code analysis
- Interview questions: An assistant reviews your function and returns three findings. How do you decide which to act on? (qc3.genai-in-development.R08); What would you check to judge a generated change for correctness, maintainability and security? (qc3.genai-in-development.R08); How do you use an assistant to analyse unfamiliar code, and what are the best practices? (qc3.genai-in-development.P03); Follow-up (a level beyond): a finding is true but the case it describes cannot happen at the source. Do you still act on it, and how? (qc3.genai-in-development.R08)
- Adjacent concept: Static analysis tools (pylint, Bandit) against an assistant's review — a linter's rule is deterministic and repeatable, an assistant's review is not, so a team keeps both and settles disagreements with the docs and a test.
- Trade-off or limit: an assistant's explanation "may not always be accurate or complete and should be reviewed" — [Application card: GitHub Copilot Chat](https://docs.github.com/en/copilot/responsible-use/chat-in-your-ide)
- Recognise on sight: a review finding that states library behaviour ("`duplicated` marks the first copy too") with no doc link; a style suggestion that contradicts the team's lint config ("drop the docstring").
- Claims:
  - `duplicated` marks every copy after the first by default; the review's claim is false and the doc settles it — [pandas.DataFrame.duplicated](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html)
  - A left merge keeps unmatched left rows with missing right columns, so an orphan event carries `NaT` and passes `created_at < opened_at` — [pandas.DataFrame.merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)
  - MySQL's foreign key with `ON DELETE CASCADE` prevents orphans at the source; an orphan reaches `clean_events` only through staging (`etl.run` exports `tickets` before reading events, `desk_raw.ticket_events` is appended to and `desk_raw.tickets` is reloaded) — [FOREIGN KEY Constraints (MySQL 8.4)](https://dev.mysql.com/doc/refman/8.4/en/create-table-foreign-keys.html)
  - Dropping a one-line docstring brings back pylint C0116 — [missing-function-docstring / C0116 (Pylint)](https://pylint.readthedocs.io/en/stable/user_guide/messages/convention/missing-function-docstring.html)
  - Review generated code for functionality, security, readability and maintainability, backed by linting and code scanning — [Best practices for using GitHub Copilot](https://docs.github.com/en/copilot/get-started/best-practices)

### Security risks
- Interview questions: What security risks come with using generated code: code injection, insecure defaults and data leakage? Give one example of each and its fix (qc3.genai-in-development.R07); Why is an f-string in a SQL query dangerous when the value comes from a user, and what replaces it? (qc3.genai-in-development.R07); Name insecure patterns you look for in any generated code, and how you mitigate each (qc3.genai-in-development.S01); Follow-up (a level beyond): `extract.read_table` also builds `f"SELECT * FROM {table}"`. Why is that acceptable there and not in the generated file? (qc3.genai-in-development.S01)
- Adjacent concept: Defence in depth for generated code — parameter binding, least privilege on the database account and a secrets source outside the code each limit the damage when one check is missed; least privilege is in the glossary from week 3.
- Trade-off or limit: binding treats input as data but does not decide whether a user may see the rows; identifiers cannot be bound and need an allow-list — [SQL Injection Prevention Cheat Sheet (OWASP)](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- Recognise on sight: `cursor.execute(f"... WHERE t.status = '{status}'")`; `os.environ.get("DESK_DB_PASSWORD", "deskapp")`; `ssl_disabled=True`; `logging.basicConfig(level=logging.DEBUG)`; `log.info(row)` on a row holding `email`.
- Claims:
  - `execute` binds `params` to `%s` placeholders; a one-value tuple needs the comma — [MySQLCursor.execute()](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html)
  - Model-generated SQL run without parameterisation is OWASP's example of improper output handling — [LLM05:2025 Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/)
  - Hard-coded credentials are CWE-798 — [CWE-798](https://cwe.mitre.org/data/definitions/798.html)
  - The connector negotiates TLS by default; `ssl_disabled=True` turns it off; deleting `ssl_verify_cert=False` would change nothing because it is already the default — [Connector/Python Connection Arguments](https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html)
  - Writing sensitive data to a log is CWE-532; PII and passwords belong out of logs — [CWE-532](https://cwe.mitre.org/data/definitions/532.html), [Logging Cheat Sheet (OWASP)](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

### Responsible use
- Interview questions: What are the limitations, risks and ethical considerations of AI-assisted development? (qc3.genai-in-development.P04); Who owns code an assistant generates, and what licence risk does it carry? (qc3.genai-in-development.P06); Your client's contract forbids sending its data out. What may you paste into a public chat? (qc3.genai-in-development.P04); Follow-up (a level beyond): a suggestion matches a GPL-licensed repository. What happens if you ship it in closed-source client code? (qc3.genai-in-development.P06)
- Adjacent concept: Overreliance and the skills a junior builds by hand — the interviewer's next question after "what are the risks" is how you stay able to judge the output; notes step 5 covers ethics and step 6 the legal side.
- Trade-off or limit: provider terms assign the output to the user only "if any" rights exist, and copyright protects only sufficient human expressive choices, so ownership of purely generated code is uncertain — [Consumer Terms of Service (Anthropic)](https://www.anthropic.com/legal/consumer-terms), [NewsNet 1060 (U.S. Copyright Office)](https://www.copyright.gov/newsnet/2025/1060.html)
- Recognise on sight: a pull request description with no mention that a block was generated; a long suggestion that reads like a known library's file; a generated customer reply that assumes a customer's country or role.
- Claims:
  - Copilot's card names bias from training data and puts review on the user — [Application card: GitHub Copilot Chat](https://docs.github.com/en/copilot/responsible-use/chat-in-your-ide)
  - Overreliance is placing excessive trust in output without verification — [LLM09:2025 Misinformation (OWASP GenAI)](https://genai.owasp.org/llmrisk/llm092025-misinformation/)
  - A permissive licence (MIT) asks only for the notice; a copyleft licence (GPLv3) requires source disclosure under the same licence — [The MIT License (Open Source Initiative)](https://opensource.org/license/mit), [GNU General Public License version 3 (Open Source Initiative)](https://opensource.org/license/gpl-3-0), [Licenses (choosealicense.com)](https://choosealicense.com/licenses/), [What is Copyleft? (GNU)](https://www.gnu.org/licenses/copyleft.en.html)
  - Code referencing can block or flag suggestions that match public code, with licence information — [GitHub Copilot code referencing](https://docs.github.com/en/copilot/concepts/completions/code-referencing)
  - Prompts alone do not make the user an author; training-data copyright is still an open question (Part 3 is a pre-publication report) — [Copyright and Artificial Intelligence (U.S. Copyright Office)](https://www.copyright.gov/ai/)
  - NIST's Generative AI Profile is a voluntary framework for identifying generative AI risks, a source a client's AI policy may cite — [AI Risk Management Framework (NIST)](https://www.nist.gov/itl/ai-risk-management-framework)

### AI tooling review
- Interview questions: Compare AI-assisted development with traditional development: when is each more effective and more appropriate? (qc3.genai-in-development.S02); Which tasks would you give an assistant, which with review, and which by hand? (qc3.genai-in-development.S02); Follow-up (a level beyond): the assisted version was faster to write. Why might it still cost the team more? (qc3.genai-in-development.S02)
- Adjacent concept: Total cost of a change — writing time is only part; review, defects found later, what the developer learned and who can maintain it decide the comparison (the `ticket_age_band` off-by-one from Wednesday is the worked case).
- Trade-off or limit: assistants are strong at tests and repetitive code and are a tool, "rather than a replacement for human programming" — [Best practices for using GitHub Copilot](https://docs.github.com/en/copilot/get-started/best-practices), [Application card: GitHub Copilot Chat](https://docs.github.com/en/copilot/responsible-use/chat-in-your-ide)
- Recognise on sight: a decision table with three columns (use an assistant, use it with review, do it by hand) and rows such as boilerplate tests, a regular expression, a security-sensitive query, a schema change. Course convention (week plan "products as examples", no external source): the page teaches four categories, chat assistant, editor assistant, agentic coding tool (a category only; week 10 teaches agents) and API access, and names products only as examples.
- Claims:
  - A vendor draws the same line the course's categories draw: Copilot's "Assistive" side "responds while you work, suggesting code, answering questions, or explaining code", its "Agentic" side takes a goal and "can work through multiple steps" — [About GitHub Copilot features (GitHub Docs)](https://docs.github.com/en/copilot/get-started/features)
  - Windsurf's editor was renamed Devin Desktop ("Devin Desktop is the new name for Windsurf"); its JetBrains plugin is in maintenance mode — [Devin Desktop](https://devin.ai/desktop), [Welcome to Windsurf Plugins](https://docs.devin.ai/windsurf/plugins/getting-started)
  - Traditional static analysis is deterministic but narrow: Bandit's B608 "looks for strings that resemble SQL statements that are involved in some form of string building operation" and, run (Bandit 1.9.4) on a mock `export_tickets.py`, flags the f-string query and nothing else of the five planted issues, so a human (or assisted) review still has to find the other four — [B608: hardcoded_sql_expressions (Bandit)](https://bandit.readthedocs.io/en/latest/plugins/b608_hardcoded_sql_expressions.html)
  - A model can suggest non-existent libraries, and hallucinated package names are a supply-chain attack path, so the docs check stays in both workflows — [LLM09:2025 Misinformation (OWASP GenAI)](https://genai.owasp.org/llmrisk/llm092025-misinformation/)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Refactoring (Martin Fowler) — https://refactoring.com/
- Working with missing data (pandas 3.1.0 docs) — https://pandas.pydata.org/docs/user_guide/missing_data.html
- pandas.DataFrame.merge — https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html
- pandas.DataFrame.duplicated — https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html
- FOREIGN KEY Constraints (MySQL 8.4 Reference Manual) — https://dev.mysql.com/doc/refman/8.4/en/create-table-foreign-keys.html
- missing-function-docstring / C0116 (Pylint 4.1.3 docs) — https://pylint.readthedocs.io/en/stable/user_guide/messages/convention/missing-function-docstring.html
- MySQLCursor.execute() (MySQL Connector/Python) — https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html
- Connector/Python Connection Arguments — https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html
- SQL Injection Prevention Cheat Sheet (OWASP) — https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- Logging Cheat Sheet (OWASP) — https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- OWASP Top 10 for LLM Applications 2025 — https://genai.owasp.org/llm-top-10/
- LLM05:2025 Improper Output Handling — https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/
- LLM09:2025 Misinformation — https://genai.owasp.org/llmrisk/llm092025-misinformation/
- CWE-89 — https://cwe.mitre.org/data/definitions/89.html
- CWE-798 — https://cwe.mitre.org/data/definitions/798.html
- CWE-1188 — https://cwe.mitre.org/data/definitions/1188.html
- CWE-489 — https://cwe.mitre.org/data/definitions/489.html
- CWE-532 — https://cwe.mitre.org/data/definitions/532.html
- CWE-319 — https://cwe.mitre.org/data/definitions/319.html
- logging (Python 3 docs) — https://docs.python.org/3/library/logging.html
- os (Python 3 docs) — https://docs.python.org/3/library/os.html
- profiling — Python profilers (new in 3.15) — https://docs.python.org/3/library/profiling.html
- profile (Python 3 docs; deprecated in 3.15) — https://docs.python.org/3/library/profile.html
- timeit (Python 3 docs) — https://docs.python.org/3/library/timeit.html
- Bandit test plugins (Bandit 1.9.4 run on `py` 3.15) — https://bandit.readthedocs.io/en/latest/plugins/index.html
- B608: hardcoded_sql_expressions (Bandit) — https://bandit.readthedocs.io/en/latest/plugins/b608_hardcoded_sql_expressions.html
- B106: hardcoded_password_funcarg (Bandit) — https://bandit.readthedocs.io/en/latest/plugins/b106_hardcoded_password_funcarg.html
- Application card: GitHub Copilot Chat — https://docs.github.com/en/copilot/responsible-use/chat-in-your-ide
- Best practices for using GitHub Copilot — https://docs.github.com/en/copilot/get-started/best-practices
- About GitHub Copilot features (GitHub Docs) — https://docs.github.com/en/copilot/get-started/features
- Refactor code (GitHub Docs) — https://docs.github.com/en/copilot/tutorials/refactor-code
- GitHub Copilot code referencing — https://docs.github.com/en/copilot/concepts/completions/code-referencing
- Devin Desktop (formerly Windsurf) — https://devin.ai/desktop
- Welcome to Windsurf Plugins — https://docs.devin.ai/windsurf/plugins/getting-started
- The MIT License (Open Source Initiative) — https://opensource.org/license/mit
- GNU General Public License version 3 (Open Source Initiative) — https://opensource.org/license/gpl-3-0
- Licenses (choosealicense.com; secondary, maintained by GitHub) — https://choosealicense.com/licenses/
- What is Copyleft? (GNU) — https://www.gnu.org/licenses/copyleft.en.html
- Copyright and Artificial Intelligence (U.S. Copyright Office) — https://www.copyright.gov/ai/
- NewsNet 1060: Copyright Office Releases Part 2 — https://www.copyright.gov/newsnet/2025/1060.html
- Consumer Terms of Service (Anthropic) — https://www.anthropic.com/legal/consumer-terms
- AI Risk Management Framework (NIST) — https://www.nist.gov/itl/ai-risk-management-framework
- Models overview (Claude Platform docs) — https://platform.claude.com/docs/en/about-claude/models/overview
- Not citable (fetch refused, HTTP 403): https://openai.com/policies/terms-of-use/ and https://openai.com/policies/row-terms-of-use/ — do not quote OpenAI's terms from this brief

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- code injection | An attack where input a program trusts is run as part of a command, such as user text pasted into an SQL string. | aka: SQL injection, injection attack
- hard-coded credential | A password, key or token written into the source code, so anyone who reads the code or its history can use it. | aka: hardcoded password, hard-coded secret
- insecure default | A setting that ships switched to the unsafe choice and stays that way unless someone changes it. | aka: unsafe default, insecure defaults
- refactoring | Changing how code is written inside without changing what it does from the outside. | aka: refactor, refactored
- copyleft | A licence rule that anyone who shares a changed version of the code must share it under the same licence with its source. | aka: copyleft licence, copyleft license, GPL
- permissive licence | An open-source licence that lets anyone reuse the code, even in closed products, as long as the notice is kept. | aka: permissive license, MIT license
- static analysis | Checking code for bugs and risky patterns by reading it with a tool, without running it. | aka: static analyser, SAST, Bandit
- overreliance | Trusting a model's output so much that it is used without being checked. | aka: over-reliance, automation bias

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Accepting the "faster" `apply_scd2` because week 4's three tests pass: the tests guard only their fixtures, which hold no missing value, so pairs stop before writing the missing-value copy of `test_rerun_after_change_adds_nothing`.
- Taking a confident review finding as fact: learners accept "`duplicated` marks the first copy too" without opening the pandas page (default `keep="first"`), and dismiss the true `how="left"` orphan finding because MySQL's foreign key forbids orphans at the source, missing that staging can still produce one.
- Fixing the injection by quoting or escaping the status inside the f-string, or by "validating" it, instead of a `%s` placeholder with `(status,)`; and forgetting the comma in a one-value tuple.
- Treating `os.environ.get("DESK_DB_PASSWORD", "deskapp")` as safe because it "reads an environment variable": the fallback is the real `desk_app` password and the code runs, and leaks it, with no variable set; and replacing `ssl_disabled=True` with `ssl_verify_cert=False`, which is already the default.
- Thinking a debug log is harmless because it is "only local": a `DEBUG` level plus logging whole joined rows writes `customers.email` (dana@example.com) to a file that is shared, shipped or committed.
- Believing that because the provider's terms "assign the output to you", the code is free of licence and copyright questions: the assignment is of rights "if any", and a suggestion matching GPL code carries that licence's conditions.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- (demoFormat none: nothing typed on the desk.) The critical-evaluation checklist on the board (does it run, does it meet the requirement, is it tested, can the team maintain it, is it safe, is the claim in the docs) used to sort the three `clean_events` findings, with the `duplicated` doc line and the MySQL foreign-key line printed in the pair pack.
- The `apply_scd2` divergence settled on paper with the pandas missing-data lines printed (`None == None` is `True`, `np.nan == np.nan` is `False`) and the run results the runbook author records under pandas 3.0.6: three week-4 tests pass on both versions, the missing-value copy passes on the loop and fails on the rewrite.
- The printed `export_tickets.py` on the trainer's screen with its five planted lines marked in pairs on paper, then set side by side with `extract.read_events` and its `%s` parameter, and the `read_table` question answered (table name from the `TABLES` constant, identifiers cannot be bound, OWASP's allow-list line printed).
- The two-way `ticket_age_band` comparison (traditional against assisted) on the board, with the requirement's outputs for 3, 4, 24 and 25 hours as the shared acceptance test, ending in the three-column decision table.
