/* widgets.js — small inline learning widgets for notes pages.
   Declared via markup; auto-initialized on DOMContentLoaded. Pure client-side.

   1. Interaction legend:   <div class="ix-legend"></div>
   2. Predict-then-reveal:  <div class="ix-predict" data-q="..." data-a="..."></div>
   3. Spot-the-problem:     <div class="ix-spot" data-snippet="..." data-q="..." data-a="..."></div>
   4. Runnable block:       <pre data-run="python"><code>...</code></pre>   (D-0042)
      Add data-continues when the block uses names from the runnable block above it. Run, Edit and Reset
      appear under the block.
   5. Practice task:        <div class="ix-task" data-id="t1" data-title="..." data-q="...">   (D-0043)
                              <pre class="task-starter"><code>...</code></pre>
                              <pre class="task-tests" hidden><code>assert ..., "label"</code></pre>
                            </div>
      Tasks sit in <section class="practice" hidden>. The reader types a solution, runs it and checks it:
      every top-level assert in task-tests is one check and its message is the label shown.

   4 and 5 run Python in pyworker.js (Pyodide), fetched on the first Run or Check click, and edit in
   CodeMirror, fetched when an editor is first needed. A load failure is shown as it is; nothing falls back.
*/
(function () {
  const SELF = document.currentScript ? document.currentScript.src : "";
  const PY_LABEL = "Python 3.14";
  const RUN_LIMIT_MS = 10000;
  const CM_BASE = "https://cdn.jsdelivr.net/npm/codemirror@5.65.21/";
  const LSTASK = "tc_practice";
  const esc = (s) => (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  function predict(elist) {
    elist.forEach(el => {
      const q = el.dataset.q || "";
      const a = el.dataset.a || "";
      el.innerHTML =
        `<div class="ix-k">Predict</div><p class="ix-q">${q}</p>` +
        `<button class="ix-btn" type="button">Reveal answer</button>` +
        `<div class="ix-a">${a}</div>`;
      const btn = el.querySelector(".ix-btn"), ans = el.querySelector(".ix-a");
      btn.addEventListener("click", () => { ans.classList.add("show"); btn.style.display = "none"; });
    });
  }

  function spot(elist) {
    elist.forEach(el => {
      const snip = el.dataset.snippet || "", q = el.dataset.q || "What is the problem here?", a = el.dataset.a || "";
      el.innerHTML =
        `<div class="ix-k spot">🔍 Spot the problem</div>` +
        `<pre class="ix-snippet">${esc(snip)}</pre>` +
        `<p class="ix-q">${q}</p>` +
        `<button class="ix-btn" type="button">Reveal the problem</button>` +
        `<div class="ix-a">${a}</div>`;
      const btn = el.querySelector(".ix-btn"), ans = el.querySelector(".ix-a");
      btn.addEventListener("click", () => { ans.classList.add("show"); btn.style.display = "none"; });
    });
  }

  function legend(elist) {
    elist.forEach(el => {
      el.innerHTML =
        `<span class="ixl-lead">This page is interactive —</span>` +
        `<span class="ixl-chip">Predict</span>` +
        `<span class="ixl-chip">🔍 Spot the problem</span>` +
        `<span class="ixl-chip">✓ Check</span>` +
        (document.querySelector("pre[data-run]") ? `<span class="ixl-chip">▶ Run the code</span>` : "") +
        (document.querySelector(".ix-task") ? `<span class="ixl-chip">✎ Practice</span>` : "") +
        `<span class="ixl-chip">click diagram nodes</span>`;
    });
  }

  // ---- running Python (D-0042, D-0043) -----------------------------------------
  // One worker, one job at a time. A job is { id, code, prelude, tests, bar, out, onChecks }.
  // A failure is shown where the reader clicked and logged; nothing is retried.
  const py = { worker: null, job: null, queue: [], timer: 0, seq: 0 };

  function say(job, cls, text) {
    const span = document.createElement("span");
    if (cls) span.className = cls;
    span.textContent = text;
    job.out.appendChild(span);
  }

  // start a note on its own line when the output did not end with one
  const ownLine = (job, text) => (job.out.textContent && !job.out.textContent.endsWith("\n") ? "\n" : "") + text;

  function finish(job) {
    clearTimeout(py.timer);
    if (!job.out.textContent && job.tests == null) say(job, "info", "(no output)");
    job.bar.classList.remove("running");
    py.job = null;
    next();
  }

  function fail(text) {
    console.error("[run] " + text);
    const job = py.job;
    if (!job) return;
    job.out.textContent = "";
    say(job, "err", text);
    finish(job);
  }

  function onMessage(msg) {
    const job = py.job;
    if (!job || msg.id !== job.id) return;
    if (msg.type === "start") {
      job.out.textContent = "";
      py.timer = setTimeout(() => {
        py.worker.terminate();
        py.worker = null;
        say(job, "err", ownLine(job, `Stopped after ${RUN_LIMIT_MS / 1000} s.`));
        finish(job);
      }, RUN_LIMIT_MS);
    } else if (msg.type === "out" || msg.type === "err") {
      say(job, msg.type === "err" ? "err" : "", msg.text);
    } else if (msg.type === "cut") {
      say(job, "info", ownLine(job, "… output cut here"));
    } else if (msg.type === "checks") {
      job.onChecks(msg);
    } else if (msg.type === "done") {
      finish(job);
    } else if (msg.type === "fatal") {
      // Pyodide cannot run again after a fatal error (an endless recursion overflows the browser's stack),
      // so drop the worker: the next Run starts a fresh one instead of failing until the page is reloaded.
      py.worker.terminate();
      py.worker = null;
      fail(msg.text + "\n\nPython stopped. Endless recursion is the usual cause. Run again to restart it.");
    }
  }

  function next() {
    if (py.job || !py.queue.length) return;
    const job = py.job = py.queue.shift();
    job.bar.classList.add("running");
    job.out.textContent = "";
    try {
      if (!py.worker) {
        say(job, "info", `Loading ${PY_LABEL} (about 6 MB, once)…`);
        py.worker = new Worker(new URL("pyworker.js" + new URL(SELF).search, SELF), { type: "module" });
        py.worker.onmessage = (ev) => onMessage(ev.data);
        py.worker.onerror = (ev) => { py.worker = null; fail(ev.message || "pyworker.js could not be started"); };
      }
      py.worker.postMessage({ id: job.id, code: job.code, prelude: job.prelude, tests: job.tests });
    } catch (err) {
      fail(String(err));
    }
  }

  function submit(job) {
    job.id = ++py.seq;
    py.queue.push(job);
    next();
  }

  // ---- the editor (CodeMirror 5, fetched when an editor is first needed) --------
  let editorReady = null;

  function loadEditor() {
    if (editorReady) return editorReady;
    const add = (tag, attrs) => new Promise((ok, bad) => {
      const el = Object.assign(document.createElement(tag), attrs);
      el.onload = ok;
      el.onerror = () => bad(new Error("Could not load " + (attrs.src || attrs.href)));
      document.head.appendChild(el);
    });
    editorReady = Promise.all([
      add("link", { rel: "stylesheet", href: CM_BASE + "lib/codemirror.css" }),
      add("script", { src: CM_BASE + "lib/codemirror.js" }).then(() => Promise.all([
        add("script", { src: CM_BASE + "mode/python/python.js" }),
        add("script", { src: CM_BASE + "addon/edit/matchbrackets.js" }),
      ])),
    ]);
    return editorReady;
  }

  // An editor in host holding text. Ctrl+Enter calls onRun, Escape leaves the editor, Tab indents by 4 spaces.
  function mountEditor(host, text, onRun, onChange) {
    host.textContent = "";
    const cm = window.CodeMirror(host, {
      value: text, mode: "python", theme: "tc", lineNumbers: true, indentUnit: 4, tabSize: 4,
      matchBrackets: true, viewportMargin: Infinity,
      extraKeys: {
        Tab: (c) => c.execCommand(c.somethingSelected() ? "indentMore" : "insertSoftTab"),
        "Shift-Tab": "indentLess",
        "Ctrl-Enter": onRun, "Cmd-Enter": onRun,
        Esc: (c) => c.getInputField().blur(),
      },
    });
    if (onChange) cm.on("change", () => onChange(cm.getValue()));
    return cm;
  }

  function editorFailed(host, err) {
    console.error("[run] " + err.message);
    host.innerHTML = `<pre class="run-out"><span class="err">${esc(err.message)}</span></pre>`;
  }

  const runBar = (buttons) =>
    `<div class="run-bar">${buttons}<code class="run-ver">${PY_LABEL} · runs in your browser</code></div>` +
    `<pre class="run-out" aria-live="polite"></pre>`;

  // ---- 4. runnable blocks -------------------------------------------------------
  function run(elist) {
    const blocks = Array.from(elist).map(pre => ({ pre, src: pre.textContent.replace(/^\n/, "").replace(/\s+$/, ""), host: null, cm: null }));
    const text = (b) => (b.cm && !b.host.hidden ? b.cm.getValue().replace(/\s+$/, "") : b.src) + "\n";
    // A data-continues block runs after the runnable blocks above it, as the reader has them now.
    const prelude = (i) => {
      const out = [];
      for (let j = i; j > 0 && blocks[j].pre.hasAttribute("data-continues"); j--) out.unshift(text(blocks[j - 1]));
      return out;
    };

    blocks.forEach((b, i) => {
      b.pre.insertAdjacentHTML("afterend", runBar(
        `<button class="ix-btn run-go" type="button">▶ Run</button>` +
        `<button class="ix-btn run-alt" type="button" data-act="edit">Edit</button>` +
        `<button class="ix-btn run-alt" type="button" data-act="reset" hidden>Reset</button>`));
      const bar = b.pre.nextElementSibling, out = bar.nextElementSibling;
      const reset = bar.querySelector('[data-act="reset"]');

      const go = () => {
        reset.hidden = false;
        submit({ code: text(b), prelude: prelude(i), bar, out });
      };

      bar.querySelector(".run-go").addEventListener("click", go);
      bar.querySelector('[data-act="edit"]').addEventListener("click", () => {
        reset.hidden = false;
        if (b.host) { b.host.hidden = false; b.pre.hidden = true; if (b.cm) { b.cm.refresh(); b.cm.focus(); } return; }
        b.host = document.createElement("div");
        b.host.className = "run-editor ex";
        b.pre.insertAdjacentElement("beforebegin", b.host);
        loadEditor().then(() => {
          b.pre.hidden = true;
          b.cm = mountEditor(b.host, b.src, go);
          b.cm.focus();
        }, (err) => editorFailed(b.host, err));
      });
      reset.addEventListener("click", () => {
        if (b.cm) b.cm.setValue(b.src);
        if (b.host) b.host.hidden = true;
        b.pre.hidden = false;
        out.textContent = "";
        reset.hidden = true;
      });
    });
  }

  // ---- 5. practice tasks --------------------------------------------------------
  const store = {
    all() { try { return JSON.parse(localStorage.getItem(LSTASK) || "{}"); } catch (e) { return {}; } },
    put(key, rec) {
      try {
        const all = this.all();
        if (rec) all[key] = rec; else delete all[key];
        localStorage.setItem(LSTASK, JSON.stringify(all));
      } catch (e) {}
    },
  };

  function task(elist) {
    const els = Array.from(elist);
    if (!els.length) return;
    const section = els[0].closest(".practice");
    const page = (document.querySelector('meta[name="tc-day"]') || {}).content || location.pathname;
    const saved = store.all();

    const intro = document.createElement("p");
    intro.className = "practice-intro";
    els[0].insertAdjacentElement("beforebegin", intro);
    const progress = () => {
      intro.innerHTML = `${tasks.length} short tasks, one for each section above. Write the code, run it, then check it. ` +
        `Your work is kept in this browser. <b>${tasks.filter(t => t.solved).length} of ${tasks.length} solved</b>`;
    };

    const tasks = els.map((el, i) => {
      const key = page + ":" + el.dataset.id;
      const starter = el.querySelector(".task-starter").textContent.replace(/^\n/, "").replace(/\s+$/, "");
      const tests = el.querySelector(".task-tests").textContent;
      const was = saved[key] || {};
      const t = { starter, code: typeof was.code === "string" ? was.code : starter, solved: !!was.solved, cm: null };

      el.innerHTML =
        `<div class="ix-k">Task ${i + 1} <span class="ix-sub">· ${esc(el.dataset.title)}</span><span class="task-state"></span></div>` +
        `<p class="ix-q">${el.dataset.q || ""}</p>` +
        `<div class="run-editor"><pre><code>${esc(t.code)}</code></pre></div>` +
        runBar(
          `<button class="ix-btn run-go" type="button">▶ Run</button>` +
          `<button class="ix-btn run-go" type="button" data-act="check">✓ Check</button>` +
          `<button class="ix-btn run-alt" type="button" data-act="reset">Reset</button>`) +
        `<ul class="task-checks" aria-live="polite"></ul>`;
      t.host = el.querySelector(".run-editor");
      const bar = el.querySelector(".run-bar"), out = el.querySelector(".run-out");
      const checks = el.querySelector(".task-checks"), state = el.querySelector(".task-state");

      const paint = () => { state.textContent = t.solved ? "Solved ✓" : ""; el.classList.toggle("solved", t.solved); };
      const save = () => store.put(key, { code: t.code, solved: t.solved });
      const row = (ok, label, detail) => {
        const li = document.createElement("li");
        li.className = ok ? "ok" : "bad";
        li.textContent = (ok ? "✓ " : "✗ ") + label + (detail ? " — " + detail : "");
        checks.appendChild(li);
      };
      const onChecks = (msg) => {
        if (!msg.ran) row(false, "The checks did not run", "the code stopped with the error above");
        msg.results.forEach(r => row(r.ok, r.label, r.detail));
        t.solved = msg.ran && msg.results.length > 0 && msg.results.every(r => r.ok);
        paint(); save(); progress();
      };
      const go = (check) => {
        checks.textContent = "";
        submit({ code: t.code.replace(/\s+$/, "") + "\n", prelude: [], tests: check ? tests : undefined, bar, out, onChecks });
      };

      let timer = 0;
      t.mount = () => {
        t.cm = mountEditor(t.host, t.code, () => go(true), (value) => {
          t.code = value;
          clearTimeout(timer);
          timer = setTimeout(save, 400);
        });
      };

      bar.querySelector(".run-go").addEventListener("click", () => go(false));
      bar.querySelector('[data-act="check"]').addEventListener("click", () => go(true));
      bar.querySelector('[data-act="reset"]').addEventListener("click", () => {
        t.code = t.starter; t.solved = false;
        if (t.cm) t.cm.setValue(t.starter);
        else t.host.innerHTML = `<pre><code>${esc(t.starter)}</code></pre>`;
        clearTimeout(timer);   // setValue above queued a save of the starter
        store.put(key, null);
        out.textContent = ""; checks.textContent = "";
        paint(); progress();
      });
      paint();
      return t;
    });
    progress();

    // fetch the editor when the reader gets near the tasks, not on page load
    const near = new IntersectionObserver((entries) => {
      if (!entries.some(e => e.isIntersecting)) return;
      near.disconnect();
      loadEditor().then(() => tasks.forEach(t => t.mount()), (err) => tasks.forEach(t => editorFailed(t.host, err)));
    }, { rootMargin: "800px 0px" });
    near.observe(section);
  }

  // The practice section is hidden in the markup, so it stays out of the way where scripts do not run.
  // Show it now, before scrolly.js builds the table of contents.
  document.querySelectorAll("section.practice[hidden]").forEach(s => { s.hidden = false; });

  document.addEventListener("DOMContentLoaded", () => {
    legend(document.querySelectorAll(".ix-legend"));
    predict(document.querySelectorAll(".ix-predict"));
    spot(document.querySelectorAll(".ix-spot"));
    run(document.querySelectorAll('pre[data-run="python"]'));
    task(document.querySelectorAll(".practice .ix-task"));
  });
})();
