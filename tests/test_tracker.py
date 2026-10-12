"""Work tracker (D-0035): tracker.html is generated from repo state and must never go stale.

harness/build_tracker.py rewrites only the data block of tracker.html; harness/log_run.py appends one
record per workflow run to harness/runs.jsonl. Every writer of tracked state (both workflows, build_index,
publish_demos, decisions/new) rebuilds the tracker, and the staleness test below catches anything else.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import HARNESS, ROOT, TRAINER, ParsedPage, curriculum, live_days, node_exe, run_node

sys.path.insert(0, str(HARNESS))
import build_tracker as bt  # noqa: E402
import log_run  # noqa: E402

TRACKER = ROOT / "tracker.html"
WORKFLOWS = HARNESS / "workflows"
INLINE_SCRIPT_RE = re.compile(r"<script>(.*?)</script>", re.S)


def shell_html() -> str:
    """tracker.html without its generated data block."""
    html = TRACKER.read_text(encoding="utf-8")
    return html[:html.index(bt.BEGIN)] + html[html.index(bt.END) + len(bt.END):]


@unittest.skipUnless(TRAINER.exists(), "trainer/ private repo not cloned here; the tracker cannot be rebuilt")
class TrackerDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = bt.collect()

    def test_tracker_block_in_sync(self):
        html = TRACKER.read_text(encoding="utf-8")
        self.assertIn(bt.BEGIN, html)
        self.assertIn(bt.END, html)
        self.assertEqual(bt.splice(html, bt.render(self.data)), html,
                         "tracker.html is stale — run: python harness/build_tracker.py")

    def test_render_is_deterministic_and_reads_no_clock(self):
        self.assertEqual(bt.render(), bt.render())
        src = (HARNESS / "build_tracker.py").read_text(encoding="utf-8")
        for clock in ("today()", ".now(", "time.time", "import datetime", "import time"):
            self.assertNotIn(clock, src, f"build_tracker.py must not read a clock ({clock}); the browser computes date-relative state")

    def test_shape_matches_the_curriculum(self):
        cur = curriculum()
        self.assertEqual(len(cur["weeks"]), len(self.data["weeks"]))
        days = [d for w in self.data["weeks"] for d in w["days"]]
        teaching = [d for d in days if d["kind"] != "holiday"]
        self.assertEqual(51, len(teaching))
        self.assertEqual(len(cur["holidays"]), len(days) - len(teaching))
        self.assertEqual(len(list(live_days())), sum(1 for d in teaching if d["status"] == "live"))
        for d in teaching:
            self.assertEqual({"research", "demos", "notes", "exercise", "runbook", "solutions", "published"}, set(d["a"]), d["id"])
            self.assertEqual({"planned", "scripts", "keys"}, set(d["a"]["demos"]), d["id"])
        for w, d, rel in live_days():
            td = next(x for x in teaching if x["id"] == d["id"])
            self.assertTrue(td["a"]["research"] and td["a"]["notes"] and td["a"]["exercise"] and td["a"]["runbook"], f"{d['id']} is live but an artifact is missing")

    def test_status_and_stages_are_parsed(self):
        text = (ROOT / "STATUS.md").read_text(encoding="utf-8")
        st = self.data["status"]
        self.assertTrue(st["phase"])
        self.assertRegex(st["updated"] or "", r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(len(re.findall(r"^\| \d+ \| ", text, re.M)), len(st["milestones"]))
        self.assertEqual(sorted(set(re.findall(r"^\| (O-\d+) \| ", text, re.M))), sorted(i["id"] for i in st["openItems"]))
        self.assertTrue(any(i["due"] for i in st["openItems"] if not i["closed"]), "no open item has a readable due date")
        self.assertTrue(st["log"])
        self.assertGreaterEqual(len(self.data["stages"]), 5)
        self.assertTrue(any(s["done"] for s in self.data["stages"]))
        self.assertEqual(len(list((ROOT / "decisions").glob("D-*.md"))), self.data["decisions"]["count"])
        for row in self.data["decisions"]["latest"]:
            self.assertTrue((ROOT / "decisions" / row["file"]).is_file(), row)

    def test_threads_follow_the_plans(self):
        self.assertTrue(self.data["threads"], "config.json threads is empty")
        for t in self.data["threads"]:
            self.assertEqual(t["planned"], len(t["rungs"]))
            self.assertTrue(t["chainOk"], f"thread {t['id']}: a rung no longer extends its Starts from key")
            for r in t["rungs"]:
                if r["authored"]:
                    self.assertEqual("ok", r["chain"], r)


class RunLogTests(unittest.TestCase):
    def test_every_record_is_valid(self):
        runs = log_run.read_runs()
        self.assertTrue(runs, "harness/runs.jsonl is empty")
        cur = curriculum()
        for i, r in enumerate(runs):
            with self.subTest(run=i):
                self.assertEqual(log_run.FIELDS, list(r), "record keys must be the normalized set, in order")
                self.assertEqual([], log_run.validate(r, cur))
                self.assertEqual(r, log_run.normalize(r))

    def test_every_live_day_and_every_plan_has_a_record(self):
        runs = log_run.read_runs()
        recorded_days = {d for r in runs for d in r["days"]}
        for w, d, rel in live_days():
            self.assertIn(d["id"], recorded_days, f"{d['id']} is live but no run in harness/runs.jsonl names it")
        planned_weeks = {r["week"] for r in runs if r["kind"] == "week-plan"}
        for p in sorted((HARNESS / "plans").glob("week-*.md")):
            self.assertIn(int(p.stem.split("-")[1]), planned_weeks, f"{p.name} exists but no week-plan run is recorded")

    def test_add_and_amend_on_a_scratch_log(self):
        rec = {"kind": "day-fanout", "date": "2026-10-14", "week": 1, "days": ["w01d3"], "agents": 14,
               "tiers": {"labels": "demos=sonnet/medium", "verified": None},
               "artifacts": [{"day": "w01d3", "name": "research", "status": "done", "passes": 1}],
               "flagged": 0, "flags": [], "tests": None}
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            log = tmp / "runs.jsonl"
            report = tmp / "report.json"
            report.write_text(json.dumps(rec), encoding="utf-8")
            out = log_run.add(report, path=log)
            self.assertFalse(report.exists(), "the temp report is consumed")
            self.assertEqual(log_run.FIELDS, list(out))
            self.assertIsNone(out["runId"])
            amended = log_run.amend(-1, {"runId": "wf_0123abcd-9ef", "tests": "pass", "tiersVerified": True, "minutes": 31.5},
                                    path=log, match_days=["w01d3"])
            self.assertEqual(("wf_0123abcd-9ef", "pass", True, 31.5),
                             (amended["runId"], amended["tests"], amended["tiers"]["verified"], amended["minutes"]))
            self.assertEqual(1, len(log_run.read_runs(log)))
            with self.assertRaises(SystemExit):          # --last must not amend another run's record
                log_run.amend(-1, {"tests": "fail"}, path=log, match_days=["w01d4"])
            for bad in ({**rec, "kind": "nightly"}, {**rec, "days": ["w09d9"]}, {**rec, "date": "14 Oct"},
                        {**rec, "tests": "green"}, {**rec, "days": []}):
                report.write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaises(SystemExit):
                    log_run.add(report, path=log)
            self.assertEqual(1, len(log_run.read_runs(log)), "a rejected record must not be appended")


class WiringTests(unittest.TestCase):
    """Static: every writer of tracked state rebuilds the tracker or records its run."""

    def test_workflows_record_their_run_and_rebuild(self):
        for name in ("day-fanout.js", "week-plan.js"):
            src = (WORKFLOWS / name).read_text(encoding="utf-8")
            with self.subTest(script=name):
                self.assertIn("phase('Record')", src)
                self.assertIn("log_run.py add harness/run-report.tmp.json", src)
                self.assertIn("build_tracker.py --check", src)
                self.assertIn("{ title: 'Record' }", src)
                self.assertRegex(src, r"label:\s*[`'][^`']*record[`'], phase:'Record', \.\.\.tier\('wire'\)")
        day = (WORKFLOWS / "day-fanout.js").read_text(encoding="utf-8")
        wire = day[day.index("WIRE step"):day.index("phase('Record')")]
        self.assertIn("build_tracker.py", wire, "the Wire step must rebuild the tracker after it changes curriculum status")
        self.assertLess(day.index("phase('Record')"), day.index("phase('Verify')"), "Record runs before Verify so the run-log test sees the record")
        self.assertIn("log_run.py amend --last --match-days", day, "Verify records the test result on this run's record")

    def test_state_writing_scripts_rebuild(self):
        for path in (HARNESS / "build_index.py", HARNESS / "publish_demos.py", HARNESS / "log_run.py", ROOT / "decisions" / "new.py"):
            with self.subTest(script=path.name):
                src = path.read_text(encoding="utf-8")
                self.assertRegex(src, r"(build_tracker|bt)\.build\(", f"{path.name} must rebuild tracker.html when it changes tracked state")

    def test_thresholds_come_from_config(self):
        cfg = json.loads((HARNESS / "config.json").read_text(encoding="utf-8"))["tracker"]
        for k in ("dayAmberDaysBeforeWeek", "dayRedDaysBeforeWeek", "planAmberDaysBeforeWeek", "planRedDaysBeforeWeek",
                  "closeAmberDays", "closeRedDays", "itemAmberDays"):
            self.assertIsInstance(cfg[k], int, k)
        self.assertGreater(cfg["dayAmberDaysBeforeWeek"], cfg["dayRedDaysBeforeWeek"])
        self.assertGreater(cfg["planAmberDaysBeforeWeek"], cfg["planRedDaysBeforeWeek"])


class TrackerPageTests(unittest.TestCase):
    def test_page_is_self_contained_and_off_the_site(self):
        self.assertTrue(TRACKER.is_file())
        self.assertFalse((ROOT / "docs" / "tracker.html").exists(), "the tracker is not part of the trainee site")
        ParsedPage(TRACKER)  # raises on unclosed tags
        shell = shell_html()
        for m in re.finditer(r"""(?:src|href)\s*=\s*["']([^"']+)["']|url\(\s*["']?([^"')]+)""", shell):
            target = m.group(1) or m.group(2)
            self.assertNotRegex(target, r"^(https?:)?//", f"tracker.html must not load anything from the network: {target}")
        for font in re.findall(r'url\("([^"]+\.woff2)"\)', shell):
            self.assertTrue((ROOT / font).is_file(), f"font {font} missing")

    @unittest.skipUnless(node_exe(), "node not found")
    def test_alarm_rules(self):
        """The previous-Friday readiness rule and the other alarms, on synthetic data, in the page's own JS."""
        scripts = [s for s in INLINE_SCRIPT_RE.findall(shell_html())]
        rules = {"dayAmberDaysBeforeWeek": 5, "dayRedDaysBeforeWeek": 3, "planAmberDaysBeforeWeek": 7, "planRedDaysBeforeWeek": 5,
                 "closeAmberDays": 1, "closeRedDays": 2, "itemAmberDays": 2}

        def day(i, date, status="planned", taught=None):
            return {"id": i, "slot": 1, "date": date, "kind": "lesson", "title": i, "status": status, "taught": taught, "demoFormat": "py",
                    "a": {"research": status == "live", "demos": {"planned": 2, "scripts": 2 if status == "live" else 0, "keys": 2 if status == "live" else 0},
                          "notes": status == "live", "exercise": status == "live", "runbook": status == "live", "solutions": False, "published": False}}

        def week(n, start, days, plan):
            return {"week": n, "start": start, "end": start, "plan": {"exists": plan, "ok": plan, "problems": 0, "path": ""}, "days": days}

        data = {
            "rules": rules, "threads": [{"id": "t", "chainOk": True}],
            "weeks": [week(1, "2026-10-12", [day("w01d2", "2026-10-13", "live"), day("w01d3", "2026-10-14")], True),
                      week(2, "2026-10-19", [day("w02d1", "2026-10-19")], False),
                      week(5, "2026-11-09", [day("w05d1", "2026-11-09")], False)],
            "status": {"openItems": [{"id": "O-1", "closed": False, "due": "2026-10-13"}, {"id": "O-2", "closed": True, "due": "2026-10-01"},
                                     {"id": "O-3", "closed": False, "due": None}]},
            "runs": [{"kind": "day-fanout", "week": 1, "days": ["w01d2"], "date": "2026-10-11", "flagged": 1, "resolved": False, "runId": "a"},
                     {"kind": "day-fanout", "week": 1, "days": ["w01d2"], "date": "2026-10-12", "flagged": 0, "resolved": False, "runId": "b"}],
        }
        prog = (
            "const vm=require('vm');let s='';process.stdin.setEncoding('utf8');process.stdin.on('data',c=>s+=c);"
            "process.stdin.on('end',()=>{const i=JSON.parse(s);const sb={window:{}};vm.runInNewContext(i.src,sb);const TR=sb.window.TR;"
            "const out={};i.dates.forEach(t=>{out[t]=TR.alerts(i.data,t).map(a=>a.level+' '+a.kind+' '+a.id);});"
            "out.next=TR.nextUp(i.data,'2026-10-14').d.id;out.missing=TR.missing(i.data.weeks[0].days[1]);"
            "process.stdout.write(JSON.stringify(out));});"
        )
        dates = ["2026-10-12", "2026-10-14", "2026-10-16", "2026-10-21"]
        out = json.loads(run_node(prog, json.dumps({"src": "\n".join(scripts), "data": data, "dates": dates})))
        mon, wed, fri, later = (out[d] for d in dates)
        # Monday of week 1: a week-1 day that is not live is already late; week 2 is a week away (plan due, days clear)
        self.assertIn("red day w01d3", mon)
        self.assertIn("amber plan week 2", mon)
        self.assertFalse([a for a in mon if "w02d1" in a or "w05d1" in a or "week 5" in a], mon)
        self.assertIn("amber item O-1", mon)
        self.assertFalse([a for a in mon if "O-2" in a or "O-3" in a], "closed and undated items never alarm")
        self.assertFalse([a for a in mon if " run " in a], "only the newest run per day counts, and it has no flags")
        # Wednesday before week 2: its days turn amber, the missing plan turns red, the taught day needs its close
        self.assertIn("amber day w02d1", wed)
        self.assertIn("red plan week 2", wed)
        self.assertIn("amber close w01d2", wed)
        self.assertIn("red item O-1", wed)
        # Friday before week 2: not live means late
        self.assertIn("red day w02d1", fri)
        self.assertIn("red close w01d2", fri)
        self.assertFalse([a for a in later if "w05d1" in a], "a day three weeks out raises no alarm")
        self.assertEqual("w01d3", out["next"])
        self.assertEqual(["research", "demos", "notes", "exercise", "runbook"], out["missing"])


if __name__ == "__main__":
    unittest.main()
