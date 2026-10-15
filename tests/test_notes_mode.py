"""Notes-only mode, pinned tiers and the research brief's Notes depth section (D-0040). Static checks of
harness/args_for.py, harness/workflows/day-fanout.js, harness/config.json and the live briefs."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest

from helpers import HARNESS, ROOT, live_days

ARGS_FOR = HARNESS / "args_for.py"
FANOUT = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")
WEEK_PLAN = (HARNESS / "workflows" / "week-plan.js").read_text(encoding="utf-8")
CONFIG = json.loads((HARNESS / "config.json").read_text(encoding="utf-8"))


def _args(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ARGS_FOR), *argv], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)


class ArgsForTests(unittest.TestCase):
    def test_notes_only_args(self):
        r = _args("1", "2", "--notes-only", "--today", "2026-10-13")
        self.assertEqual(0, r.returncode, r.stderr)
        a = json.loads(r.stdout)
        self.assertTrue(a["notesOnly"])
        self.assertFalse(a["skipResearch"], "the research depth pass runs in a notes-only run")
        self.assertEqual("w01d2", a["days"][0]["id"])
        self.assertNotIn("existingScripts", a["days"][0], "D-0055: demos are a separate run; a notes-only run needs no scripts on disk")

    def test_template_override(self):
        r = _args("1", "2", "--notes-only", "--template", "harness/templates/day.exemplar.html", "--today", "2026-10-13")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertTrue(json.loads(r.stdout)["template"].endswith("harness/templates/day.exemplar.html"))
        self.assertEqual(2, _args("1", "2", "--template", "harness/templates/missing.html", "--today", "2026-10-13").returncode)

    def test_notes_only_needs_the_brief(self):
        # a day with no committed brief: week 3 is not authored yet (week 2's briefs now exist)
        r = _args("3", "1", "--no-plan", "--notes-only", "--today", "2026-10-13")
        self.assertEqual(2, r.returncode)
        self.assertIn("--notes-only needs an existing brief", r.stderr)


class WorkflowWiringTests(unittest.TestCase):
    def test_notes_only_branch(self):
        self.assertIn("const NOTES_ONLY = !!A.notesOnly", FANOUT)
        self.assertEqual(1, FANOUT.count("async function notesStage("))
        self.assertEqual(1, FANOUT.count("async function researchDepthStage("))
        self.assertIn("const notes = () => notesStage(d)", FANOUT, "materialsStage delegates to notesStage")
        self.assertIn("notes: await notesStage(d)", FANOUT, "the notes-only branch calls notesStage")
        self.assertNotIn("demosStage(", FANOUT, "demos left day-fanout.js (D-0055)")
        self.assertIn("researchDepthStage(d) : researchStage(d)", FANOUT)
        self.assertIn("'cached'", FANOUT[FANOUT.index("if (NOTES_ONLY) {", FANOUT.index("phase('Materials')")):])

    def test_notes_schema_and_author_prompt(self):
        schema = FANOUT[FANOUT.index("const NOTES_SCHEMA"):FANOUT.index("const VERIFY_NOTES_SCHEMA")]
        for key in ("h3Count", "interviewCount", "checkYourselfCount", "codeBlocks", "citations", "sourcesChecked", "stepMap"):
            self.assertIn(key, schema)
        author = FANOUT[FANOUT.index("You are the NOTES-PAGE author"):FANOUT.index("NOTES CRITIC")]
        for needle in ("notes_check.py", "Say it in an interview", "Check yourself", "deliveryPhrases", "Notes depth", "WRITE INCREMENTALLY",
                       "ONE Write of the whole shell", "Fill ONE step per Edit", "sup class=\"cite\"", "Sources checked", "stepMap", "...tier('notes', pass)"):
            self.assertIn(needle, author)
        self.assertNotIn("deepens what the trainer types live", author)

    def test_verify_agent_binds_the_critic(self):
        self.assertIn("const notesVerify = (d, pass) => agent(", FANOUT)
        crit = FANOUT[FANOUT.index("const v = await notesVerify(d, pass)"):FANOUT.index("async function materialsStage")]
        self.assertIn("...tier('notes-critic')", crit)
        for needle in ("structural", "dead link", "stale", "pass:false"):
            self.assertIn(needle, crit)
        verify = FANOUT[FANOUT.index("const notesVerify"):FANOUT.index("async function notesStage")]
        self.assertIn("notes_check.py", verify)
        self.assertIn("--links", verify)
        self.assertIn("WebFetch", verify)
        self.assertIn("'notes-verify-full' : 'notes-verify-light'", verify)

    def test_humanizer_is_prose_guarded(self):
        body = FANOUT[FANOUT.index("const humanize = "):FANOUT.index("const humanizeTrainer = ")]
        for needle in ("prose_guard.py snapshot", "prose_guard.py check", "one section.step", "notes_check.py", "...tier('humanize')"):
            self.assertIn(needle, body)

    def test_wire_realigns_the_coverage_map(self):
        wire = FANOUT[FANOUT.index("WIRE step"):FANOUT.index("// ---------- report")]
        self.assertIn("plan_check.py", wire)
        self.assertIn("Notes step", wire)
        self.assertIn("stepMaps", wire)

    def test_run_record_names_the_mode(self):
        self.assertIn("notes-only run (D-0040)", FANOUT[FANOUT.index("const runRecord"):])


class TierTests(unittest.TestCase):
    def test_every_stage_is_pinned(self):
        models = CONFIG["models"]
        self.assertTrue(models["escalate"].get("model") and models["escalate"].get("effort"))
        for name, t in models["stages"].items():
            with self.subTest(stage=name):
                self.assertIn(t.get("model"), ("sonnet", "haiku", "opus"), f"{name} must pin a model (D-0040)")
                self.assertIn(t.get("effort"), ("low", "medium", "high", "xhigh", "max"))

    def test_every_tier_call_names_a_configured_stage(self):
        stages = set(CONFIG["models"]["stages"])
        for src, label in ((FANOUT, "day-fanout.js"), (WEEK_PLAN, "week-plan.js")):
            used = set(re.findall(r"tier\('([\w-]+)'", src))
            self.assertTrue(used, label)
            self.assertEqual(set(), used - stages, f"{label} uses tiers config.json does not define")
        for name in ("notes-critic", "notes-verify-light", "notes-verify-full"):
            self.assertIn(name, FANOUT[FANOUT.index("const TIER_LABELS"):FANOUT.index("const NOTES_ONLY")])
        series = (HARNESS / "workflows" / "demo-series.js").read_text(encoding="utf-8")
        used = set(re.findall(r"tier\('([\w-]+)'", series))
        self.assertEqual(set(), used - stages, "demo-series.js uses tiers config.json does not define")
        for name in ("demos", "demos-critic", "series-review", "humanize"):
            self.assertIn(name, series[series.index("const TIER_LABELS"):series.index("const J = ")])


class LiveBriefTests(unittest.TestCase):
    def test_live_briefs_carry_notes_depth(self):
        for w, d, rel in live_days():
            brief = HARNESS / "research" / f"{rel}.md"
            with self.subTest(rel=rel):
                text = brief.read_text(encoding="utf-8")
                self.assertIn("## Notes depth", text)
                depth = text[text.index("## Notes depth"):]
                depth = depth[:depth.index("\n## ", 1)] if "\n## " in depth[1:] else depth
                heads = [h.strip().lower() for h in re.findall(r"^### (.+)$", depth, re.M)]
                for st in d["subtopics"]:
                    self.assertIn(st.strip().lower(), heads, f"{rel}: Notes depth lacks a block for {st!r}")
                for bullet in ("Interview questions:", "Adjacent concept:", "Trade-off or limit:", "Recognise on sight:", "Claims:"):
                    self.assertEqual(len(heads), depth.count(bullet), f"{rel}: every block needs '{bullet}'")


if __name__ == "__main__":
    unittest.main()
