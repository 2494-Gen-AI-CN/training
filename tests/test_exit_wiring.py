"""Exit criteria as a harness input (D-0063): static checks that day-fanout.js, demo-series.js, the critics and
the templates carry the week's exit group and the day's / block's exit rows to the right agents and no other."""

from __future__ import annotations

import re
import unittest

from helpers import HARNESS

FANOUT = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")
SERIES = (HARNESS / "workflows" / "demo-series.js").read_text(encoding="utf-8")
EXIT = "${exitCtx(d)}"


class DayFanoutTests(unittest.TestCase):
    def test_exit_ctx_is_defined_after_the_learner_repo(self):
        self.assertIn("const EG = A.exitGroup || {}", FANOUT)
        self.assertGreater(FANOUT.index("const exitCtx"), FANOUT.index("const LR = "), "exitCtx follows learnerCtx (dayHeader stays free of it)")
        body = FANOUT[FANOUT.index("const exitCtx"):FANOUT.index("async function researchStage")]
        for needle in ("EG.active", "d.exitRows", "EG.pageRel", "D-0063"):
            self.assertIn(needle, body)

    def test_exit_ctx_reaches_exactly_eight_prompts(self):
        self.assertEqual(8, FANOUT.count(EXIT), "research author+critic, depth author+critic, notes author+critic, runbook author+critic")
        seen = []
        for chunk in FANOUT.split("agent(")[1:]:
            if EXIT in chunk.split("{ schema:")[0]:
                m = re.search(r"label:`\$\{d\.id\}:([\w-]+)`", chunk)
                self.assertIsNotNone(m, "every exitCtx prompt is a labelled per-day agent")
                self.assertRegex(m.group(1), r"^(research|research-depth|notes|runbook)(-crit)?$", m.group(1))
                seen.append(m.group(1))
        self.assertEqual(sorted(seen), sorted(["research", "research-crit", "research-depth", "research-depth-crit", "notes", "notes-crit", "runbook", "runbook-crit"]))
        self.assertNotIn("label:`${d.id}:exercise", FANOUT, "the per-day exercise stage is gone (D-0068)")

    def test_humanize_and_verify_do_not_see_it(self):
        for start, end in (("const humanize = ", "const humanizeTrainer = "), ("const humanizeTrainer = ", "function demoFacts"), ("const notesVerify", "async function notesStage")):
            self.assertNotIn(EXIT, FANOUT[FANOUT.index(start):FANOUT.index(end)], start)

    def test_exit_step_map_is_wired(self):
        schema = FANOUT[FANOUT.index("const NOTES_SCHEMA"):FANOUT.index("const VERIFY_NOTES_SCHEMA")]
        self.assertIn("exitStepMap", schema)
        self.assertIn("required:['id','step']", schema)
        self.assertRegex(schema, r"required:\[[^\]]*'exitStepMap'[^\]]*\]")
        author = FANOUT[FANOUT.index("You are the NOTES-PAGE author"):FANOUT.index("NOTES CRITIC")]
        self.assertIn("exitStepMap (every exit row ID mapped to this day", author)
        wire = FANOUT[FANOUT.index("WIRE step"):FANOUT.index("// ---------- report")]
        self.assertIn("exitStepMaps", wire)
        self.assertIn("Exit criteria map", wire)
        self.assertIn("const exitStepMaps = perDay.filter(", FANOUT[FANOUT.index("const stepMaps"):FANOUT.index("const wire = ")])

    def test_notes_author_structure_bullets(self):
        author = FANOUT[FANOUT.index("You are the NOTES-PAGE author"):FANOUT.index("NOTES CRITIC")]
        for needle in ("../../exit-criteria/index.html", 'class="exit"', "Required exit criterion", "written from the day's Required exit criteria"):
            self.assertIn(needle, author)

    def test_critic_prompts_name_their_items(self):
        self.assertIn("Item 7c against the exit rows", FANOUT)
        self.assertIn("Item 21 against the exit rows (HARD, D-0063)", FANOUT)
        self.assertIn("Item 4 against the exit rows", FANOUT)
        self.assertIn("Exit criteria mapped to today", FANOUT[FANOUT.index("You are the RUNBOOK author"):FANOUT.index("RUNBOOK CRITIC")])


class DemoSeriesTests(unittest.TestCase):
    def test_block_rows_and_group_reach_the_demo_prompts(self):
        self.assertIn("A.exitGroup", SERIES[SERIES.index("const header"):SERIES.index("const blockCtx")])
        self.assertIn("b.exitRows", SERIES[SERIES.index("const blockCtx"):SERIES.index("const humanizeBlock")])
        author = SERIES[SERIES.index("You are the DEMO author"):SERIES.index("DEMOS CRITIC")]
        self.assertIn("every exit criterion row of this block is exercised in a named step", author)
        critic = SERIES[SERIES.index("DEMOS CRITIC"):SERIES.index("// =====", SERIES.index("DEMOS CRITIC"))]
        self.assertIn("(item 13)", critic)


class CriticAndTemplateTests(unittest.TestCase):
    def test_critics_carry_the_items(self):
        notes = (HARNESS / "critics" / "notes.md").read_text(encoding="utf-8")
        self.assertRegex(notes, re.compile(r"^21\. Exit criteria \(D-0063", re.M), "notes critic item 21")
        self.assertIn("exitStepMap", notes)
        demos = (HARNESS / "critics" / "demos.md").read_text(encoding="utf-8")
        self.assertRegex(demos, re.compile(r"^13\. Exit criteria \(D-0063", re.M), "demos critic item 13")
        research = (HARNESS / "critics" / "research.md").read_text(encoding="utf-8")
        self.assertRegex(research, re.compile(r"^7c\. Exit criteria \(D-0063", re.M), "research critic item 7c")
        self.assertGreater(research.index("7c."), research.index("7b."))
        runbook = (HARNESS / "critics" / "runbook.md").read_text(encoding="utf-8")
        self.assertIn("Exit criteria mapped to today", runbook)
        self.assertIn("D-0063", runbook)

    def test_templates_show_the_shape(self):
        research = (HARNESS / "templates" / "research.md").read_text(encoding="utf-8")
        self.assertIn("(qc", research[research.index("- Interview questions:"):research.index("- Adjacent concept:")])
        runbook = (HARNESS / "templates" / "runbook.md").read_text(encoding="utf-8")
        self.assertIn("| ID | Tier | Criterion | Where |", runbook[runbook.index("## Objectives"):runbook.index("## Setup check")])
        self.assertIn("Exit criteria mapped to today", runbook)


if __name__ == "__main__":
    unittest.main()
