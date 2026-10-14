/* practice_browser.js — the browser half of the practice-task pass (D-0043). See harness/practice_browser.py,
   which serves this file as /__practice_browser.js next to the page.

   An agent runs ONE line in the page (…?run=1) with its JavaScript tool:

       await (await import("/__practice_browser.js")).default()

   and gets back a short JSON string. The full report stays in window.__practiceReport.

   For every task on the page it types the starter, the model answers and every case from /__cases.json into
   the task's editor, clicks Check, and reads what the page shows. "ok" is true when nothing is off AND every
   task line equals the line CPython produced (data.expected), so the browser and the contract tests agree. */
export default async function practicePass() {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const data = await (await fetch("/__cases.json")).json();
  const report = { ok: false, rel: data.rel, runtime: "", runs: 0, seconds: 0, lines: [], problems: [] };
  const problem = (id, what, r) => report.problems.push(
    id + ": " + what + (r ? " | page showed: " + (r.rows.map((x) => x.text).join(" ; ") || "(no rows)").slice(0, 240) + " | output: " + r.out.slice(-120) : ""));

  document.querySelector("section.practice").scrollIntoView({ block: "start", behavior: "instant" });
  const tasks = Array.from(document.querySelectorAll(".ix-task"));
  const t0 = performance.now();
  const editors = () => document.querySelectorAll(".ix-task .CodeMirror").length;
  while (editors() < tasks.length && performance.now() - t0 < 20000) await wait(100);
  if (editors() < tasks.length) problem("page", "the editors did not load: " + (tasks[0] ? tasks[0].querySelector(".run-editor").textContent : "no tasks"));
  if (tasks.length !== Object.keys(data.cases).length) problem("page", `${tasks.length} tasks on the page, ${Object.keys(data.cases).length} in practice_cases.py`);

  // Type code into a task's editor (null = leave what is there), click Check, read the rows the reader would see.
  const check = async (t, code) => {
    if (code != null) t.querySelector(".CodeMirror").CodeMirror.setValue(code.replace(/^\n/, ""));
    t.querySelector('[data-act="check"]').click();
    const s = performance.now();
    await wait(20);
    while (t.querySelector(".run-bar").classList.contains("running") && performance.now() - s < 60000) await wait(25);
    report.runs++;
    const rows = Array.from(t.querySelectorAll(".task-checks li")).map((li) => (
      { ok: li.className === "ok", label: li.textContent.slice(2).split(" — ")[0], text: li.textContent }));
    return { solved: t.classList.contains("solved"), rows, out: t.querySelector(".run-out").textContent };
  };

  const started = performance.now();
  if (!report.problems.length) {
    for (const t of tasks) {
      const id = t.dataset.id, c = data.cases[id];
      if (!c) { problem(id, "no cases for this task"); continue; }
      let r = await check(t, null);
      const starterSolved = r.solved;
      if (starterSolved) problem(id, "the starter is marked solved", r);

      r = await check(t, data.model);
      const labels = r.rows.map((x) => x.label);
      const modelOk = r.solved && r.rows.length > 0 && r.rows.every((x) => x.ok);
      if (!modelOk) problem(id, "the model answer is not marked solved", r);

      let acceptOk = 0;
      for (let i = 0; i < c.accept.length; i++) {
        r = await check(t, c.accept[i]);
        if (r.solved && r.rows.length === labels.length && r.rows.every((x) => x.ok)) acceptOk++;
        else problem(id, `right answer ${i} is not marked solved`, r);
      }

      const kills = Object.fromEntries(labels.map((l) => [l, 0]));
      let rejectOk = 0;
      for (let i = 0; i < c.reject.length; i++) {
        const [code, label] = c.reject[i];
        r = await check(t, code);
        const failed = r.rows.filter((x) => !x.ok).map((x) => x.label);
        failed.forEach((l) => { if (l in kills) kills[l]++; });
        const caught = !r.solved && (label === null
          ? failed.length === 1 && failed[0] === data.didNotRun && r.out.length > 0
          : failed.includes(label));
        if (caught) rejectOk++;
        else problem(id, `wrong answer ${i} was not caught by "${label === null ? "an error before the checks" : label}"`, r);
      }

      const line = `${id}: starter ${starterSolved ? "SOLVED" : "unsolved"}, model ${modelOk ? "pass" : "FAIL"}, ` +
        `right ${acceptOk}/${c.accept.length}, wrong caught ${rejectOk}/${c.reject.length}, per check ${Object.values(kills).join(" ")}`;
      report.lines.push(line);
      if (line !== data.expected[id]) problem(id, `differs from CPython, which gave: ${data.expected[id]}`);
      t.querySelector('[data-act="reset"]').click();
    }
  }
  await wait(600);   // let the editors' debounced save run, then leave no trace on this origin
  try { localStorage.removeItem("tc_practice"); } catch (e) {}
  report.seconds = Math.round((performance.now() - started) / 100) / 10;
  report.runtime = (document.querySelector(".run-ver") || {}).textContent || "";
  report.view = document.documentElement.getAttribute("data-view") || "full";
  report.browser = (navigator.userAgent.match(/(Chrome|Firefox|Edg)\/[\d.]+/g) || [navigator.userAgent]).pop();
  report.ok = report.problems.length === 0 && report.lines.length === Object.keys(data.expected).length;
  window.__practiceReport = report;
  return JSON.stringify(report);
}
