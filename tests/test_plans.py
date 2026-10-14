"""Week plans (D-0034): one plan per week before any day of the week is authored.

harness/plans/week-WW.md is written by harness/workflows/week-plan.js from args that only
`python harness/args_for.py <week> --plan` emits; args_for.py refuses day args until the plan exists
and passes harness/plan_check.py (escape: --no-plan, logged). Model tiers reach the workflow only
through args, so the tier names are checked on the args and statically on the script source.
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from helpers import HARNESS, ROOT, TRAINER, curriculum, live_days, metrics

sys.path.insert(0, str(HARNESS))
import args_for  # noqa: E402
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
                    if d["demoFormat"] not in ("none", "loose") or day["threadRows"]:
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


class WeekBatchTests(unittest.TestCase):
    """D-0038: one invocation authors the days of a week; demos in day order, the rest in parallel."""

    def test_demos_run_in_day_order_never_in_parallel(self):
        src = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")
        run = src[src.index("phase('Research')"):src.index("phase('Wire')")]
        calls = [m.start() for m in re.finditer(r"\b(researchStage|demosStage|materialsStage)\(d", run)]
        self.assertEqual(3, len(calls), "each stage is called once in the Run section")
        self.assertLess(run.index("phase('Demos')"), run.index("demosStage(d"))
        self.assertLess(run.index("demosStage(d"), run.index("phase('Materials')"), "every day's demos finish before any materials start")
        demos_part = run[run.index("phase('Demos')"):run.index("phase('Materials')")]
        self.assertNotIn("parallel(", demos_part, "a rung starts from the previous rung's key on disk (D-0033): demos are serial")
        self.assertRegex(demos_part, r"for \(const d of DAYS\)")
        self.assertIn("blockedBy", demos_part, "a day with no demo keys must block the later days of the run")

    def test_pages_of_one_batch_link_forward(self):
        wk = next(w for w in curriculum()["weeks"] if (PLANS / f"week-{w['week']:02d}.md").is_file())
        days = [d for d in wk["days"] if d.get("kind") != "holiday"]
        self.assertGreaterEqual(len(days), 2)
        res = run_args(str(wk["week"]), *[str(d["day"]) for d in days], "--today", "2026-10-12")
        self.assertEqual(0, res.returncode, res.stderr)
        out = json.loads(res.stdout)["days"]
        self.assertEqual([d["id"] for d in days], [d["id"] for d in out], "batch days come out in day order")
        for cur, nxt in zip(out, out[1:]):
            self.assertEqual(f"{nxt['slug']}.html", cur["nextHref"], f"{cur['id']} links to the next page of the same run")
        self.assertEqual("../../index.html", out[-1]["nextHref"], "the last day of a week points back at the program")
        # outside a batch and inside the week (releaseOnWire true), a day only links to a page that is already live
        # (D-0052: an authored next page is unreleased; NextLinkTests covers the authored-ahead case)
        alone = json.loads(run_args(str(wk["week"]), str(days[0]["day"]), "--today", "2026-10-12").stdout)["days"][0]
        expect = f"{days[1]['slug']}.html" if days[1].get("status") == "live" else "../../index.html"
        self.assertEqual(expect, alone["nextHref"])

    def test_series_review_runs_once_after_the_demos_loop(self):
        # D-0053: one series-review critic after every day's demos, only on a multi-day run; flags only
        src = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")
        demos_part = src[src.index("phase('Demos')"):src.index("phase('Materials')")]
        self.assertEqual(1, demos_part.count("tier('series-review')"), "exactly one series-review agent, in the Demos phase")
        self.assertEqual(1, src.count("tier('series-review')"))
        loop = demos_part.rindex("for (const d of DAYS)")
        call = demos_part.index("tier('series-review')")
        self.assertLess(loop, call, "the series review runs after the day-order demos loop")
        guard = demos_part.index("DAYS.length > 1")
        self.assertLess(loop, guard)
        self.assertLess(guard, call, "a single-day run has no series to review")
        self.assertIn("critics/series-review.md", demos_part)
        self.assertIn("series-review: ", src, "a FAIL reaches the run record's flags")
        self.assertIn("'series-review'", src[src.index("const TIER_LABELS"):src.index("const NOTES_ONLY")])
        self.assertTrue((HARNESS / "critics" / "series-review.md").is_file())
        cfg = json.loads((HARNESS / "config.json").read_text(encoding="utf-8"))
        self.assertIn("series-review", cfg["models"]["stages"])


class ReleaseOnWireTests(unittest.TestCase):
    """D-0052: the Wire step writes `live` once the week has started, `authored` when the week is authored ahead."""

    def _release(self, today: str) -> bool:
        res = run_args("1", "4", "--today", today)
        self.assertEqual(0, res.returncode, res.stderr)
        return json.loads(res.stdout)["releaseOnWire"]

    def test_true_on_or_after_the_weeks_monday(self):
        start = json.loads(run_args("1", "4", "--today", "2026-10-14").stdout)["weekStart"]
        self.assertEqual("2026-10-12", start)
        self.assertTrue(self._release("2026-10-14"))
        self.assertTrue(self._release(start))

    def test_false_before_the_weeks_monday(self):
        self.assertFalse(self._release("2026-10-09"))
        self.assertFalse(self._release("2026-10-11"))

    def test_today_must_be_an_iso_date(self):
        # a lexical compare would put "2026-10-5" after "2026-10-12" and release the week early
        for bad in ("2026-10-5", "14/10/2026", "tomorrow"):
            with self.subTest(today=bad):
                res = run_args("1", "4", "--today", bad)
                self.assertNotEqual(0, res.returncode, res.stdout)
                self.assertIn("YYYY-MM-DD", res.stderr)
        res = run_args("1", "--plan", "--today", "2026-10-5")
        self.assertNotEqual(0, res.returncode)


class NextLinkTests(unittest.TestCase):
    """D-0052: a page links forward to an authored (unlinked) next day only while it stays unreleased itself."""

    def _next_href(self, statuses: dict, day: int, today: str, *more: int) -> str:
        cur = copy.deepcopy(curriculum())
        wk = next(w for w in cur["weeks"] if w["week"] == 1)
        for d in wk["days"]:
            if d["day"] in statuses:
                d["status"] = statuses[d["day"]]
        out = io.StringIO()
        with mock.patch.object(args_for.bi, "load_curriculum", return_value=cur), contextlib.redirect_stdout(out):
            rc = args_for.main(["1", str(day), *map(str, more), "--today", today])
        self.assertEqual(0, rc)
        return json.loads(out.getvalue())["days"][0]["nextHref"]

    def test_authored_next_day(self):
        wk = next(w for w in curriculum()["weeks"] if w["week"] == 1)
        slug4 = next(d["slug"] for d in wk["days"] if d["day"] == 4) + ".html"
        index = "../../index.html"
        # inside the week (releaseOnWire true): this day goes live on Wire, so an authored next page is not linked
        self.assertEqual(index, self._next_href({3: "authored", 4: "authored"}, 3, "2026-10-14"))
        # before the week (releaseOnWire false): both pages stay unreleased, so the link is safe
        self.assertEqual(slug4, self._next_href({3: "authored", 4: "authored"}, 3, "2026-10-09"))
        # an already-live page never links into an authored one, even ahead of the week
        self.assertEqual(index, self._next_href({3: "live", 4: "authored"}, 3, "2026-10-09"))
        # a planned next day is never linked; a next day of the same run always is
        self.assertEqual(index, self._next_href({3: "authored", 4: "planned"}, 3, "2026-10-09"))
        self.assertEqual(slug4, self._next_href({3: "live", 4: "planned"}, 3, "2026-10-14", 4))
        # a live next day is linked whenever
        self.assertEqual(slug4, self._next_href({3: "live", 4: "live"}, 3, "2026-10-14"))

    def test_wire_never_points_a_live_page_at_an_authored_one(self):
        src = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")
        wire = src[src.index("WIRE step"):src.index("// ---------- report")]
        step4 = wire[wire.index("`4. "):wire.index("`5. ")]
        self.assertIn("A.releaseOnWire", step4)
        self.assertIn("leave its window.NEXT exactly as it is", step4)

    def test_wire_status_is_computed_per_day(self):
        # D-0052: Wire never downgrades a live day; the target status is computed per day in the script, not in prose
        src = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")
        self.assertIn("d.status === 'live' || A.releaseOnWire", src)
        self.assertLess(src.index("const WIRE_STATUS"), src.index("WIRE step"))
        wire = src[src.index("WIRE step"):src.index("// ---------- report")]
        step2 = wire[wire.index("`2. "):wire.index("`3. ")]
        self.assertIn("${J(WIRE_STATUS)}", step2)
        self.assertNotIn("A.releaseOnWire ?", step2, "one baked status for every day would downgrade a live day")


if __name__ == "__main__":
    unittest.main()
