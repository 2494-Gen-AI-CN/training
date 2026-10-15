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

    def test_plan_lists_every_subtopic_and_every_block_chains(self):
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
                prev_last = plan_check.previous_last_block(plan["week"])
                for t in plan["threads"]:
                    prev = None
                    for r in t["blocks"]:
                        s = r["Starts from"]
                        if prev is None:
                            # first block: cold, or the previous week's last walkthrough of the same thread
                            ok = s == "cold" or (plan_check.WALK_RE.match(s) and (t["id"] not in prev_last or prev_last[t["id"]] == s))
                            self.assertTrue(ok, f"{t['id']} block {r['Block']}: Starts from {s} does not resolve")
                        else:
                            self.assertEqual(prev, s, f"{t['id']} block {r['Block']}: Starts from must be the previous block's walkthrough")
                        prev = r["Walkthrough"]
                blocks = plan_check.week_blocks(plan)
                self.assertEqual([b["n"] for b in blocks], list(range(1, len(blocks) + 1)))
                for b in blocks:
                    self.assertTrue(b["stopPoint"], f"{b['name']} has no stop point")

    def test_template_has_every_section(self):
        text = (HARNESS / "templates" / "week-plan.md").read_text(encoding="utf-8")
        for s in plan_check.SECTIONS:
            self.assertIn(s, text)
        for cols in (plan_check.BLOCK_COLS, plan_check.LADDER_COLS, plan_check.COVERAGE_COLS, plan_check.STANDALONE_COLS,
                     plan_check.STOP_COLS, plan_check.SCAFFOLD_COLS, plan_check.NEVER_COLS, plan_check.SPOILER_COLS, plan_check.DEVIATION_COLS):
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
            for k in ("id", "date", "dateLabel", "subtopics", "status", "rel"):
                self.assertIn(k, d, f"plan day {d.get('id')} lacks {k}")
        for k in ("existingWalkthroughs", "demosDir", "prepBranch"):
            self.assertIn(k, a, f"plan args lack {k} (D-0055)")
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
                        self.assertTrue(day["blockRows"], "a demo day needs block rows (D-0055)")
                        for r in day["blockRows"]:
                            self.assertIn("startsFrom", r)
                            self.assertTrue(r["startsFrom"] == "cold" or plan_check.WALK_RE.match(r["startsFrom"]), r)
                            self.assertIn(r["slot"], ("AM", "PM"))
                            self.assertTrue(r["commitMessage"] or r["thread"] == "standalone", r)
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
        for needle in ("weekPlanRows", "blockRows", "startsFrom", "noPlan"):
            self.assertIn(needle, src, f"day-fanout.js must use {needle} from args (D-0034, D-0055)")


class WeekBatchTests(unittest.TestCase):
    """D-0038 / D-0055: one day-fanout invocation authors the materials of a week's days in parallel; demos are a
    separate weekly run (demo-series.js) whose blocks are authored serially in ladder order."""

    def test_day_fanout_has_no_demos_phase(self):
        src = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")
        self.assertNotIn("phase('Demos')", src, "demos left day-fanout.js (D-0055)")
        self.assertNotIn("publish_demos", src)
        self.assertNotIn("demo-card", src)
        self.assertNotIn("Demos today", src)
        self.assertNotIn("codePopups", src)
        self.assertLess(src.index("phase('Research')"), src.index("phase('Materials')"))

    def test_demo_series_runs_blocks_in_ladder_order_then_one_series_review(self):
        src = (HARNESS / "workflows" / "demo-series.js").read_text(encoding="utf-8")
        self.assertIn("export const meta", src)
        blocks_part = src[src.index("phase('Blocks')"):src.index("phase('Review')")]
        self.assertNotIn("parallel(", blocks_part, "a block starts from the previous block's commit: blocks are serial")
        self.assertRegex(blocks_part, r"for \(const b of BLOCKS\)")
        self.assertIn("blockedBy", blocks_part, "a block with no commit must block the later blocks of its thread")
        review_part = src[src.index("phase('Review')"):src.index("phase('Record')")]
        self.assertEqual(1, review_part.count("tier('series-review')"), "exactly one series-review agent, in the Review phase")
        self.assertEqual(1, src.count("tier('series-review')"))
        self.assertIn("A.seriesCritic", review_part, "the series critic path comes from args (harness/critics/series-review.md)")
        self.assertIn("series_readme.py", src)
        for stage in ("'demos'", "'demos-critic'", "'humanize'", "'series-review'", "'wire'", "'verify'", "'fix'"):
            self.assertIn(f"tier({stage}", src, f"demo-series.js must spread tier({stage})")
        chunks = re.split(r"\bagent\((?!\))", src)
        for i, chunk in enumerate(chunks[1:], 1):
            self.assertIn("...tier(", chunk, f"agent() call #{i} in demo-series.js does not spread a tier(...)")
        cfg = json.loads((HARNESS / "config.json").read_text(encoding="utf-8"))
        for stage in ("demos", "demos-critic", "series-review"):
            self.assertIn(stage, cfg["models"]["stages"])
        self.assertTrue((HARNESS / "critics" / "series-review.md").is_file())

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


class DemoSeriesArgsTests(unittest.TestCase):
    """D-0055: args_for.py <week> --demos emits the week's blocks in ladder order for demo-series.js."""

    def test_demos_args_carry_blocks_and_tiers(self):
        wk = next(w for w in curriculum()["weeks"] if (PLANS / f"week-{w['week']:02d}.md").is_file())
        res = run_args(str(wk["week"]), "--demos", "--today", "2026-10-15")
        if res.returncode != 0 and "research brief" in res.stderr:
            self.skipTest("the week's research briefs are not on disk")
        self.assertEqual(0, res.returncode, res.stderr)
        a = json.loads(res.stdout)
        for k in ("root", "today", "week", "weekDir", "blocks", "demosDir", "template", "critic", "seriesCritic", "weekPlan", "models", "config", "demoRepo", "prepBranch"):
            self.assertIn(k, a, f"demos args lack {k}")
        self.assertTrue(a["blocks"])
        self.assertEqual([b["n"] for b in a["blocks"]], list(range(1, len(a["blocks"]) + 1)))
        for b in a["blocks"]:
            for k in ("name", "day", "dayId", "slot", "minutes", "startsFrom", "adds", "endState", "commitMessage", "researchBrief", "stopPoint", "dateLabel"):
                self.assertIn(k, b, f"block {b.get('name')} lacks {k}")
            self.assertTrue(b["name"].startswith(f"{b['n']:02d}-"))
        self.assertIn("demos-critic", a["models"]["stages"])
        self.assertRegex(a["prepBranch"], r"^prep/week-\d{2}$")
        self.assertTrue(a["demosDir"].endswith(f"trainer/{a['weekDir']}/demos"))


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
