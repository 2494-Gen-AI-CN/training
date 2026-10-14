#!/usr/bin/env python3
"""Browser pass for a day's practice tasks (D-0043, stdlib only). Driven by an agent session with browser tools.

tests/test_assets.py proves a page's task checks under CPython. This step proves them where a learner meets
them: the real page, the real editor and Check button, Pyodide in a browser. Run it whenever a page's practice
tasks, their checks, widgets.js or pyworker.js change.

Usage:
    python harness/practice_browser.py <week> <day> [--port 8124]

It first runs every case under CPython and stops if one is wrong. Then it serves docs/ on 127.0.0.1 plus TWO
extra URLs: /__cases.json, built from trainer/<rel>/solutions/practice.py and practice_cases.py together with
the outcome CPython gave for each task, and /__practice_browser.js, the driver in harness/practice_browser.js.
Nothing is written to either repo and the answers stay on this machine.

The agent then, with its browser tools (Claude in Chrome):
  1. opens the URL this script prints;
  2. runs this one line in that page with the JavaScript tool:
         await (await import("/__practice_browser.js")).default()
  3. reads the JSON it returns: "ok" must be true, which means no problem was found and every task line is the
     same as the CPython line printed below; a false "ok" lists what the page showed under "problems";
  4. stops this server and records the result in STATUS.md.

The driver types every case into the task's editor and clicks Check. It runs on its own port so the saved work
of whoever previews the site on another port is left alone, and it resets the tasks and clears its own storage
when it ends.
"""
from __future__ import annotations

import ast
import functools
import http.server
import json
import re
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402
import notes_check as nc  # noqa: E402

ROOT = bi.ROOT
TRAINER = ROOT / "trainer"
DID_NOT_RUN = "The checks did not run"   # the row widgets.js shows when the code stops with an error


def locate(week_no: int, day_no: int) -> str:
    week = next(w for w in bi.load_curriculum()["weeks"] if w["week"] == week_no)
    day = next(d for d in week["days"] if d["day"] == day_no)
    if day.get("kind") == "holiday":
        raise SystemExit(f"week {week_no} day {day_no} is a holiday")
    return f"{week['dir']}/{day['slug']}"


def runner() -> dict:
    """The Python runner pyworker.js ships to the browser (the same source tests/test_assets.py loads)."""
    js = (ROOT / "docs" / "assets" / "js" / "pyworker.js").read_text(encoding="utf-8")
    g: dict = {}
    exec(re.search(r"const RUNNER = `(.*?)`;", js, re.S).group(1), g)
    return g


def check(g: dict, code: str, checks: str) -> tuple[bool, list[dict]]:
    finished = g["_tc_run"](lambda kind, text: None, code, [])
    return finished, (json.loads(g["_tc_check"](checks)) if finished else [])


def task_line(tid: str, starter_solved: bool, model_ok: bool, accept_ok: int, accepts: int, reject_ok: int, rejects: int, kills: list[int]) -> str:
    """One line per task; practice_browser.js builds the same line from what the page shows. "per check" is how
    many wrong answers fail each check, in page order. No key=value pairs: a browser tool may withhold output
    that looks like a query string."""
    return (f"{tid}: starter {'SOLVED' if starter_solved else 'unsolved'}, model {'pass' if model_ok else 'FAIL'}, "
            f"right {accept_ok}/{accepts}, wrong caught {reject_ok}/{rejects}, per check {' '.join(str(k) for k in kills)}")


def expected(rel: str) -> tuple[dict, list[str]]:
    """({model, cases, expected: {task id: line}}, problems) from the page and the trainer's files, under CPython."""
    sol = TRAINER / rel / "solutions"
    page = nc.parse_html((ROOT / "docs" / "weeks" / f"{rel}.html").read_text(encoding="utf-8"))
    tasks = page.find_all("div", "ix-task")
    if not tasks:
        raise SystemExit(f"{rel}: the page has no practice tasks")
    for name in ("practice.py", "practice_cases.py"):
        if not (sol / name).is_file():
            raise SystemExit(f"missing {sol / name}")
    model = (sol / "practice.py").read_text(encoding="utf-8")
    cases = runpy.run_path(str(sol / "practice_cases.py"))["CASES"]
    g, lines, problems = runner(), {}, []
    for t in tasks:
        tid, source = t.attrs["data-id"], t.find("pre", "task-tests").text()
        starter = t.find("pre", "task-starter").text().strip("\n") + "\n"
        labels = [n.msg.value for n in ast.parse(source).body if isinstance(n, ast.Assert)]
        solved = lambda fr: fr[0] and bool(fr[1]) and all(r["ok"] for r in fr[1])   # noqa: E731
        kills = {label: 0 for label in labels}
        accept_ok = sum(solved(check(g, code, source)) for code in cases[tid]["accept"])
        reject_ok = 0
        for code, label in cases[tid]["reject"]:
            finished, results = check(g, code, source)
            failed = [r["label"] for r in results if not r["ok"]]
            for x in failed:
                if x in kills:
                    kills[x] += 1
            reject_ok += (not finished) if label is None else (finished and label in failed)
        line = task_line(tid, solved(check(g, starter, source)), solved(check(g, model, source)),
                         accept_ok, len(cases[tid]["accept"]), reject_ok, len(cases[tid]["reject"]), list(kills.values()))
        lines[tid] = line
        want = task_line(tid, False, True, len(cases[tid]["accept"]), len(cases[tid]["accept"]),
                         len(cases[tid]["reject"]), len(cases[tid]["reject"]), list(kills.values()))
        if line != want or 0 in kills.values():
            problems.append(line)
    return {"rel": rel, "didNotRun": DID_NOT_RUN, "model": model, "cases": cases, "expected": lines}, problems


def main(argv: list[str]) -> int:
    port = 8124
    if "--port" in argv:
        port = int(argv[argv.index("--port") + 1])
        argv = [a for i, a in enumerate(argv) if a != "--port" and (i == 0 or argv[i - 1] != "--port")]
    if len(argv) != 2:
        print(__doc__)
        return 2
    rel = locate(int(argv[0]), int(argv[1]))
    data, problems = expected(rel)
    print(f"CPython, {rel}:")
    for line in data["expected"].values():
        print("  " + line)
    if problems:
        print("STOP: these tasks are not right under CPython (fix them and run the contract tests first):")
        for line in problems:
            print("  " + line)
        return 1
    extra = {
        "/__cases.json": ("application/json", json.dumps(data).encode("utf-8")),
        "/__practice_browser.js": ("text/javascript", (ROOT / "harness" / "practice_browser.js").read_bytes()),
    }

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            hit = extra.get(self.path.split("?")[0])
            if hit is None:
                super().do_GET()
                return
            self.send_response(200)
            self.send_header("Content-Type", hit[0])
            self.send_header("Content-Length", str(len(hit[1])))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(hit[1])

        def log_message(self, *args):   # keep the terminal for the lines above
            pass

    print(f"Open in the browser:  http://127.0.0.1:{port}/weeks/{rel}.html")
    print('Then run in that page:  await (await import("/__practice_browser.js")).default()')
    print("Ctrl+C stops this server.", flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Handler, directory=str(ROOT / "docs"))).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
