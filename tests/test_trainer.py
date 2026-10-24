"""Runbook contract (trainer/ is the private repo; those tests skip when it is absent) and the learner repo
convention the runbook prompts carry (D-0051, D-0068)."""

from __future__ import annotations

import json
import re
import subprocess
import unittest

import sys

from helpers import HARNESS, TRAINER, all_days, authored_days, load_json, metrics, week_demos

sys.path.insert(0, str(HARNESS))
import plan_check  # noqa: E402

CONFIG = load_json(HARNESS / "config.json")
REQUIRED = ["## Day at a glance", "## Objectives", "## Setup check", "## Notes page handoff",
            "## Common questions", "## If running long / short"]
# D-0068: the per-day exercise is gone; the slot it held is sprint / project work. Taught days keep the
# shape they were delivered with (their runbook is history), so either heading is accepted there.
SPRINT = "## Sprint / project work"
OLD_EXERCISE = "## Exercise briefing"
PRACTICE_KEYS = {"practice.py", "practice_cases.py"}


@unittest.skipUnless(TRAINER.exists(), "trainer/ private repo not cloned here")
class TrainerTests(unittest.TestCase):
    def test_every_authored_runbook(self):
        M = metrics()["runbook"]
        for w, d, rel in authored_days():  # D-0052: authored or live
            rb = TRAINER / rel / "runbook.md"
            with self.subTest(rel=rel):
                self.assertTrue(rb.exists(), f"missing {rb}")
                text = rb.read_text(encoding="utf-8")
                self.assertTrue(text.startswith(f"# {d['id']} runbook"), "first line must be '# <id> runbook'")
                for h in REQUIRED:
                    self.assertIn(h, text, f"missing heading {h}")
                # D-0027: header links every public artifact absolutely (trainer repo is separate)
                head = "\n".join(text.splitlines()[:4])
                self.assertIn(f"{CONFIG['siteUrl']}weeks/{rel}.html", head, "runbook header must link the notes page on the site")
                if week_demos(w["dir"]).is_dir():
                    self.assertIn("](../demos/)", head, "runbook header must link the week's walkthrough folder (D-0055)")
                if d.get("taught"):
                    self.assertTrue(SPRINT in text or OLD_EXERCISE in text, "taught runbook lost its hands-on section")
                else:
                    self.assertIn(SPRINT, text, f"missing heading {SPRINT} (D-0068)")
                    self.assertNotIn(OLD_EXERCISE, text, "the per-day exercise is gone (D-0068)")
                    self.assertNotRegex(head, r"Exercise:|\]\(solutions/\)", "line 3 links no exercise and no solutions/ (D-0068)")
                if d.get("feedback"):
                    self.assertIn("## Feedback form", text)
                if d["kind"] == "review":
                    self.assertIn("## Review agenda", text)
                # D-0055: one "## Demo: <walkthrough>.md" per block of the day in the week plan; concept days facilitate
                if d["demoFormat"] == "none":
                    self.assertNotRegex(text, re.compile(r"^## Demo", re.M), "demoFormat none: no Demo sections")
                    self.assertRegex(text, re.compile(r"^## Facilitation \d+: .+\(\d+ min\)", re.M), "demoFormat none day needs timed Facilitation sections")
                elif week_demos(w["dir"]).is_dir():
                    plan_file = HARNESS / "plans" / f"week-{w['week']:02d}.md"
                    blocks = plan_check.day_rows(plan_check.load_plan(plan_file), d["id"])["blockRows"] if plan_file.is_file() else []
                    self.assertTrue(blocks, f"{d['id']} has no block in the week plan")
                    for b in blocks:
                        self.assertRegex(text, re.compile(rf"^## Demo: {re.escape(b['name'])}\.md", re.M), f"no section for walkthrough {b['name']}.md")
                        self.assertTrue((week_demos(w["dir"]) / f"{b['name']}.md").is_file(), f"walkthrough {b['name']}.md missing on disk")
                # minutes table sums into the day band
                glance = text.split("## Day at a glance", 1)[1].split("\n## ", 1)[0]
                mins = [int(m) for m in re.findall(r"^\|[^|]*\|\s*(\d+)\s*\|", glance, re.M)]
                total = sum(mins[:-1]) if len(mins) > 1 and mins[-1] == sum(mins[:-1]) else sum(mins)
                self.assertTrue(M["dayMinutesMin"] <= total <= M["dayMinutesMax"], f"day sums to {total} min")

    def test_solutions_hold_practice_keys_only(self):
        """D-0068: trainer/<rel>/solutions/ keeps the practice answer key (D-0047) and nothing from the retired exercise."""
        for sol in TRAINER.glob("week-*/day-*/solutions"):
            with self.subTest(sol=sol.relative_to(TRAINER).as_posix()):
                files = {p.name for p in sol.iterdir() if p.is_file()}
                self.assertLessEqual(files, PRACTICE_KEYS, "only practice.py / practice_cases.py belong in solutions/")


