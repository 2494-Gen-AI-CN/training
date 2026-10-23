# Exercise — A library schema in SQL

Week 3 · Day 1 · `week-03/day-1-sql-and-rdbms-intro` · ~45 min
Notes: [weeks/week-03/day-1-sql-and-rdbms-intro.html](https://2494-gen-ai-cn.github.io/training/weeks/week-03/day-1-sql-and-rdbms-intro.html) · Demos: [2494-Gen-AI-CN/demos](https://github.com/2494-Gen-AI-CN/demos)

## Task

A small library needs a database. Write `starter/library.sql`, a SQL file that creates a database `city_library` with three tables, choosing a type for every column from `INT`, `VARCHAR`, `CHAR`, `DECIMAL` and `DATETIME`. This file is the only thing you write. The tests run it inside your own `desk-mysql` container and read what MySQL built back from `information_schema.columns`, the server's own list of every column it holds. Do not add keys or rows: today is types only.

- `books`: `book_id` (whole number), `title` (text up to 200 characters), `isbn` (always exactly 13 characters), `price` (money, up to 9999.99)
- `members`: `member_id` (whole number), `name` (up to 100 characters), `email` (up to 100 characters), `country` (always a two-letter code such as `CA`), `joined_at` (date and time)
- `loans`: `loan_id`, `book_id` and `member_id` (whole numbers), `loaned_at` and `due_at` (date and time), `late_fee` (money, up to 999.99)

The file starts with `DROP DATABASE IF EXISTS city_library;`, then `CREATE DATABASE city_library;` and `USE city_library;`, so it can be run again and again. (Why not just `library`? In MySQL 9.7 `LIBRARY` is a reserved word, a word the SQL language keeps for itself, so `CREATE DATABASE library;` stops with `ERROR 1064`.) Put the columns in the order listed. Use the SQL style from the demos: keywords in capitals, lower snake case names, one column per line, every statement ending with `;`.

## Acceptance criteria

- [ ] `test_opens_with_drop_create_use`: the file's first three statements are `DROP DATABASE IF EXISTS city_library`, `CREATE DATABASE city_library` and `USE city_library`
- [ ] `test_books_columns`: `books` has its four columns with types `int`, `varchar(200)`, `char(13)`, `decimal(6,2)`
- [ ] `test_members_columns`: `members` has its five columns with the described types
- [ ] `test_loans_columns`: `loans` has its six columns with the described types
- [ ] `test_no_keys_yet`: the three tables exist and no column is marked as a key
- [ ] `test_tables_are_empty`: no rows are inserted
- [ ] `test_file_can_run_twice`: running the file a second time succeeds and leaves the same columns

When every box is ticked, `python -m pytest -q` reports 7 passed.

## Getting started

Run these from your clone of the training repo. They copy this exercise into your own repository (`<FirstnameLastname>`, the one you created in the Week 1 Git exercise) at the same path, and you work in that copy. The paths assume the two repositories sit side by side; adjust `..` if yours do not.

```
git pull
mkdir -p ../<FirstnameLastname>/week-03/day-1-sql-and-rdbms-intro
cp -r exercises/week-03/day-1-sql-and-rdbms-intro/* ../<FirstnameLastname>/week-03/day-1-sql-and-rdbms-intro/
cd ../<FirstnameLastname>/week-03/day-1-sql-and-rdbms-intro
docker ps                    # desk-mysql must be listed; if not: docker start desk-mysql
python -m pytest -q          # everything fails until you write starter/library.sql
```

Open `starter/library.sql`: it holds a header comment and the three opening lines as comments. Remove the `-- ` in front of those three lines, add the three `CREATE TABLE` statements, and run the tests as you go. The tests only touch the `city_library` database (they drop it and let your file rebuild it on every run), so your `ticket_desk` database is left alone.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `week-03/day-1-sql-and-rdbms-intro/` there.

## Hints

- Check your file by hand: `docker exec -i desk-mysql mysql -uroot -pdesk < starter/library.sql`, then `docker exec -it desk-mysql mysql -uroot -p city_library` and `DESCRIBE books;`. The `Type` column of `DESCRIBE` shows exactly what the tests compare against (`int`, `char(13)`, `decimal(6,2)`). In Git Bash, if the second command says `the input device is not a TTY`, put `winpty` in front of it.
- `CHAR(n)` is for a value that is always exactly `n` characters long (an ISBN, a country code); `VARCHAR(n)` is for text of varying length up to `n` characters (a title, a name, an email).
- `DECIMAL(p,s)` stores `p` digits in total, `s` of them after the point. The largest price, 9999.99, has 4 digits before the point and 2 after, so it needs 6 in total: `DECIMAL(6,2)`. Work out `late_fee` the same way. Money is never `FLOAT`, which stores an approximation.
- If a second run stops with `ERROR 1007 (HY000): Can't create database 'city_library'; database exists`, the `DROP DATABASE IF EXISTS city_library;` line is missing or still commented out.
