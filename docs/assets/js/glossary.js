/* glossary.js — centralized technical-terminology glossary for every notes page.
 *
 * ONE source of truth (GLOSSARY below). At load time this script:
 *   1. scans the page prose (.reading-col) for any glossary term that appears,
 *   2. underlines each occurrence and attaches a hover tooltip,
 *   3. builds a "Key terms" block in the left rail listing only the terms
 *      present on THIS page — click opens a popup with the definitions.
 *
 * Definitions are deliberately short: one plain-language sentence.
 * The harness Wire step APPENDS new entries from each day's research brief
 * between the GLOSSARY:BEGIN / GLOSSARY:END markers. Keep entries unique
 * (case-insensitive across term + aka); tests/test_glossary.py enforces it.
 *
 * Entry shape: { term: display form, def: one sentence, aka?: [alt surface forms] }
 * Simple trailing-"s" plurals are matched automatically; add irregulars to aka.
 */
(function () {
  "use strict";

  // ---- THE GLOSSARY (single source of truth) --------------------------------
  var GLOSSARY = [
    // GLOSSARY:BEGIN
    // — programming fundamentals —
    { term: "interpreter", def: "A program that runs your code line by line without producing a separate compiled file." },
    { term: "compiler", def: "A program that translates your whole source code into machine code before it runs." },
    { term: "REPL", def: "Read-Eval-Print Loop — an interactive prompt where you type one expression at a time and see the result.", aka: ["read-eval-print loop"] },
    { term: "variable", def: "A named slot that holds a value you can read and change.", aka: ["variables"] },
    { term: "function", def: "A named, reusable block of code that takes inputs and returns a result.", aka: ["functions"] },
    { term: "class", def: "A blueprint that defines the data and behaviour shared by objects of one kind.", aka: ["classes"] },
    { term: "object", def: "A single instance built from a class, with its own data.", aka: ["objects", "instance", "instances"] },
    { term: "inheritance", def: "A class reusing and extending the behaviour of a parent class.", aka: ["inherit", "inherits", "subclass", "subclasses"] },
    { term: "module", def: "A single Python file whose functions and classes you can import elsewhere.", aka: ["modules"] },
    { term: "package", def: "A folder of related modules that import as one unit.", aka: ["packages"] },
    { term: "virtual environment", def: "An isolated folder of installed packages so one project cannot break another.", aka: ["venv", "virtualenv"] },
    { term: "exception", def: "An error object raised when something goes wrong, which you can catch and handle.", aka: ["exceptions"] },
    { term: "iterator", def: "An object that hands you items one at a time until none are left.", aka: ["iterators", "iterable", "iterables"] },
    { term: "unit test", def: "A small automated check that one piece of code does what it should.", aka: ["unit tests", "unit testing"] },
    { term: "JSON", def: "A plain-text format for structured data that almost every language and API can read." },
    { term: "API", def: "Application Programming Interface — the set of calls one program exposes so other programs can use it.", aka: ["APIs"] },

    // — version control —
    { term: "version control", def: "Tracking every change to a codebase so you can review, undo and collaborate.", aka: ["source control"] },
    { term: "commit", def: "A saved snapshot of your changes with a message describing them.", aka: ["commits"] },
    { term: "branch", def: "A separate line of work in a repository that can later be merged back.", aka: ["branches"] },
    { term: "merge", def: "Combining the changes from one branch into another.", aka: ["merges", "merging"] },
    { term: "pull request", def: "A request to merge your branch, where teammates review the changes first.", aka: ["pull requests", "PR", "PRs"] },

    // — data & SQL —
    { term: "schema", def: "A defined shape for data — which tables, fields and types exist.", aka: ["schemas"] },
    { term: "primary key", def: "The column that uniquely identifies each row in a table.", aka: ["primary keys"] },
    { term: "foreign key", def: "A column that points to the primary key of another table to link rows.", aka: ["foreign keys"] },
    { term: "join", def: "Combining rows from two tables based on a matching column.", aka: ["joins"] },
    { term: "transaction", def: "A group of database operations that either all succeed or all roll back.", aka: ["transactions"] },
    { term: "ACID", def: "Atomicity, Consistency, Isolation, Durability — the guarantees a reliable database transaction gives." },
    { term: "normalization", def: "Organising tables so each fact is stored once, reducing duplication and update errors.", aka: ["normalize", "normalized"] },
    { term: "ETL", def: "Extract, Transform, Load — pulling data from sources, reshaping it, and loading it into a store.", aka: ["ELT"] },
    { term: "data warehouse", def: "A database optimised for analysis across large volumes of historical data.", aka: ["data warehouses", "warehouse"] },
    { term: "OLTP", def: "Online Transaction Processing — databases tuned for many small, fast reads and writes." },
    { term: "OLAP", def: "Online Analytical Processing — databases tuned for big aggregate queries over history." },

    // — machine learning —
    { term: "model", def: "A function learned from data that maps inputs to predictions.", aka: ["models"] },
    { term: "training", def: "Adjusting a model's internal numbers so its predictions match known examples.", aka: ["train", "trained"] },
    { term: "inference", def: "Running a trained model to get an answer, as opposed to training it." },
    { term: "feature", def: "One measurable input a model uses to make a prediction.", aka: ["features"] },
    { term: "label", def: "The known correct answer for a training example.", aka: ["labels"] },
    { term: "overfitting", def: "When a model memorises its training data and performs badly on new data.", aka: ["overfit", "overfits"] },
    { term: "tensor", def: "A multi-dimensional array of numbers — the basic data structure in deep learning.", aka: ["tensors"] },
    { term: "neural network", def: "A model built from layers of simple units whose connections are tuned during training.", aka: ["neural networks", "neural net"] },
    { term: "epoch", def: "One full pass through the training data.", aka: ["epochs"] },

    // — generative AI —
    { term: "LLM", def: "Large Language Model — an AI trained on huge amounts of text to predict and generate language.", aka: ["LLMs", "large language model", "large language models"] },
    { term: "token", def: "A chunk of text (roughly a word-piece) that a model reads and counts one at a time.", aka: ["tokens"] },
    { term: "context window", def: "The fixed amount of text a model can hold in view at once — its working memory.", aka: ["context windows"] },
    { term: "prompt", def: "The text instructions and context you give a model to steer its answer.", aka: ["prompts"] },
    { term: "hallucination", def: "When a model states something fluent and confident that is simply false.", aka: ["hallucinations", "hallucinate"] },
    { term: "embedding", def: "A list of numbers that captures a text's meaning so similar texts land near each other.", aka: ["embeddings", "embed"] },
    { term: "vector", def: "An ordered list of numbers; here, the numeric form of a text's meaning.", aka: ["vectors"] },
    { term: "vector store", def: "A database built to find the stored vectors nearest a query vector, fast.", aka: ["vector database", "vector databases", "vector stores"] },
    { term: "RAG", def: "Retrieval-Augmented Generation — fetch relevant documents, then answer using them.", aka: ["retrieval-augmented generation", "retrieval augmented generation"] },
    { term: "fine-tuning", def: "Continuing to train a model on your own data so new behaviour lives in its weights.", aka: ["fine-tune", "fine-tuned", "finetuning"] },
    { term: "agent", def: "A program that lets a model decide which tools to call, in what order, to reach a goal.", aka: ["agents", "agentic"] },

    // — w01d2: orientation, Agile & Git —
    { term: "repository", def: "A folder whose full change history Git tracks in a hidden .git directory.", aka: ["repo", "repositories"] },
    { term: "staging area", def: "The holding area where you put changes with git add before they become part of the next commit.", aka: ["staged", "git index"] },
    { term: "remote", def: "A copy of a repository hosted elsewhere (such as GitHub) that you push to and pull from.", aka: ["origin"] },
    { term: "SDLC", def: "Software Development Life Cycle — the stages software goes through from idea to retirement: plan, design, build, test, deploy, maintain.", aka: ["software development life cycle"] },
    { term: "Scrum", def: "An Agile framework that delivers work in short fixed-length Sprints with defined roles, events and artifacts.", aka: ["scrum framework"] },
    { term: "sprint", def: "A fixed time-box of one month or less in which a Scrum team turns backlog items into a usable increment." },
    { term: "story point", def: "A relative, unit-less estimate of how much effort a backlog item takes compared with other items, not a number of hours." },
    { term: "Jupyter notebook", def: "A browser document of code and text cells where each code cell runs in a live kernel and shows its output underneath.", aka: ["notebook", "Jupyter", ".ipynb"] },
    { term: "Agile", def: "A way of building software in short iterations that each deliver working software and welcome changing requirements, as set out in the 2001 Agile Manifesto.", aka: ["Agile Manifesto", "agile methodology"] },
    { term: "waterfall", def: "A sequential delivery model where each SDLC phase is finished and signed off before the next begins, so working software appears only at the end.", aka: ["waterfall model"] },
    { term: "backlog", def: "The ordered list of everything the product might need, owned by the Product Owner; the Sprint Backlog is the slice the team commits to for one Sprint.", aka: ["product backlog", "sprint backlog"] },
    { term: "Daily Scrum", def: "A 15-minute event where the Developers inspect progress toward the Sprint Goal and plan the next day's work.", aka: ["stand-up", "standup", "daily stand-up"] },
    { term: "DVCS", def: "Distributed Version Control System — every clone holds the full history, so commits, branches and logs work offline and only push, pull and fetch touch the network.", aka: ["distributed version control", "distributed version control system"] },
    { term: "merge conflict", def: "What Git reports when both branches changed the same lines; it writes the three conflict markers into the file so you can edit, stage and commit the version you want.", aka: ["conflict markers"] },
    { term: "fast-forward", def: "A merge where the target branch has no new commits of its own, so Git simply moves the branch pointer forward and creates no merge commit.", aka: ["fast-forward merge", "ff merge"] },
    { term: "upstream", def: "The remote branch a local branch tracks, set by git push -u, so that plain git push and git pull know where to go.", aka: ["upstream branch", "tracking branch"] },

    // — w01d3: Python basics —
    { term: "PEP 8", def: "The official Python style guide that a team adopts as its shared contract for names, layout and comments.", aka: ["PEP8", "Python style guide"] },
    { term: "snake_case", def: "A naming style that writes identifiers in lowercase words joined by underscores, used for Python variables and functions.", aka: ["snake case", "lower_case_with_underscores"] },
    { term: "docstring", def: "A string literal placed first in a module, function or class that documents what it is for and is readable at runtime.", aka: ["docstrings", "module docstring"] },
    { term: "f-string", def: "A string literal prefixed with f whose braces hold expressions and optional format specs that are evaluated when the line runs.", aka: ["f-strings", "formatted string literal", "formatted string literals"] },
    { term: "operator precedence", def: "The fixed ranking that decides which operator in an expression is applied first when there are no parentheses.", aka: ["precedence", "order of operations"] },
    { term: "short-circuit evaluation", def: "The rule that and/or stop evaluating as soon as the result is known and return one of their operands rather than a pure True or False.", aka: ["short-circuit", "short circuit", "short-circuiting"] },
    { term: "standard streams", def: "The three channels every process gets, stdin for input, stdout for normal output and stderr for warnings and errors.", aka: ["stdin", "stdout", "stderr"] },

    // — w01d4: data types —
    { term: "truthiness", def: "How Python decides whether any value counts as True or False in a condition or `bool()` call: empty containers, zero and `None` are false, nearly everything else is true.", aka: ["truthy", "falsy", "truth value"] },
    { term: "mutable", def: "An object whose contents can change in place after it is created, such as a list, set or dict, unlike a str, tuple or int.", aka: ["mutability"] },
    { term: "aliasing", def: "Two names bound to the same object, so changing it through one name shows up through the other.", aka: ["alias", "aliases"] },
    { term: "hashable", def: "An object with a fixed hash value for its lifetime, which is what lets it be a set member or a dict key.", aka: ["hashability"] },
    { term: "floating-point error", def: "The tiny rounding gap that appears because binary floats cannot store most decimal fractions exactly, so `0.1 + 0.2` is not `0.3`.", aka: ["float precision", "rounding error"] },
    { term: "naive datetime", def: "A datetime with no time zone attached, so it names a clock reading but not an exact moment.", aka: ["naive datetimes"] },
    { term: "namespace", def: "A mapping from names to objects, such as a module's globals, that decides which object a name refers to at that point.", aka: ["namespaces"] },
    { term: "bytes", def: "An immutable sequence of integers from 0 to 255, the raw form that text becomes after `.encode()`.", aka: ["byte string"] },

    // — w01d5: control flow, functions & classes —
    { term: "guard clause", def: "An early `if` that handles a bad or special case and returns or continues at once, so the main logic stays unnested below it.", aka: ["early return", "guard clauses"] },
    { term: "lambda", def: "A one-expression anonymous function written inline, most often as the `key=` argument of `sorted()`.", aka: ["lambda expression", "anonymous function"] },
    { term: "LEGB rule", def: "The order Python searches for a name: local, enclosing, global, built-in.", aka: ["LEGB", "variable scope", "name lookup order"] },
    { term: "mutable default argument", def: "A default such as `history=[]` that Python creates once at definition time and so shares across every call that omits it.", aka: ["mutable default", "default argument trap"] },
    { term: "method override", def: "A subclass redefining a method it inherited so that calls on its objects run the new version, optionally reaching the parent's through `super()`.", aka: ["override", "overriding", "super()"] },
    { term: "__repr__", def: "The special method that returns the developer-facing string for an object, used by `print()` when no `__str__` exists.", aka: ["repr", "dunder repr"] },
    { term: "instance attribute", def: "A value stored on one object through `self`, as opposed to a class attribute shared by all objects of the class.", aka: ["self attribute", "class attribute"] },

    // — week 2: modules, exceptions, testing, collections, pandas & plotting —
    { term: "logging level", def: "A label (DEBUG, INFO, WARNING, ERROR, CRITICAL) on each log message, plus a threshold below which messages are dropped.", aka: ["log level", "log levels", "severity level"] },
    { term: "logger", def: "A named object that code calls to record events, which the logging system routes to handlers such as the console.", aka: ["loggers", "getLogger"] },
    { term: "regular expression", def: "A compact pattern language for finding or replacing text that follows a shape, such as a ticket reference or an email address.", aka: ["regex", "regexes", "regexp", "regular expressions"] },
    { term: "pip", def: "The tool that downloads and installs Python packages from an index into the active environment.", aka: ["pip install"] },
    { term: "PyPI", def: "The public online index that pip downloads packages from.", aka: ["Python Package Index"] },
    { term: "requirements file", def: "A text file listing the packages and versions a project needs so another machine can install the same set.", aka: ["requirements.txt", "pinned dependencies", "pinning"] },
    { term: "linter", def: "A tool that reads source code without running it and reports style problems and likely mistakes.", aka: ["linters", "linting", "pylint"] },
    { term: "__name__ guard", def: "The `if __name__ == \"__main__\":` test that runs code only when a file is run directly, not when it is imported.", aka: ["main guard", "name guard", "__main__"] },
    { term: "traceback", def: "The report Python prints when an exception is not handled, listing the chain of calls with the most recent last and the error on the final line.", aka: ["stack trace", "backtrace"] },
    { term: "try-except", def: "A statement that runs a block of code and, if a named exception is raised in it, runs a handler instead of ending the program.", aka: ["try/except", "exception handler", "exception handling"] },
    { term: "context manager", def: "An object used with a with statement that sets something up on entry and always cleans it up on exit, such as closing a file.", aka: ["with statement", "with block"] },
    { term: "file mode", def: "The string passed to open() that says whether a file is read, written, appended to or exclusively created, and whether as text or bytes.", aka: ["open mode"] },
    { term: "serialization", def: "Converting an in-memory object into text or bytes that can be stored or sent, so it can be rebuilt later.", aka: ["serialize", "serialise", "deserialization", "round trip"] },
    { term: "ISO 8601", def: "The international standard text format for dates and times, such as 2026-10-20T09:00:00, which sorts correctly and is how dates are stored in JSON.", aka: ["ISO date", "isoformat"] },
    { term: "exception chaining", def: "Raising a new exception with raise ... from err so the traceback keeps the original error as its direct cause.", aka: ["raise from", "direct cause"] },
    { term: "assertion", def: "A statement that a condition must be true, which stops the test with a failure report when it is false.", aka: ["assert", "asserts", "assertions"] },
    { term: "fixture", def: "A function marked with `@pytest.fixture` that builds test data or set-up once per test and hands it to any test that names it as a parameter.", aka: ["fixtures", "pytest fixture"] },
    { term: "test pyramid", def: "A picture of a healthy test suite with many fast unit tests at the base, fewer integration tests in the middle and a few end-to-end tests at the top.", aka: ["testing pyramid"] },
    { term: "decorator", def: "A line starting with `@` above a `def` that passes the function below it through another function, which can register or change it.", aka: ["decorators", "@ syntax"] },
    { term: "parametrize", def: "A pytest marker that runs one test function once for each set of inputs and expected values in a list.", aka: ["parametrise", "parametrized test", "parameterized test"] },
    { term: "NumPy", def: "A third-party Python library whose main object is the array, a fixed-type container that supports arithmetic on every element at once." },
    { term: "array", def: "A NumPy container holding same-typed values in a fixed shape, written `np.array([...])` and also called an ndarray.", aka: ["arrays", "ndarray", "np.array"] },
    { term: "vectorisation", def: "Applying an operation to a whole array in one expression, such as `arr * 2`, instead of looping over the elements.", aka: ["vectorization", "vectorised", "vectorized"] },
    { term: "Counter", def: "A dictionary subclass from the collections module that counts how many times each item appears.", aka: ["collections.Counter", "counter object"] },
    { term: "namedtuple", def: "A tuple whose positions also have names, so a field is read as row.status as well as row[2].", aka: ["named tuple", "named tuples", "namedtuples"] },
    { term: "defaultdict", def: "A dictionary that builds a starting value, such as an empty list, the first time a missing key is used.", aka: ["default dict", "default dictionaries"] },
    { term: "deque", def: "A double-ended queue that adds and removes items at either end quickly.", aka: ["double-ended queue", "deques"] },
    { term: "DataFrame", def: "The pandas table of labelled rows and columns, where each column holds one kind of value.", aka: ["data frame", "dataframes", "df"] },
    { term: "Series", def: "One column of a pandas DataFrame: a labelled sequence of values of one type.", aka: ["pandas Series", "series object"] },
    { term: "NaN", def: "The \"not a number\" value pandas uses to mark a missing number.", aka: ["NaN value", "not a number", "missing value"] },
    { term: "figure", def: "The whole Matplotlib canvas that holds one or more plot areas and is what gets saved to an image file.", aka: ["plt.figure"] },
    { term: "axes", def: "One plot area inside a figure, with its own x and y axis, title, labels and drawn marks.", aka: ["ax", "subplot"] },
    { term: "data visualization", def: "Turning data into a chart so that one comparison or trend can be seen at a glance.", aka: ["dataviz", "charting", "plotting"] },
    { term: "bar chart", def: "A chart that draws one bar per category with the bar's length showing its value.", aka: ["bar graph", "bar plot"] },
    { term: "RDBMS", def: "A relational database management system is the server program, such as MySQL, that stores data as related tables and answers queries about it.", aka: ["relational database", "relational database management system", "relational model"] },
    { term: "SQL", def: "Structured Query Language is the standard language for describing, changing and asking questions of the data in a relational database.", aka: ["Structured Query Language"] },
    { term: "Docker image", def: "A read-only package of files and settings, such as mysql:9.7, from which containers are started.", aka: ["image", "images", "container image"] },
    { term: "container", def: "An isolated running process started from an image, with its own filesystem, which is deleted along with the container unless data is kept in a volume.", aka: ["containers", "Docker container"] },
    { term: "Docker volume", def: "A named storage area managed by Docker and mounted into a container so the data outlives the container.", aka: ["named volume", "volumes"] },
    { term: "ERD", def: "An entity relationship diagram draws each kind of thing as a box of attributes and each relationship as a line between boxes, before any table is created.", aka: ["entity relationship diagram", "ER diagram", "entity-relationship diagram"] },
    { term: "crow's foot", def: "The fork drawn at the \"many\" end of an ERD line, so a line with a single bar at customers and a fork at tickets reads as one customer to many tickets.", aka: ["crow's-foot notation"] },
    { term: "DDL", def: "Data Definition Language: the SQL statements (CREATE, ALTER, DROP, TRUNCATE) that define or change the structure of tables and databases.", aka: ["data definition language"] },
    { term: "DML", def: "Data Manipulation Language: the SQL statements (INSERT, UPDATE, DELETE) that add, change or remove the rows inside tables.", aka: ["data manipulation language"] },
    { term: "DQL", def: "Data Query Language: the SQL statement SELECT, which reads rows without changing them.", aka: ["data query language"] },
    { term: "DCL", def: "Data Control Language: the SQL statements (GRANT, REVOKE) that give or take away what an account may do.", aka: ["data control language", "GRANT", "REVOKE"] },
    { term: "TCL", def: "Transaction Control Language: the SQL statements (START TRANSACTION, COMMIT, ROLLBACK, SAVEPOINT) that group changes so they apply or vanish together.", aka: ["transaction control language", "rollback", "savepoint"] },
    { term: "autocommit", def: "The MySQL default in which every statement outside a transaction is saved the moment it runs.", aka: ["auto-commit"] },
    { term: "least privilege", def: "Giving an account only the permissions its job needs, so a mistake or a leaked password does less damage.", aka: ["principle of least privilege"] },
    { term: "composite key", def: "A primary key made of two or more columns whose combination, not each column, must be unique.", aka: ["composite primary key", "compound key"] },
    { term: "candidate key", def: "A minimal set of columns that could uniquely identify a row, from which one is chosen as the primary key.", aka: ["candidate keys"] },
    { term: "alternate key", def: "A candidate key not chosen as the primary key, declared UNIQUE NOT NULL.", aka: ["alternate keys", "secondary key"] },
    { term: "referential integrity", def: "The guarantee that every foreign key value matches an existing parent row or is NULL.", aka: ["foreign key integrity"] },
    { term: "constraint", def: "A rule declared on a table that the database enforces on every write.", aka: ["integrity constraint"] },
    { term: "cascade", def: "A foreign key action that applies a parent's delete or update to its child rows.", aka: ["ON DELETE CASCADE", "cascading delete"] },
    { term: "bridge table", def: "A table of two foreign keys that links two tables in a many-to-many relationship.", aka: ["junction table", "link table", "association table"] },
    { term: "surrogate key", def: "A meaningless generated id used as the primary key instead of a real-world value.", aka: ["surrogate id"] },
    { term: "subquery", def: "A SELECT written inside another SQL statement whose result the outer statement uses as a value, a list or a temporary table.", aka: ["subqueries", "nested query", "inner query"] },
    { term: "aggregate function", def: "A SQL function such as COUNT, SUM or AVG that turns many rows into a single value per group.", aka: ["aggregate functions", "aggregation"] },
    { term: "outer join", def: "A join that keeps rows with no match on one or both sides and fills the missing columns with NULL.", aka: ["left join", "right join", "left outer join", "right outer join", "full outer join"] },
    { term: "isolation level", def: "The setting that decides how much of other transactions' unfinished or newly committed work a transaction can see.", aka: ["isolation levels", "transaction isolation"] },
    { term: "scalar function", def: "A SQL function such as CONCAT or DATE_ADD that returns one value for each input row.", aka: ["scalar functions"] },
    { term: "dirty read", def: "Reading a change that another transaction has made but not yet committed and may still undo.", aka: ["dirty reads"] },
    { term: "common table expression", def: "A named temporary result defined with WITH at the top of a query so later parts can read from it by name.", aka: ["CTE", "CTEs", "WITH clause"] },
    { term: "window function", def: "A function that computes over a set of related rows while still returning every row, unlike an aggregate that collapses them.", aka: ["window functions", "OVER clause"] },
    { term: "trigger", def: "A routine stored with a table that the server runs automatically when a row is inserted, updated or deleted.", aka: ["triggers", "database trigger"] },
    { term: "view", def: "A named, stored SELECT that is read like a table but holds no rows of its own.", aka: ["views"] },
    { term: "stored procedure", def: "A named block of SQL kept in the database and run on demand with CALL.", aka: ["stored procedures", "procedure"] },
    { term: "user-defined function", def: "A named routine kept in the database that takes inputs and returns one value, usable inside a query.", aka: ["UDF", "stored function"] },
    { term: "index", def: "A separate sorted structure on one or more columns that lets the server find rows without reading the whole table.", aka: ["indexes", "B-tree index"] },
    { term: "EXPLAIN", def: "A statement that prints how the server plans to run a query, such as a table scan or an index lookup.", aka: ["query plan", "execution plan"] },
    { term: "cloud computing", def: "Renting computing resources from a provider over a network, on demand and billed by measured use, instead of owning the hardware.", aka: ["the cloud"] },
    { term: "IaaS", def: "Infrastructure as a service: the provider supplies virtual machines, storage and networks, and the customer runs everything above them.", aka: ["infrastructure as a service"] },
    { term: "PaaS", def: "Platform as a service: the provider runs the operating system and runtime or managed engine, and the customer brings code or data.", aka: ["platform as a service"] },
    { term: "SaaS", def: "Software as a service: the provider runs a finished application that users reach through a browser or app.", aka: ["software as a service"] },
    { term: "region", def: "A geographic area in a cloud provider's network, made of several zones, such as Toronto's northamerica-northeast2.", aka: ["cloud region"] },
    { term: "availability zone", def: "An isolated deployment area inside a region with its own power and networking, so one failure does not take down the others.", aka: ["zones", "availability zones"] },
    { term: "hybrid cloud", def: "A setup that joins an organisation's own infrastructure to a public cloud so workloads and data can move between them.", aka: ["hybrid"] },
    { term: "multi-cloud", def: "Using services from more than one cloud provider for one organisation's workloads.", aka: ["multicloud"] },
    { term: "big data", def: "Data whose volume, velocity or variety is too great for one machine and an ordinary database to store and process well.", aka: ["big-data", "five V's"] },
    { term: "batch processing", def: "Processing a bounded set of data collected over a period in one scheduled run that then ends.", aka: ["batch job", "batch jobs"] },
    { term: "stream processing", def: "Processing an unbounded flow of events continuously as each one arrives.", aka: ["streaming pipeline", "streaming pipelines"] },
    { term: "distributed storage", def: "Keeping data split and copied across many machines so capacity grows by adding machines and one failure loses nothing.", aka: ["distributed file system"] },
    { term: "semi-structured data", def: "Data that carries its own structure through keys or tags, such as JSON or XML, without a fixed table schema.", aka: ["semi structured", "semistructured"] },
    { term: "columnar format", def: "A file or table layout that stores each column's values together so a query reads only the columns it needs.", aka: ["column-oriented", "columnar file"] },
    { term: "data lifecycle", def: "The stages data passes through from generation to deletion: collection, storage, processing, analysis, sharing and archival between.", aka: ["data life cycle", "lifecycle stages"] },
    { term: "JSON lines", def: "A text file holding one complete JSON object per line.", aka: ["newline-delimited JSON", "NDJSON", "JSONL"] },
    { term: "schema-on-write", def: "Checking and typing data against a fixed table schema at the moment it is loaded, as a warehouse does, instead of when it is read.", aka: ["schema on write"] },
    { term: "data mart", def: "A subject-focused slice of warehouse data built for one team, such as support managers.", aka: ["data marts", "dependent data mart", "independent data mart"] },
    { term: "operational data store", def: "A short-history, frequently refreshed copy that integrates current data from operational systems for day-to-day reports.", aka: ["ODS"] },
    { term: "denormalization", def: "Deliberately storing copies of values or nesting related rows together so analytical queries need fewer joins.", aka: ["denormalisation", "denormalize", "denormalise", "denormalized"] },
    { term: "data cleansing", def: "The steps that fix or reject missing, duplicate, invalid and inconsistently formatted rows before they are loaded into a warehouse.", aka: ["data cleaning", "data quality"] },
    { term: "slot", def: "BigQuery's unit of computing capacity, which a query's stages are scheduled over.", aka: ["slots", "slot usage"] },
    { term: "dataset", def: "The BigQuery container that groups tables and views in a project and carries a location and a default table expiration.", aka: ["datasets", "BigQuery dataset"] },
    { term: "staging table", def: "A table that holds extracted data exactly as it arrived, before cleansing and modelling.", aka: ["staging tables", "raw staging"] },
    { term: "fact table", def: "The central table of a dimensional model, with one row per event or measurement at a stated grain, holding keys to dimensions and numeric measures.", aka: ["fact tables", "fact"] },
    { term: "dimension table", def: "A table of descriptive attributes (who, what, where, when) that a fact table points to and that queries filter and group by.", aka: ["dimension tables", "dimension", "dimensions"] },
    { term: "grain", def: "What exactly one row of a fact table represents, such as one ticket event, stated before any column is chosen.", aka: ["granularity", "fact grain"] },
    { term: "star schema", def: "A dimensional model with one fact table joined directly to denormalised dimension tables, drawn like a star.", aka: ["star schemas", "star"] },
    { term: "snowflake schema", def: "A star whose dimensions are further normalised into linked lookup tables, trading extra joins for less repetition.", aka: ["snowflake", "snowflaked"] },
    { term: "slowly changing dimension", def: "A dimension whose attribute values change rarely, with a rule (type 0 to 6) for what happens to the old value.", aka: ["SCD", "SCDs", "SCD type 2"] },
    { term: "partition pruning", def: "A warehouse skipping the partitions a filter on the partition column rules out, so fewer bytes are scanned and billed.", aka: ["pruning", "pruned partitions"] },
    { term: "clustered table", def: "A table whose storage is sorted by up to four chosen columns, so a filter on them reads fewer blocks.", aka: ["clustering", "cluster columns"] },
    { term: "watermark", def: "The highest id or timestamp a job has already loaded, read at the start of a run so it extracts only newer rows.", aka: ["high-water mark", "load watermark"] },
    { term: "incremental load", def: "A run that extracts and loads only the rows added since the last run instead of the whole source.", aka: ["delta load", "incremental extract"] },
    { term: "idempotent", def: "Describes a job whose repeated run leaves the data exactly as one run did.", aka: ["idempotency", "safe to rerun"] },
    { term: "reject", def: "A record that fails a validation rule and is saved in a separate table with the reason instead of being loaded or silently dropped.", aka: ["rejects", "rejected row", "reject table"] },
    { term: "external table", def: "A BigQuery table whose data stays in a source such as a Google Sheet or Cloud Storage and is read at query time.", aka: ["external data source"] },
    { term: "federated query", def: "A query that BigQuery sends to an outside database through a connection and joins with its own tables.", aka: ["federated queries", "EXTERNAL_QUERY"] },
    { term: "query parameter", def: "A named placeholder such as @kind in SQL whose value is sent separately from the statement text.", aka: ["parameterized query", "named parameter", "bind variable"] },
    { term: "load log", def: "A table with one row per job run recording when it ran and how many rows were read, loaded and rejected.", aka: ["run log", "audit table"] }
    // GLOSSARY:END
  ];

  // ---- build lookup: every surface form → entry ------------------------------
  var BY_FORM = {};        // lowercased surface form → entry
  var FORMS = [];          // all surface forms, for regex (longest first)
  function addForm(form, entry) {
    var k = form.toLowerCase();
    if (!BY_FORM[k]) { BY_FORM[k] = entry; FORMS.push(form); }
  }
  GLOSSARY.forEach(function (e) {
    addForm(e.term, e);
    (e.aka || []).forEach(function (a) { addForm(a, e); });
  });
  // longest first so "context window" wins over "context"
  FORMS.sort(function (a, b) { return b.length - a.length; });

  function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
  // optional trailing "s" for simple plurals; \b word boundaries
  var RE = new RegExp("\\b(" + FORMS.map(esc).join("|") + ")(s?)\\b", "gi");

  // ---- tooltip (hover) -------------------------------------------------------
  var tip;
  function ensureTip() {
    if (tip) return tip;
    tip = document.createElement("div");
    tip.className = "gloss-tip";
    tip.setAttribute("role", "tooltip");
    document.body.appendChild(tip);
    return tip;
  }
  function showTip(el) {
    var t = ensureTip();
    t.innerHTML = '<b>' + el.dataset.glossTerm + '</b>' + el.dataset.glossDef;
    t.classList.add("show");
    var r = el.getBoundingClientRect();
    var tw = t.offsetWidth, th = t.offsetHeight;
    var left = r.left + r.width / 2 - tw / 2 + window.scrollX;
    left = Math.max(10 + window.scrollX, Math.min(left, window.scrollX + document.documentElement.clientWidth - tw - 10));
    var top = r.top + window.scrollY - th - 9;
    var below = false;
    if (top < window.scrollY + 6) { top = r.bottom + window.scrollY + 9; below = true; }
    t.style.left = left + "px";
    t.style.top = top + "px";
    t.classList.toggle("below", below);
  }
  function hideTip() { if (tip) tip.classList.remove("show"); }

  // ---- glossary modal (opened by the Key-terms block or any inline term) -----
  var modal;
  function buildModal(order, found) {
    modal = document.createElement("div");
    modal.className = "gloss-modal-overlay";
    var rows = order.map(function (t) {
      var e = found[t];
      return '<div class="gm-row" data-term="' + t.toLowerCase() + '">' +
        '<dt class="gm-term">' + t + '</dt><dd class="gm-def">' + e.def + '</dd></div>';
    }).join("");
    modal.innerHTML =
      '<div class="gloss-modal" role="dialog" aria-modal="true" aria-label="Glossary">' +
        '<button class="gloss-modal-x" aria-label="Close">✕</button>' +
        '<div class="gm-k">Glossary</div>' +
        '<h2 class="gm-h">Key terms on this page</h2>' +
        '<p class="gm-sub">' + order.length + ' term' + (order.length === 1 ? '' : 's') +
          ' · plain-language definitions, shared across every page.</p>' +
        '<dl class="gm-list">' + rows + '</dl>' +
      '</div>';
    document.body.appendChild(modal);
    modal.addEventListener("click", function (e) {
      if (e.target === modal || e.target.classList.contains("gloss-modal-x")) closeModal();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeModal(); });
  }
  function openModal(highlight) {
    if (!modal) return;
    modal.querySelectorAll(".gm-row.on").forEach(function (r) { r.classList.remove("on"); });
    modal.classList.add("show");
    if (highlight) {
      var row = modal.querySelector('.gm-row[data-term="' + highlight.toLowerCase() + '"]');
      if (row) {
        row.classList.add("on");
        row.scrollIntoView({ block: "center" });
      }
    } else {
      modal.querySelector(".gloss-modal").scrollTop = 0;
    }
  }
  function closeModal() { if (modal) modal.classList.remove("show"); }

  // Focus view (D-0044) reads as plain text: no tips, no modal, no tab stops on the terms.
  function quiet() { return document.documentElement.getAttribute("data-view") === "focus"; }

  function wire(el) {
    el.addEventListener("mouseenter", function () { if (!quiet()) showTip(el); });
    el.addEventListener("mouseleave", hideTip);
    el.addEventListener("focus", function () { if (!quiet()) showTip(el); });
    el.addEventListener("blur", hideTip);
    el.addEventListener("click", function (e) {
      if (quiet()) return;
      e.preventDefault();
      hideTip();
      openModal(el.dataset.glossTerm);
    });
  }

  // ---- scan the page, wrap occurrences of each term --------------------------
  var SKIP = { CODE: 1, PRE: 1, A: 1, BUTTON: 1, H1: 1, H2: 1, H3: 1, SCRIPT: 1, STYLE: 1, SVG: 1 };
  function skipNode(node) {
    for (var p = node.parentNode; p && p.nodeType === 1; p = p.parentNode) {
      if (SKIP[p.tagName]) return true;
      if (p.classList && (p.classList.contains("tag") ||
        p.classList.contains("reading-sources") ||
        p.classList.contains("gloss-term"))) return true;
    }
    return false;
  }

  function run() {
    var root = document.querySelector(".reading-col");
    if (!root) return;
    var found = {};
    var foundOrder = [];

    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (!n.nodeValue || !n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        if (skipNode(n)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var textNodes = [];
    var tn;
    while ((tn = walker.nextNode())) textNodes.push(tn);

    // One underline per term per section.step (D-0060): the first occurrence in a step gets the tooltip, later
    // ones stay plain text, so a page with "module" 76 times is not underlined 76 times. Text outside any step
    // (the lede) is its own scope. The Key terms block still lists every term the page uses.
    var seenInScope = {};
    function scopeOf(node) {
      var el = node.parentNode;
      while (el && el.nodeType === 1 && el !== root) {
        if (el.classList && el.classList.contains("step")) return el.getAttribute("data-step") || "step";
        el = el.parentNode;
      }
      return "lede";
    }

    textNodes.forEach(function (node) {
      var text = node.nodeValue;
      var scope = scopeOf(node);
      var seen = seenInScope[scope] || (seenInScope[scope] = {});
      RE.lastIndex = 0;
      var m, hits = [];
      while ((m = RE.exec(text))) {
        var entry = BY_FORM[m[1].toLowerCase()];
        if (!entry) continue;
        if (!found[entry.term]) { found[entry.term] = entry; foundOrder.push(entry.term); }
        if (seen[entry.term]) continue;
        seen[entry.term] = true;
        hits.push({ start: m.index, end: m.index + m[0].length, entry: entry, text: m[0] });
      }
      if (!hits.length) return;
      var frag = document.createDocumentFragment();
      var cursor = 0;
      hits.forEach(function (h) {
        if (h.start > cursor) frag.appendChild(document.createTextNode(text.slice(cursor, h.start)));
        var span = document.createElement("span");
        span.className = "gloss-term";
        span.tabIndex = 0;
        span.textContent = h.text;
        span.dataset.glossTerm = h.entry.term;
        span.dataset.glossDef = h.entry.def;
        wire(span);
        frag.appendChild(span);
        cursor = h.end;
      });
      if (cursor < text.length) frag.appendChild(document.createTextNode(text.slice(cursor)));
      node.parentNode.replaceChild(frag, node);
    });

    // theme.js fires tc-view when the reader changes the page view
    var terms = root.querySelectorAll(".gloss-term");
    function syncView() {
      var stop = quiet() ? -1 : 0;
      for (var i = 0; i < terms.length; i++) terms[i].tabIndex = stop;
      hideTip();
    }
    if (quiet()) syncView();
    document.addEventListener("tc-view", syncView);

    buildKeyTerms(foundOrder, found);
  }

  // ---- "Key terms" block → opens the glossary modal --------------------------
  function buildKeyTerms(order, found) {
    if (!order.length) return;
    order.sort(function (a, b) { return a.toLowerCase().localeCompare(b.toLowerCase()); });
    buildModal(order, found);

    function keyTermsBlock() {
      var block = document.createElement("button");
      block.type = "button";
      block.className = "gloss-block";
      block.innerHTML =
        '<span class="gb-k">Glossary</span>' +
        '<span class="gb-t">Key terms on this page</span>' +
        '<span class="gb-n">' + order.length + ' term' + (order.length === 1 ? '' : 's') +
          ' · tap to define</span>';
      block.addEventListener("click", function () { openModal(); });
      return block;
    }

    // One block under the page menu and one inline before the sources. The menu is
    // hidden in narrow windows and in Focus view (D-0044), and can come and go after
    // load, so the stylesheet picks which of the two shows (.gloss-block-alt).
    var toc = document.querySelector(".toc");
    if (toc) toc.appendChild(keyTermsBlock());
    var inline = keyTermsBlock();
    inline.classList.add("gloss-block-inline");
    if (toc) inline.classList.add("gloss-block-alt");
    var src = document.querySelector(".reading-sources");
    if (src) src.parentNode.insertBefore(inline, src);
    else document.querySelector(".reading-col").appendChild(inline);
  }

  // Expose for tests / tooling (read-only).
  window.GLOSSARY = GLOSSARY;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
