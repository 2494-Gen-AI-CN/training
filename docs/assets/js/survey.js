/* survey.js — weekly experience survey (offline fallback for the external feedback form).
   Page defines window.SURVEY = { week: "01", title, topics: [ "Day 1 — ...", ... ] }
   Captures per-topic minutes + difficulty + confidence plus weekly questions. localStorage only. */
(function () {
  const LSKEY = "tc_surveys";

  function save(rec) {
    try { const all = JSON.parse(localStorage.getItem(LSKEY) || "{}"); all[rec.id] = rec; localStorage.setItem(LSKEY, JSON.stringify(all)); } catch (e) {}
  }

  function scale(name, lo, hi) {
    const wrap = document.createElement("div"); wrap.className = "sv-scale";
    for (let i = 1; i <= 5; i++) {
      const l = document.createElement("label");
      l.innerHTML = `<input type="radio" name="${name}" value="${i}"><span>${i}</span>`;
      wrap.appendChild(l);
    }
    const cap = document.createElement("div"); cap.className = "sv-cap"; cap.innerHTML = `<span>${lo}</span><span>${hi}</span>`;
    const box = document.createElement("div"); box.appendChild(wrap); box.appendChild(cap);
    return box;
  }

  function render(host, S) {
    host.innerHTML = "";
    const h = document.createElement("h2"); h.textContent = S.title || `Week ${S.week} — How did it go?`; host.appendChild(h);
    const p = document.createElement("p"); p.style.color = "var(--ink-soft)"; p.style.marginTop = "-6px";
    p.textContent = "Two minutes. Honest numbers help us keep the pace right."; host.appendChild(p);

    const tbl = document.createElement("div"); tbl.className = "sv-table";
    const head = document.createElement("div"); head.className = "sv-row sv-head";
    head.innerHTML = "<div>Day / topic</div><div>Minutes on exercise</div><div>Difficulty (1 easy–5 hard)</div><div>Confidence after (1–5)</div>";
    tbl.appendChild(head);
    S.topics.forEach((t, i) => {
      const r = document.createElement("div"); r.className = "sv-row";
      const name = document.createElement("div"); name.textContent = t;
      const mins = document.createElement("input"); mins.type = "number"; mins.min = 0; mins.placeholder = "min"; mins.dataset.k = "min" + i;
      r.appendChild(name); r.appendChild(mins); r.appendChild(scale("diff" + i, "easy", "hard")); r.appendChild(scale("conf" + i, "lost", "solid"));
      tbl.appendChild(r);
    });
    host.appendChild(tbl);

    const wk = document.createElement("div"); wk.className = "sv-week";
    wk.innerHTML =
      '<div class="sv-q"><label>Overall pace this week</label>' +
        '<select data-k="pace"><option value="">—</option><option>Too slow</option><option>About right</option><option>Too fast</option></select></div>' +
      '<div class="sv-q"><label>Where did you get stuck?</label><textarea data-k="stuck" rows="2" placeholder="be specific"></textarea></div>' +
      '<div class="sv-q"><label>Anything confusing, broken, or missing in the materials?</label><textarea data-k="feedback" rows="2"></textarea></div>';
    host.appendChild(wk);

    const actions = document.createElement("div"); actions.className = "actions";
    const btn = document.createElement("button"); btn.className = "btn"; btn.textContent = "Save survey";
    const msg = document.createElement("span"); msg.className = "scorebox";
    actions.appendChild(btn); actions.appendChild(msg); host.appendChild(actions);

    btn.addEventListener("click", () => {
      const topics = S.topics.map((t, i) => ({
        topic: t,
        minutes: Number((tbl.querySelector(`[data-k="min${i}"]`) || {}).value || 0),
        difficulty: (host.querySelector(`input[name="diff${i}"]:checked`) || {}).value || null,
        confidence: (host.querySelector(`input[name="conf${i}"]:checked`) || {}).value || null
      }));
      const get = k => { const e = wk.querySelector(`[data-k="${k}"]`); return e ? e.value : null; };
      save({ id: `survey-w${S.week}`, type: "survey", week: S.week, topics, pace: get("pace"), stuck: get("stuck"), feedback: get("feedback"), ts: new Date().toISOString() });
      msg.textContent = "Saved locally ✓ — now submit the feedback form linked above."; msg.className = "scorebox pass";
      btn.disabled = true;
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    const host = document.getElementById("survey");
    if (host && window.SURVEY) render(host, window.SURVEY);
  });
})();
