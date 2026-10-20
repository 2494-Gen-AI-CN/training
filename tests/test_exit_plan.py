"""Exit criteria in the week plan (D-0063): the '## Exit criteria map' section checked by harness/plan_check.py and
the exitGroup / exitRows args emitted by harness/args_for.py.

From curriculum exitCriteria.fromWeek every plan carries the map as its last section, with every criterion of the
week's group exactly once (mapped to a day of the week or deferred to a later week of the group). Earlier weeks
may omit it; a map present there is validated without the completeness rule. The fixtures are temp copies of
harness/plans/week-02.md with the registry patched to make week 2 active where a case needs it.
"""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from helpers import HARNESS, curriculum
from test_plans import run_args

sys.path.insert(0, str(HARNESS))
import build_index as bi  # noqa: E402
import exit_criteria  # noqa: E402
import plan_check  # noqa: E402

PLANS = HARNESS / "plans"
WEEK2 = PLANS / "week-02.md"
HEADING = "## Exit criteria map"
TABLE_HEAD = "| " + " | ".join(plan_check.EXIT_COLS) + " |\n|" + "---|" * len(plan_check.EXIT_COLS) + "\n"


def active_registry(from_week: int = 2) -> dict:
    """The real registry with fromWeek moved, so week 2 (qc1's last week) counts as active."""
    reg = copy.deepcopy(exit_criteria.registry(curriculum()))
    reg["fromWeek"] = from_week
    return reg


def row(c: dict, day: str, where: str, step: str) -> str:
    return f"| {c['id']} | {c['tier']} | {c['text']} | {day} | {where} | {step} |\n"


class ArgsTests(unittest.TestCase):
    def test_plan_args_carry_the_active_group(self):
        res = run_args("3", "--plan", "--today", "2026-10-20")
        self.assertEqual(0, res.returncode, res.stderr)
        g = json.loads(res.stdout)["exitGroup"]
        self.assertTrue(g["active"])
        self.assertEqual("qc2", g["id"])
        self.assertEqual(45, len(g["criteria"]))
        self.assertEqual("../../exit-criteria/qc-2-sql.html", g["pageRel"])
        for c in g["criteria"]:
            self.assertEqual({"id", "section", "tier", "text"}, set(c))

    def test_plan_args_before_from_week_are_inactive(self):
        res = run_args("1", "--plan", "--today", "2026-10-20")
        self.assertEqual(0, res.returncode, res.stderr)
        g = json.loads(res.stdout)["exitGroup"]
        self.assertFalse(g["active"])
        self.assertEqual(3, g["fromWeek"])
        self.assertIn("reason", g)

    def test_day_args_without_a_plan_carry_empty_exit_rows(self):
        res = run_args("3", "1", "--no-plan", "--today", "2026-10-20")
        self.assertEqual(0, res.returncode, res.stderr)
        a = json.loads(res.stdout)
        self.assertEqual([], a["days"][0]["exitRows"])
        self.assertTrue(a["exitGroup"]["active"])

    def test_day_args_from_a_plan_carry_exit_rows(self):
        res = run_args("2", "1", "--today", "2026-10-20")
        self.assertEqual(0, res.returncode, res.stderr)
        day = json.loads(res.stdout)["days"][0]
        self.assertIn("exitRows", day)
        self.assertIsInstance(day["exitRows"], list)

    def test_demos_args_carry_exit_rows_per_block(self):
        res = run_args("2", "--demos", "--today", "2026-10-20")
        if res.returncode != 0:
            self.skipTest(f"demos args refused: {res.stderr.strip().splitlines()[0] if res.stderr.strip() else res.returncode}")
        a = json.loads(res.stdout)
        self.assertTrue(a["blocks"])
        for b in a["blocks"]:
            self.assertIsInstance(b.get("exitRows"), list, f"block {b.get('name')} lacks exitRows")


class PlanCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WEEK2.read_text(encoding="utf-8")
        cls.plan = plan_check.load_plan(WEEK2)
        cls.group = exit_criteria.load_group("qc1")
        assert cls.group and cls.group["exists"], "qc1 source must be published"
        cls.by_day: dict[str, list[str]] = {}
        for b in plan_check.week_blocks(cls.plan):
            cls.by_day.setdefault(b["day"], []).append(b["name"])
        wk = next(w for w in curriculum()["weeks"] if w["week"] == 2)
        cls.ids = [d["id"] for d in bi.teaching_days(wk)]
        cls.td = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def problems(self, text: str, active: bool = False) -> list[str]:
        p = Path(self.td.name) / "week-02.md"
        p.write_text(text, encoding="utf-8")
        if active:
            with mock.patch.object(exit_criteria, "registry", return_value=active_registry(2)):
                return plan_check.check_plan(p)
        return plan_check.check_plan(p)

    def exit_problems(self, text: str, active: bool = False) -> list[str]:
        return [x for x in self.problems(text, active) if "exit map" in x or "Exit criteria map" in x]

    def with_map(self, rows: str) -> str:
        return self.text.rstrip() + "\n\n" + HEADING + "\n\n" + TABLE_HEAD + rows

    def complete_rows(self) -> str:
        """Every qc1 criterion mapped in-week: Where cycles through the day's walkthroughs, facilitation and notes-only."""
        out, i = [], 0
        for c in self.group["criteria"]:
            day = self.ids[i % len(self.ids)]
            choices = self.by_day.get(day, []) + list(plan_check.EXIT_WHERE)
            where = choices[i % len(choices)]
            step = str(1 + i % 6)
            out.append(row(c, day, where, step))
            i += 1
        return "".join(out)

    def test_section_may_be_absent_before_from_week(self):
        self.assertFalse(plan_check.load_plan(WEEK2)["exitMap"], "the committed week-02 plan carries no exit map")
        self.assertEqual([], self.exit_problems(self.text))

    def test_section_required_from_from_week(self):
        probs = self.problems(self.text, active=True)
        self.assertTrue(any(f"missing section '{HEADING}'" in x for x in probs), "\n".join(probs))

    def test_complete_map_passes(self):
        text = self.with_map(self.complete_rows())
        self.assertEqual([], self.exit_problems(text, active=True))
        self.assertEqual([], self.exit_problems(text))
        plan = plan_check.load_plan(Path(self.td.name) / "week-02.md")
        self.assertEqual(len(self.group["criteria"]), len(plan["exitMap"]))
        rows = plan_check.day_rows(plan, self.ids[0])["exitRows"]
        self.assertTrue(rows)
        self.assertTrue(all(r["Day"] == self.ids[0] for r in rows))
        self.assertEqual(plan_check.SECTIONS[-1], HEADING)

    def _one(self, c: dict, day: str, where: str, step: str, active: bool = True, text_override: str | None = None) -> list[str]:
        r = row(c, day, where, step)
        if text_override is not None:
            r = r.replace(f"| {c['text']} |", f"| {text_override} |", 1)
        return self.exit_problems(self.with_map(r), active)

    def test_unknown_id(self):
        c = dict(self.group["criteria"][0], id="qc1.agile.R99")
        probs = self._one(c, self.ids[0], "facilitation", "1", active=False)
        self.assertTrue(any("is not a criterion of qc1" in x and "exit_criteria.py show qc1" in x for x in probs), probs)

    def test_wrong_tier(self):
        c = dict(self.group["criteria"][0], tier="Stretch")
        probs = self._one(c, self.ids[0], "facilitation", "1", active=False)
        self.assertTrue(any("Tier is 'Required' in the source" in x for x in probs), probs)

    def test_altered_text(self):
        c = self.group["criteria"][0]
        probs = self._one(c, self.ids[0], "facilitation", "1", active=False, text_override=c["text"] + " and more")
        self.assertTrue(any("Criterion text differs from the source" in x for x in probs), probs)

    def test_text_comparison_is_lenient_on_case_and_quotes(self):
        c = self.group["criteria"][0]
        probs = self._one(c, self.ids[0], "facilitation", "1", active=False, text_override=c["text"].upper().replace("'", "’"))
        self.assertFalse(any("Criterion text differs" in x for x in probs), probs)

    def test_day_outside_the_week(self):
        c = self.group["criteria"][0]
        probs = self._one(c, "w03d1", "facilitation", "1", active=False)
        self.assertTrue(any("Day must be a day id of week 02" in x for x in probs), probs)

    def test_where_not_a_walkthrough_of_that_day(self):
        c = self.group["criteria"][0]
        other_day = self.ids[-1]
        wrong = self.by_day[other_day][0]
        self.assertNotIn(wrong, self.by_day[self.ids[0]])
        probs = self._one(c, self.ids[0], wrong, "1", active=False)
        self.assertTrue(any(f"Where '{wrong}' is not a walkthrough of {self.ids[0]}" in x for x in probs), probs)
        probs = self._one(c, self.ids[0], self.by_day[self.ids[0]][0], "1", active=False)
        self.assertEqual([], probs)

    def middle_week_registry(self) -> dict:
        """qc1 stretched to weeks 1-3 (qc2 moved to week 4) so week 2 is a MIDDLE week of its group."""
        reg = active_registry(2)
        reg["groups"][0]["weeks"] = [1, 2, 3]
        reg["groups"][1]["weeks"] = [4]
        return reg

    def test_deferral_outside_the_group(self):
        c = self.group["criteria"][0]
        p = Path(self.td.name) / "week-02.md"
        p.write_text(self.with_map(row(c, "week 05", "—", "—")), encoding="utf-8")
        with mock.patch.object(exit_criteria, "registry", return_value=self.middle_week_registry()):
            probs = [x for x in plan_check.check_plan(p) if "exit map row" in x]
        self.assertTrue(any("deferred to 'week 05', not a later week of qc1" in x for x in probs), probs)
        # a forward deferral to a later week of the group is fine on a middle week
        p.write_text(self.with_map(row(c, "week 03", "—", "—")), encoding="utf-8")
        with mock.patch.object(exit_criteria, "registry", return_value=self.middle_week_registry()):
            probs = [x for x in plan_check.check_plan(p) if "exit map row" in x]
        self.assertEqual([], probs)

    def test_week_nn_naming_this_week_is_refused(self):
        c = self.group["criteria"][0]
        probs = self._one(c, "week 02", "—", "—", active=False)
        self.assertTrue(any("'week 02' is this week" in x for x in probs), probs)

    def test_deferral_on_the_groups_last_week(self):
        self.assertEqual(2, self.group["lastWeek"])
        c = self.group["criteria"][0]
        probs = self._one(c, "week 03", "—", "—", active=False)
        self.assertTrue(any("week 02 is the last week of qc1; the group's last week may defer nothing" in x for x in probs), probs)

    def test_deferred_row_must_blank_where_and_step(self):
        c = self.group["criteria"][0]
        probs = self._one(c, "week 01", "facilitation", "2", active=False)
        self.assertTrue(any("'week NN' row (deferred or taught earlier) has Where and Notes step '—'" in x for x in probs), probs)

    def test_taught_earlier_outside_the_group(self):
        c = self.group["criteria"][0]
        reg = active_registry(2)
        reg["groups"][0]["weeks"] = [2]      # qc1 is week 2 alone; week 1 is in no group
        p = Path(self.td.name) / "week-02.md"
        p.write_text(self.with_map(row(c, "week 01", "—", "—")), encoding="utf-8")
        with mock.patch.object(exit_criteria, "registry", return_value=reg):
            probs = [x for x in plan_check.check_plan(p) if "exit map row" in x]
        self.assertTrue(any("'week 01' is not an earlier week of qc1" in x for x in probs), probs)

    def test_required_row_needs_a_notes_step_when_active(self):
        c = next(x for x in self.group["criteria"] if x["tier"] == "Required")
        probs = [x for x in self._one(c, self.ids[0], "facilitation", "—", active=True) if "Notes step" in x]
        self.assertTrue(any("Notes step must be a positive integer" in x for x in probs), probs)
        # below fromWeek a dash is allowed on any tier
        self.assertEqual([], [x for x in self._one(c, self.ids[0], "facilitation", "—", active=False) if "Notes step" in x])
        # a Preferred row may carry a dash while active
        pref = next(x for x in self.group["criteria"] if x["tier"] != "Required")
        self.assertEqual([], [x for x in self._one(pref, self.ids[0], "facilitation", "—", active=True) if "Notes step" in x])
        # zero is not a step
        self.assertTrue(any("Notes step must be a positive integer" in x for x in self._one(c, self.ids[0], "facilitation", "0", active=False)))

    def test_duplicate_id(self):
        c = self.group["criteria"][0]
        text = self.with_map(row(c, self.ids[0], "facilitation", "1") * 2)
        probs = self.exit_problems(text)
        self.assertTrue(any("listed twice" in x for x in probs), probs)

    def test_missing_criterion_when_active(self):
        rows = self.complete_rows().splitlines(keepends=True)
        dropped = self.group["criteria"][-1]["id"]
        text = self.with_map("".join(r for r in rows if dropped not in r))
        probs = self.exit_problems(text, active=True)
        self.assertTrue(any(f"exit map lacks {dropped}" in x and "EXIT DEFECT" in x for x in probs), probs)
        # the completeness rule does not apply below fromWeek
        self.assertEqual([], self.exit_problems(text))

    # ---- taught earlier: "week NN" of an EARLIER week of the group, validated against that week's plan under root

    def _root_with(self, week1_rows: str | None, week2_rows: str) -> Path:
        """A temp root holding harness/plans/week-01.md (real + map rows, or absent when None) and week-02.md (real + rows)."""
        root = Path(tempfile.mkdtemp(dir=self.td.name))
        plans = root / "harness" / "plans"
        plans.mkdir(parents=True)
        if week1_rows is not None:
            w1 = (PLANS / "week-01.md").read_text(encoding="utf-8").rstrip()
            if week1_rows:
                w1 += "\n\n" + HEADING + "\n\n" + TABLE_HEAD + week1_rows
            (plans / "week-01.md").write_text(w1 + "\n", encoding="utf-8")
        (plans / "week-02.md").write_text(self.with_map(week2_rows), encoding="utf-8")
        return root

    def _check_w2(self, root: Path, from_week: int = 1) -> list[str]:
        with mock.patch.object(exit_criteria, "registry", return_value=active_registry(from_week)):
            return [x for x in plan_check.check_plan(root / "harness" / "plans" / "week-02.md", root=root) if "exit map" in x]

    def test_last_week_passes_with_in_week_and_taught_earlier_rows(self):
        # qc1 = weeks 1-2, fromWeek 1: week 2 (the last week) lists every id, the first ten as taught in week 1
        crit = self.group["criteria"]
        w1_ids = [d["id"] for d in bi.teaching_days(next(w for w in curriculum()["weeks"] if w["week"] == 1))]
        week1 = "".join(row(c, w1_ids[i % len(w1_ids)], "facilitation", "1") for i, c in enumerate(crit[:10]))
        week2 = "".join(row(c, "week 01", "—", "—") for c in crit[:10])
        week2 += "".join(ln + "\n" for ln in self.complete_rows().splitlines() if not any(f"| {c['id']} |" in ln for c in crit[:10]))
        root = self._root_with(week1, week2)
        self.assertEqual([], self._check_w2(root))
        plan = plan_check.load_plan(root / "harness" / "plans" / "week-02.md")
        self.assertEqual(len(crit), len(plan["exitMap"]))
        self.assertEqual(10, sum(1 for r in plan["exitMap"] if r["Day"] == "week 01"))
        # a taught-earlier row never reaches a day's args
        for did in self.ids:
            self.assertTrue(all(r["Day"] == did for r in plan_check.day_rows(plan, did)["exitRows"]))

    def test_taught_earlier_needs_the_earlier_plan_to_map_it_in_week(self):
        c = self.group["criteria"][0]
        # the earlier plan carries a map, but not this id in-week (it defers it forward instead)
        other = self.group["criteria"][1]
        root = self._root_with(row(other, "w01d2", "facilitation", "1") + row(c, "week 02", "—", "—"), row(c, "week 01", "—", "—"))
        probs = self._check_w2(root, from_week=3)
        self.assertTrue(any("taught earlier in week 01, but that plan does not map it to a day of week 01" in x for x in probs), probs)
        # the earlier plan carries no map at all
        root = self._root_with("", row(c, "week 01", "—", "—"))
        probs = self._check_w2(root, from_week=3)
        self.assertTrue(any("does not map it to a day of week 01" in x for x in probs), probs)

    def test_taught_earlier_needs_the_earlier_plan_file(self):
        c = self.group["criteria"][0]
        root = self._root_with(None, row(c, "week 01", "—", "—"))
        probs = self._check_w2(root, from_week=3)
        self.assertTrue(any("harness/plans/week-01.md is missing or is not a plan" in x for x in probs), probs)

    def test_taught_earlier_row_counts_once_toward_completeness(self):
        # active last week: an id listed as taught earlier is neither "lacking" nor allowed a second in-week row
        c = self.group["criteria"][0]
        rows = "".join(ln + "\n" for ln in self.complete_rows().splitlines() if f"| {c['id']} |" not in ln)
        root = self._root_with(row(c, "w01d2", "facilitation", "1"), rows + row(c, "week 01", "—", "—"))
        self.assertEqual([], self._check_w2(root))
        root = self._root_with(row(c, "w01d2", "facilitation", "1"), rows + row(c, "week 01", "—", "—") + row(c, self.ids[0], "facilitation", "1"))
        probs = self._check_w2(root)
        self.assertTrue(any("listed twice" in x for x in probs), probs)


if __name__ == "__main__":
    unittest.main()
