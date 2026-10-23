# w03d1 — SQL & RDBMS introduction

gate: light
verified: 2026-10-23
week: 3 · SQL with MySQL
day: 1 · day-1-sql-and-rdbms-intro

version-stamps:
  - python: 3.15 (verified 2026-10-23)
  - mysql: 9.7 LTS, image tag mysql:9.7 (patch floats with the tag; 9.7.4 on 2026-10-22) (verified 2026-10-23)   # syntax cited from the 9.7 manual (dev.mysql.com/doc/refman/9.7), as the w03d2 and w03d5 briefs do
  - docker-desktop: current stable, Docker Engine CLI (docker run, docker exec, docker volume) (verified 2026-10-23)

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- The official mysql image reads MYSQL_ROOT_PASSWORD to set the root password on first start, and the variable is required — [MySQL Docker Hub image](https://hub.docker.com/_/mysql)
- Data written under /var/lib/mysql in the container is kept by mounting a Docker volume there, so it outlives the container — [Docker volumes](https://docs.docker.com/engine/storage/volumes/)
- A container is an isolated process started from an image; an image is the read-only package of files and settings it starts from — [What is a container?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)
- docker run -p 3306:3306 publishes container port 3306 on host port 3306 (host port first, container port second) — [docker container run](https://docs.docker.com/reference/cli/docker/container/run/)
- docker exec runs a command inside a running container, and -it gives it an interactive terminal — [docker container exec](https://docs.docker.com/reference/cli/docker/container/exec/)
- MySQL is a relational database management system, and its default storage engine is InnoDB — [Introduction to InnoDB](https://dev.mysql.com/doc/refman/9.7/en/innodb-introduction.html)
- SELECT VERSION() returns the server version string — [Information Functions](https://dev.mysql.com/doc/refman/9.7/en/information-functions.html)
- In MySQL, CREATE SCHEMA is a synonym for CREATE DATABASE, so a MySQL schema is a database — [CREATE DATABASE Statement](https://dev.mysql.com/doc/refman/9.7/en/create-database.html)
- CREATE TABLE names each column with a data type, and IF NOT EXISTS makes a repeat run a warning instead of an error — [CREATE TABLE Statement](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- DESCRIBE is a shortcut for SHOW COLUMNS and lists each column's field, type, nullability, key, default and extra — [DESCRIBE Statement](https://dev.mysql.com/doc/refman/9.7/en/describe.html)
- INT is a 4-byte integer (-2147483648 to 2147483647 signed) and BIGINT is 8 bytes — [Integer Types](https://dev.mysql.com/doc/refman/9.7/en/integer-types.html)
- DECIMAL(M,D) stores exact fixed-point values, which is why it suits money, while FLOAT and DOUBLE are approximate — [Fixed-Point Types](https://dev.mysql.com/doc/refman/9.7/en/fixed-point-types.html)
- CHAR(n) is fixed length and padded with spaces to n, while VARCHAR(n) stores only the characters plus a length prefix — [The CHAR and VARCHAR Types](https://dev.mysql.com/doc/refman/9.7/en/char.html)
- DATETIME holds a date and time from 1000-01-01 00:00:00 to 9999-12-31 23:59:59 and has no time zone attached — [The DATE, DATETIME, and TIMESTAMP Types](https://dev.mysql.com/doc/refman/9.7/en/datetime.html)
- MySQL accepts BOOL and BOOLEAN as synonyms for TINYINT(1), so there is no separate true boolean column type — [Numeric Type Syntax](https://dev.mysql.com/doc/refman/9.7/en/numeric-type-syntax.html)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### MySQL
- Interview questions: What is MySQL and what kind of software is a database server?; What is the difference between a Docker image and a container?; Why does data vanish when a database container is removed, and what prevents it?
- Adjacent concept: client and server as separate programs talking over a port — the mysql command-line client connects to the server on 3306, which is why the client can run inside the container or on the host.
- Trade-off or limit: A container's own writable layer is deleted with the container, so a database needs a named volume for its data directory — [Docker volumes](https://docs.docker.com/engine/storage/volumes/)
- Recognise on sight: `docker run --name desk-mysql -e MYSQL_ROOT_PASSWORD=desk -p 3306:3306 -v desk-data:/var/lib/mysql -d mysql:9.7`
- Claims:
  - The -d flag runs the container in the background (detached) — [docker container run](https://docs.docker.com/reference/cli/docker/container/run/)
  - A tag such as mysql:9.7 names a release line and the patch inside it can change between pulls, so notes name the tag and not a patch version — [MySQL Docker Hub image](https://hub.docker.com/_/mysql)
  - The mysql client's -p with no value prompts for the password, so it does not appear in the command line or shell history — [mysql Client Options](https://dev.mysql.com/doc/refman/9.7/en/mysql-command-options.html)
  - docker stop halts a container and keeps it and its volumes, and docker start brings the same container back — [docker container stop](https://docs.docker.com/reference/cli/docker/container/stop/)
  - Official MySQL deployment on Docker is documented, including starting the server and connecting from a client inside the container — [Basic Steps for MySQL Server Deployment with Docker](https://dev.mysql.com/doc/refman/9.7/en/docker-mysql-getting-started.html)

### Introduction to RDBMS
- Interview questions: Why store data in a relational database instead of a JSON file? (qc2.sql.R01); What does "one fact in one place" mean and why does it matter? (qc2.sql.R01); What can a database enforce that a file cannot, and what happens when two programs write at once? (qc2.sql.R01)
- Adjacent concept: relational versus non-relational stores — an interviewer asks when a file or a document store is the better fit; it belongs here as the honest limit of the reasons.
- Trade-off or limit: A relational database needs a schema declared up front, so changing the shape of the data is a deliberate change and not a free edit — [CREATE TABLE Statement](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Recognise on sight: a file such as tickets.json rewritten whole on every save, against a table where one row changes
- Claims:
  - A relational database stores data as tables of rows and columns, and rows in different tables are related by matching column values — [MySQL Reference Manual: What is MySQL?](https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html)
  - The MySQL server handles many client connections at once, so several programs can read and write the same data — [MySQL Reference Manual: What is MySQL?](https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html)
  - In strict SQL mode, which is on by default, the server refuses a value that does not fit a column's type instead of storing a changed one, so the rule lives in the database and not in each program that writes; keys are a further rule of this kind that Wednesday adds — [Server SQL Modes](https://dev.mysql.com/doc/refman/9.7/en/sql-mode.html)
  - Relational databases are queried with SQL, a declarative language where the query says what rows are wanted and the server chooses how to find them — [MySQL Reference Manual: What is MySQL?](https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html)

### What is SQL
- Interview questions: What does SQL stand for and what is it used for?; Is SQL a programming language, and how does declarative differ from procedural?; Is SQL the same as MySQL?
- Adjacent concept: the dialect question — SQL is a standard and each server (MySQL, PostgreSQL, SQL Server) adds its own extensions, so a statement may need small changes between them.
- Trade-off or limit: MySQL follows the SQL standard with extensions and some differences, so portable SQL needs care — [MySQL Standards Compliance](https://dev.mysql.com/doc/refman/9.7/en/compatibility.html)
- Recognise on sight: `SELECT VERSION();` typed at the `mysql>` prompt and ended with a semicolon
- Claims:
  - SQL stands for Structured Query Language — [MySQL Reference Manual: What is MySQL?](https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html)
  - A statement typed at the mysql prompt runs when it ends with a semicolon, and a statement without one waits for more lines — [mysql Client Commands](https://dev.mysql.com/doc/refman/9.7/en/mysql-commands.html)
  - SQL keywords are not case sensitive, while table-name case sensitivity depends on the operating system of the server, so style rules fix names in lower snake case — [Identifier Case Sensitivity](https://dev.mysql.com/doc/refman/9.7/en/identifier-case-sensitivity.html)
  - A line starting with two dashes and a space is a comment — [Comments](https://dev.mysql.com/doc/refman/9.7/en/comments.html)

### Schema
- Interview questions: What is a database schema? (qc2.sql.P04); What is the difference between a schema and the data inside it? (qc2.sql.P04); In MySQL, how does a schema relate to a database? (qc2.sql.P04)
- Adjacent concept: other servers treat a schema as a namespace inside a database, so the answer changes by product — worth one sentence so the MySQL meaning is not over-generalised.
- Trade-off or limit: MySQL uses SCHEMA and DATABASE as the same thing, which differs from servers where a schema is a sub-namespace — [CREATE DATABASE Statement](https://dev.mysql.com/doc/refman/9.7/en/create-database.html)
- Recognise on sight: `CREATE DATABASE IF NOT EXISTS ticket_desk;` followed by `USE ticket_desk;`
- Claims:
  - CREATE DATABASE creates a database with the given name and needs the CREATE privilege on it — [CREATE DATABASE Statement](https://dev.mysql.com/doc/refman/9.7/en/create-database.html)
  - USE db_name makes that database the default for the statements that follow in the session — [USE Statement](https://dev.mysql.com/doc/refman/9.7/en/use.html)
  - SHOW DATABASES lists the databases on the server, including system ones such as mysql and information_schema — [SHOW DATABASES Statement](https://dev.mysql.com/doc/refman/9.7/en/show-databases.html)
  - information_schema is a read-only set of views that describes the server's own databases, tables and columns — [INFORMATION_SCHEMA Tables](https://dev.mysql.com/doc/refman/9.7/en/information-schema.html)

### Table structure
- Interview questions: What are rows, columns and fields in a table? (qc2.sql.P04); How do you read the structure of an existing table?; Why does a column have exactly one data type?
- Adjacent concept: NULL as "no value" — DESCRIBE shows a Null column, so an interviewer asks what NULL means; here it is named in one line and the rules that forbid it belong to a later day.
- Trade-off or limit: Every column in a row exists even when empty, so a wide table of mostly-missing values wastes space and signals a modelling problem — [CREATE TABLE Statement](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Recognise on sight: the boxed DESCRIBE output with columns Field, Type, Null, Key, Default, Extra
- Claims:
  - SHOW TABLES lists the tables in the current database — [SHOW TABLES Statement](https://dev.mysql.com/doc/refman/9.7/en/show-tables.html)
  - DESCRIBE tickets and SHOW COLUMNS FROM tickets give the same column listing — [DESCRIBE Statement](https://dev.mysql.com/doc/refman/9.7/en/describe.html)
  - SHOW CREATE TABLE prints the exact CREATE TABLE statement that would rebuild a table — [SHOW CREATE TABLE Statement](https://dev.mysql.com/doc/refman/9.7/en/show-create-table.html)
  - A column declared with only a type accepts NULL, and DESCRIBE shows YES in its Null column — [Data Type Default Values](https://dev.mysql.com/doc/refman/9.7/en/data-type-defaults.html)

### SQL data types
- Interview questions: When would you choose VARCHAR over CHAR? (qc2.sql.P05); Why is DECIMAL used for money and not FLOAT? (qc2.sql.P05); What is the difference between INT and BIGINT, and when does INT run out? (qc2.sql.P05)
- Adjacent concept: DATETIME versus TIMESTAMP — the next question after DATETIME is how each treats time zones, and it is the reason the desk's naive timestamps use DATETIME.
- Trade-off or limit: INT tops out at 2,147,483,647, so a table that may grow past two billion rows needs BIGINT, at twice the storage per value — [Integer Types](https://dev.mysql.com/doc/refman/9.7/en/integer-types.html)
- Recognise on sight: `monthly_fee DECIMAL(8,2)` and `title VARCHAR(100)` on neighbouring lines of a CREATE TABLE
- Claims:
  - DECIMAL(8,2) holds up to 8 digits of which 2 follow the decimal point, so the largest value is 999999.99 — [Fixed-Point Types](https://dev.mysql.com/doc/refman/9.7/en/fixed-point-types.html)
  - CHAR(n) values are right-padded to n characters when stored, and trailing spaces are removed when retrieved — [The CHAR and VARCHAR Types](https://dev.mysql.com/doc/refman/9.7/en/char.html)
  - VARCHAR(n) holds up to n characters, not bytes, and a utf8mb4 character takes up to four bytes — [The CHAR and VARCHAR Types](https://dev.mysql.com/doc/refman/9.7/en/char.html)
  - TIMESTAMP is stored as UTC and limited to 1970-01-01 through 2038-01-19, while DATETIME is not converted by time zone — [The DATE, DATETIME, and TIMESTAMP Types](https://dev.mysql.com/doc/refman/9.7/en/datetime.html)
  - The numeric type families are integer, fixed-point, floating-point and bit-value, and the string families include CHAR, VARCHAR, TEXT and BLOB — [Data Types](https://dev.mysql.com/doc/refman/9.7/en/data-types.html)
  - utf8mb4 is the default character set, so a VARCHAR column stores accented letters and emoji without extra settings — [Character Sets and Collations](https://dev.mysql.com/doc/refman/9.7/en/charset-mysql.html)

### Data modeling and ERD
- Interview questions: What is an ERD and what do its boxes and lines mean? (qc2.sql.P02); How do you turn a written description into entities, attributes and relationships? (qc2.sql.P06); Reading the desk's ERD, how many tickets can one customer have, and how many agents can one ticket have? (qc2.sql.P02)
- Adjacent concept: reading the crow's-foot end of a one-to-many line — the interviewer hands over a diagram and asks which box is the "many" side, and the fork at the line end is the answer an ERD exists to give.
- Trade-off or limit: An ERD records structure and relationships but not the rules a database enforces or the queries it will run, so a model is checked against both before tables are built — [MySQL Workbench: Data Modeling](https://dev.mysql.com/doc/workbench/en/wb-data-modeling.html)
- Recognise on sight: a box named tickets listing ticket_id, title, customer_id, with a crow's-foot line to a box named customers
- Claims:
  - An entity becomes a table, an attribute becomes a column, and an instance of the entity becomes a row — [MySQL Workbench: Data Modeling](https://dev.mysql.com/doc/workbench/en/wb-data-modeling.html)
  - One customer to many tickets is a one-to-many relationship, drawn with a single bar at the customer end and a crow's foot at the ticket end — [MySQL Workbench: Data Modeling](https://dev.mysql.com/doc/workbench/en/wb-data-modeling.html)
  - Each box lists its entity's attributes, and the attribute that picks out one instance (customer_id on customers, agent_id on agents, ticket_id on tickets) is marked on the box; the line from tickets to customers is drawn through the customer_id attribute both boxes carry — [MySQL Workbench: Data Modeling](https://dev.mysql.com/doc/workbench/en/wb-data-modeling.html)
  - MySQL Workbench can draw an EER diagram and generate the CREATE TABLE script from it, and can reverse-engineer a diagram from an existing database — [MySQL Workbench: Creating a Model](https://dev.mysql.com/doc/workbench/en/wb-getting-started-tutorial-creating-a-model.html)

### Defining schema
- Interview questions: Write a CREATE TABLE for a table with an id, a short name, a money amount and a created time (qc2.sql.P06); What does IF NOT EXISTS do and when does it hide a mistake?; How do you check that a table was created as you intended? (qc2.sql.P04)
- Adjacent concept: a .sql file versus typing at the prompt — the file is the source of the structure and gets rerun from the top, so the interviewer asks what happens when it runs a second time, which is where IF NOT EXISTS earns its place.
- Trade-off or limit: IF NOT EXISTS skips a CREATE TABLE when a table of that name exists, even if its columns differ, so an edited file does not change the old table on a rerun — [CREATE TABLE Statement](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Recognise on sight: a .sql file of CREATE TABLE statements, one column per line, run into the container with `docker exec -i desk-mysql mysql -uroot -pdesk < sql/schema.sql`
- Claims:
  - A CREATE TABLE statement lists column definitions separated by commas inside parentheses and ends with a semicolon — [CREATE TABLE Statement](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
  - The mysql client reads statements from standard input, so a file can be run non-interactively with a shell redirect — [mysql Client Options](https://dev.mysql.com/doc/refman/9.7/en/mysql-command-options.html)
  - Using -p with the password in the same argument works but the client warns that it is insecure, because the password is visible to other users of the machine — [End-User Guidelines for Password Security](https://dev.mysql.com/doc/refman/9.7/en/password-security-user.html)
  - A table name that is a reserved word must be quoted with backticks, which is one reason schema names avoid words such as order and group — [Keywords and Reserved Words](https://dev.mysql.com/doc/refman/9.7/en/keywords.html)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- MySQL Docker Hub image — https://hub.docker.com/_/mysql
- Basic Steps for MySQL Server Deployment with Docker — https://dev.mysql.com/doc/refman/9.7/en/docker-mysql-getting-started.html
- Docker volumes — https://docs.docker.com/engine/storage/volumes/
- What is a container? — https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/
- docker container run — https://docs.docker.com/reference/cli/docker/container/run/
- docker container exec — https://docs.docker.com/reference/cli/docker/container/exec/
- MySQL Reference Manual: What is MySQL? — https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html
- CREATE DATABASE Statement — https://dev.mysql.com/doc/refman/9.7/en/create-database.html
- CREATE TABLE Statement — https://dev.mysql.com/doc/refman/9.7/en/create-table.html
- DESCRIBE Statement — https://dev.mysql.com/doc/refman/9.7/en/describe.html
- Data Types — https://dev.mysql.com/doc/refman/9.7/en/data-types.html
- Integer Types — https://dev.mysql.com/doc/refman/9.7/en/integer-types.html
- Fixed-Point Types — https://dev.mysql.com/doc/refman/9.7/en/fixed-point-types.html
- The CHAR and VARCHAR Types — https://dev.mysql.com/doc/refman/9.7/en/char.html
- The DATE, DATETIME, and TIMESTAMP Types — https://dev.mysql.com/doc/refman/9.7/en/datetime.html
- MySQL Workbench: Data Modeling — https://dev.mysql.com/doc/workbench/en/wb-data-modeling.html
- Server SQL Modes — https://dev.mysql.com/doc/refman/9.7/en/sql-mode.html

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- RDBMS | A relational database management system is the server program, such as MySQL, that stores data as related tables and answers queries about it. | aka: relational database, relational database management system, relational model
- SQL | Structured Query Language is the standard language for describing, changing and asking questions of the data in a relational database. | aka: Structured Query Language
- Docker image | A read-only package of files and settings, such as mysql:9.7, from which containers are started. | aka: image, images, container image
- container | An isolated running process started from an image, with its own filesystem, which is deleted along with the container unless data is kept in a volume. | aka: containers, Docker container
- Docker volume | A named storage area managed by Docker and mounted into a container so the data outlives the container. | aka: named volume, volumes
- ERD | An entity relationship diagram draws each kind of thing as a box of attributes and each relationship as a line between boxes, before any table is created. | aka: entity relationship diagram, ER diagram, entity-relationship diagram
- crow's foot | The fork drawn at the "many" end of an ERD line, so a line with a single bar at customers and a fork at tickets reads as one customer to many tickets. | aka: crow's-foot notation

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Docker Desktop is installed but not running, or the container was never started after a reboot, so the client fails with a connection or "no such container" error; docker ps and docker start desk-mysql are the first checks.
- Git Bash on Windows gives "the input device is not a TTY" for docker exec -it (fixed with a winpty prefix) and can rewrite the /var/lib/mysql path in the docker run line (fixed with MSYS_NO_PATHCONV=1 in front).
- Forgetting the semicolon at the mysql> prompt: the prompt changes to -> and waits, and the learner thinks the client has hung.
- Re-running docker run for a container that already exists fails with a name conflict, and learners then delete the container and the volume together, losing the data they meant to keep.
- Using FLOAT for money, or VARCHAR for everything, and mixing up CHAR (fixed length) with VARCHAR (variable length); also reading VARCHAR(100) as 100 bytes when it counts characters.
- Reading an ERD line backwards: the crow's foot goes on the "many" end, and learners put the customer on the many side of customers to tickets.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- 01-mysql-in-docker: show docker ps and docker volume ls right after docker run, so the container, the 3306 mapping and the desk-data volume are seen as separate things before the client opens.
- 01-mysql-in-docker: type SELECT VERSION(); at the mysql> prompt, then leave out the semicolon once on purpose so the room sees the -> continuation prompt.
- 02-desk-schema: draw the ERD of customers, agents and tickets on the whiteboard before CREATE TABLE, with its two one-to-many lines (customers to tickets, agents to tickets), point at the crow's foot on each, and only then type the CREATE TABLE lines so every column traces to a box.
- 02-desk-schema: run sql/schema.sql twice with docker exec -i ... < sql/schema.sql and the redirect, then DESCRIBE tickets, so IF NOT EXISTS is visible on the second run and the three empty tables read back.