class LearnerRepoTests(unittest.TestCase):
    """D-0051 (supersedes D-0037), D-0068: one public FirstnameLastname repo per trainee in the cohort organisation,
    recorded once in config.json learnerRepo and carried to the runbook author and critic through args."""

    def setUp(self):
        self.cfg = load_json(HARNESS / "config.json")
        self.lr = self.cfg["learnerRepo"]

    def test_config_records_the_convention(self):
        org = re.fullmatch(r"https://github\.com/([^/]+)/[^/]+", self.cfg["repoUrl"]).group(1)
        self.assertEqual(org, self.lr["org"], "learner repos live in the same organisation as the training repo")
        self.assertEqual("public", self.lr["visibility"])
        self.assertRegex(self.lr["name"], r"^[A-Za-z]+$", "the name placeholder is plain letters (it is quoted inside <...>)")
        for k in ("nameRule", "createdIn", "handIn"):
            self.assertTrue(self.lr.get(k), f"learnerRepo lacks {k}")
        self.assertIn("PascalCase", self.lr["nameRule"])
        self.assertIn("hyphen or underscore", self.lr["nameRule"], "the rule tolerates a separator between the names")
        self.assertEqual({"root", "codeAlong", "scratch", "hackathon"}, set(self.lr["layout"]), "no exercises folder (D-0068)")
        self.assertIn(self.lr["createdIn"], {d["id"] for w, d, rel in all_days()}, "createdIn must be a curriculum day id")

    def test_args_carry_it_to_the_workflows(self):
        w, d, rel = next(all_days())
        for argv in ((str(w["week"]), str(d["day"]), "--no-plan"), (str(w["week"]), "--plan")):
            with self.subTest(argv=argv):
                res = subprocess.run([sys.executable, str(HARNESS / "args_for.py"), *argv, "--today", "2026-10-12"],
                                     capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(0, res.returncode, res.stderr)
                self.assertEqual(self.lr, json.loads(res.stdout)["config"]["learnerRepo"])

    def test_day_fanout_quotes_it_to_the_runbook_agents_only(self):
        src = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")
        self.assertIn("CFG.learnerRepo", src)
        header = src[src.index("const dayHeader"):src.index("const LR = ")]
        self.assertNotRegex(header, r"\$\{[^}]*(LR\b|learner)", "dayHeader reaches research, demo and notes prompts; keep the learner repo out of it")
        self.assertEqual(2, src.count("${learnerCtx(d)}"), "runbook author + critic only (D-0068)")
        for chunk in src.split("agent(")[1:]:
            if "${learnerCtx(d)}" in chunk.split("{ schema:")[0]:
                self.assertRegex(chunk, r"label:`\$\{d\.id\}:runbook", "learnerCtx belongs to the runbook prompts only")

    def test_templates_and_critics_name_it(self):
        self.assertIn(f"<{self.lr['name']}>", (HARNESS / "templates" / "runbook.md").read_text(encoding="utf-8"))
        text = (HARNESS / "critics" / "runbook.md").read_text(encoding="utf-8")
        self.assertIn("D-0051", text)
        self.assertIn(f"<{self.lr['name']}>", text)


if __name__ == "__main__":
    unittest.main()
