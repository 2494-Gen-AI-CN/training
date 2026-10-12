"""Week plans (D-0034): one plan per week before any day of the week is authored.

harness/plans/week-WW.md is written by harness/workflows/week-plan.js from args that only
`python harness/args_for.py <week> --plan` emits; args_for.py refuses day args until the plan exists
and passes harness/plan_check.py (escape: --no-plan, logged). Model tiers reach the workflow only
through args, so the tier names are checked on the args and statically on the script source.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from helpers import HARNESS, ROOT, TRAINER, curriculum, live_days, metrics

sys.path.insert(0, str(HARNESS))
import plan_check  # noqa: E402

PLANS = HARNESS / "plans"
WEEK_PLAN_JS = HARNESS / "workflows" / "week-plan.js"


def run_args(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HARNESS / "args_for.py"), *argv], capture_output=True, text=True, encoding="utf-8")


class PlanFileTests(unittest.TestCase):
    def test_every_live_day_week_has_a_plan(self):
        weeks = sorted({w["week"] for w, d, rel in live_days()})
        self.assertTrue(weeks, "no live day; nothing to check")
        for wn in weeks:
            with self.subTest(week=wn):
                self.assertTrue((PLANS / f"week-{wn:02d}.md").is_file(), f"week {wn} has a live day but no harness/plans/week-{wn:02d}.md")

    def test_every_plan_passes_plan_check(self):
        plans = sorted(PLANS.glob("week-*.md")) if PLANS.is_dir() else []
        self.assertTrue(plans, "no plan files under harness/plans/")
        for p in plans:
            with self.subTest(plan=p.name):
                problems = plan_check.check_plan(p, metrics()["demos"])
                self.assertEqual([], problems, "\n".join(problems))

    def test_plan_lists_every_subtopic_and_every_rung_starts_from_resolves(self):
        cur = curriculum()
        for p in sorted(PLANS.glob("week-*.md")) if PLANS.is_dir() else []:
            with self.subTest(plan=p.name):
                plan = plan_check.load_plan(p)
                wk = next(w for w in cur["weeks"] if w["week"] == plan["week"])
                covered = {(r["Day"], r["Subtopic"].strip().lower()) for r in plan["coverage"]}
                for d in wk["days"]:
                    if d.get("kind") == "holiday":
                        continue
                    for st in d["subtopics"]:
                        self.assertIn((d["id"], st.strip().lower()), covered, f"{d['id']} subtopic '{st}' not in the coverage map")
                self.assertTrue(plan["threads"], "plan needs at least one thread")
                for t in plan["threads"]:
                    prev = None
                    for r in t["rungs"]:
                        s = r["Starts from"]
                        if prev is None:
                            # first rung: cold, or a key that exists on disk (previous week's last rung)
                            ok = s == "cold" or (ROOT / s).is_file() or not TRAINER.exists()
                            self.assertTrue(ok, f"{t['id']} rung {r['Rung']}: Starts from {s} does not resolve")
                        else:
                            self.assertEqual(prev, s, f"{t['id']} rung {r['Rung']}: Starts from must be the previous rung's key")
                        prev = r["keyPath"]

    def test_template_has_every_section(self):
        text = (HARNESS / "templates" / "week-plan.md").read_text(encoding="utf-8")
        for s in plan_check.SECTIONS:
            self.assertIn(s, text)
        for cols in (plan_check.RUNG_COLS, plan_check.LADDER_COLS, plan_check.COVERAGE_COLS, plan_check.STANDALONE_COLS,
                     plan_check.SPOILER_COLS, plan_check.DEVIATION_COLS):
            self.assertIn("| " + " | ".join(cols) + " |", text)


class PlanArgsTests(unittest.TestCase):
    def test_plan_args_carry_tiers_and_days(self):
        res = run_args("1", "--plan", "--today", "2026-10-12")
        self.assertEqual(0, res.returncode, res.stderr)
        a = json.loads(res.stdout)
        for k in ("root", "today", "week", "days", "weekNotes", "metrics", "config", "models", "planFile", "template", "critic", "threads"):
            self.assertIn(k, a, f"plan args lack {k}")
        self.assertEqual("2026-10-12", a["today"])
        self.assertIn("week-plan", a["models"]["stages"])
        self.assertIn("week-plan-critic", a["models"]["stages"])
        self.assertEqual({"model", "effort"}, set(a["models"]["stages"]["week-plan"]))
        for d in a["days"]:
            for k in ("id", "date", "dateLabel", "subtopics", "status", "rel", "existingScripts"):
                self.assertIn(k, d, f"plan day {d.get('id')} lacks {k}")
        # same tiers as the day args carry (D-0026/D-0032: one source, config.json models)
        day = json.loads(run_args("1", "2", "--today", "2026-10-13", "--no-plan").stdout)
        self.assertEqual(day["models"], a["models"])
        self.assertTrue(a["threads"], "week 1 must have a thread in scope (config.json threads)")

    def test_plan_args_take_one_week_only(self):
        self.assertEqual(2, run_args("1", "2", "--plan").returncode)

    def test_day_args_are_gated_on_the_plan(self):
        # a week with no plan is BLOCKED; the escape is explicit and logged
        wk = next(w for w in curriculum()["weeks"] if not (PLANS / f"week-{w['week']:02d}.md").is_file())
        no_plan_week = str(wk["week"])
        slot = str(next(d["day"] for d in wk["days"] if d.get("kind") != "holiday"))
        res = run_args(no_plan_week, slot, "--today", "2026-10-19")
        self.assertEqual(2, res.returncode, res.stderr)
        self.assertIn("BLOCKED", res.stderr)
        self.assertIn("--no-plan", res.stderr)
        res = run_args(no_plan_week, slot, "--today", "2026-10-19", "--no-plan")
        self.assertEqual(0, res.returncode, res.stderr)
        self.assertIn("WARNING", res.stderr)
        a = json.loads(res.stdout)
        self.assertTrue(a["noPlan"])
        self.assertIsNone(a["weekPlan"])
        # a planned week passes the plan and the day's rows through
        for p in sorted(PLANS.glob("week-*.md")) if PLANS.is_dir() else []:
            plan = plan_check.load_plan(p)
            wk = next(w for w in curriculum()["weeks"] if w["week"] == plan["week"])
            for d in wk["days"]:
                if d.get("kind") == "holiday":
                    continue
                with self.subTest(day=d["id"]):
                    res = run_args(str(wk["week"]), str(d["day"]), "--today", "2026-10-12")
                    self.assertEqual(0, res.returncode, res.stderr)
                    a = json.loads(res.stdout)
                    self.assertFalse(a["noPlan"])
                    self.assertTrue(a["weekPlan"].endswith(f"harness/plans/week-{wk['week']:02d}.md"))
                    day = a["days"][0]
                    self.assertEqual(len(d["subtopics"]), len(day["weekPlanRows"]), "one coverage row per subtopic")
                    if d["demoFormat"] != "none":
                        self.assertTrue(day["threadRows"], "a demo day needs thread/standalone rows")
                        for r in day["threadRows"]:
                            self.assertIn("startsFrom", r)
                            self.assertTrue(r["startsFrom"] == "cold" or r["startsFrom"].startswith("trainer/"), r)
                    self.assertTrue(day["dayShape"].startswith(f"### {d['id']} —"))


class WeekPlanScriptTests(unittest.TestCase):
    def test_week_plan_js_spreads_a_tier_on_every_agent_call(self):
        src = WEEK_PLAN_JS.read_text(encoding="utf-8")
        self.assertIn("'week-plan'", src)
        self.assertIn("'week-plan-critic'", src)
        self.assertIn("escalateOn", src)
        chunks = re.split(r"\bagent\((?!\))", src)  # real calls carry a prompt; "agent()" in comments does not
        self.assertGreaterEqual(len(chunks) - 1, 2, "expected an author and a critic agent() call")
        for i, chunk in enumerate(chunks[1:], 1):
            self.assertIn("...tier(", chunk, f"agent() call #{i} in week-plan.js does not spread a tier(...)")
        self.assertIn("...tier('week-plan', pass)", src)
        self.assertIn("...tier('week-plan-critic')", src)
        self.assertTrue(src.lstrip().startswith("//") or src.lstrip().startswith("export const meta"), "script must start with meta")
        self.assertIn("export const meta", src)

    def test_day_fanout_reads_plan_rows(self):
        src = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")
        for needle in ("weekPlanRows", "threadRows", "startsFrom", "noPlan"):
            self.assertIn(needle, src, f"day-fanout.js must use {needle} from args (D-0034)")


if __name__ == "__main__":
    unittest.main()
