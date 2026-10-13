/* pyworker.js — runs a notes page's Python in the reader's browser (D-0042, D-0043).
   A module worker started by widgets.js on the first Run or Check click; nothing here loads before that.
   The runtime is Pyodide (CPython on WebAssembly) from ONE pinned URL. tests/test_assets.py checks that the
   site's scripts load code from pinned jsDelivr packages only, and that this file names Pyodide alone.

   In:   { id, code, prelude, tests }     prelude = the runnable blocks a data-continues block builds on;
                                          tests   = a practice task's checks (omitted for a plain Run)
   Out:  { id, type: "start" }            the runtime is up and the code is about to run
         { id, type: "out" | "err", text }
         { id, type: "cut" }              output passed the cap; the rest is dropped
         { id, type: "checks", ran, results }   results = [{ ok, label, detail }]; ran is false when the
                                          code stopped with an error, and then no check was tried
         { id, type: "done" }
         { id, type: "fatal", text }      the runtime did not load or the runner itself failed (shown as is) */
const PYODIDE_BASE = "https://cdn.jsdelivr.net/npm/pyodide@314.0.7/";
const MAX_LINES = 200, MAX_CHARS = 20000;

// The code runs as a script would: a fresh namespace named __main__, its own source in linecache so a
// traceback shows the failing line, and a traceback that starts at the reader's code, not at this runner.
// tests/test_assets.py runs this same source under CPython against every practice task.
const RUNNER = `
import ast, io, json, linecache, sys, traceback

_tc_last = {}

class _TcStream(io.TextIOBase):
    def __init__(self, emit, kind):
        self._emit, self._kind = emit, kind
    def writable(self):
        return True
    def write(self, s):
        if s:
            self._emit(self._kind, s)
        return len(s)

def _tc_exec(src, name, ns):
    linecache.cache[name] = (len(src), None, src.splitlines(True), name)
    exec(compile(src, name, "exec"), ns)

def _tc_run(emit, src, prelude):
    """Run src as a script and report whether it got to its end. Its namespace stays in _tc_last."""
    global _tc_last
    name = "main.py"
    ns = _tc_last = {"__name__": "__main__"}
    finished = False
    real = sys.stdout, sys.stderr
    try:
        sys.stdout = sys.stderr = io.StringIO()
        for earlier in prelude:
            try:
                _tc_exec(earlier, name, ns)
            except BaseException:
                pass   # the block above may end in the error it demonstrates; its names are still defined
        sys.stdout, sys.stderr = _TcStream(emit, "out"), _TcStream(emit, "err")
        try:
            _tc_exec(src, name, ns)
            finished = True
        except SystemExit as exc:
            finished = exc.code is None or exc.code == 0
            if exc.code is not None and not isinstance(exc.code, int):
                print(exc.code, file=sys.stderr)
        except BaseException as exc:
            tb = exc.__traceback__
            while tb is not None and tb.tb_frame.f_code.co_filename != name:
                tb = tb.tb_next
            traceback.print_exception(type(exc), exc, tb)
    finally:
        sys.stdout, sys.stderr = real
    return finished

def _tc_raises(exc_type, fn, *args, **kwargs):
    """For a check such as: assert raises(ValueError, parse_id, "3.5"), "rejects 3.5"."""
    try:
        fn(*args, **kwargs)
    except exc_type:
        return True
    return False

def _tc_check(tests):
    """Try a task's checks against the namespace of the last run. Every top-level assert is one check and
    its message is the label the reader sees; any other top-level line is setup."""
    name = "checks.py"
    env = _tc_last
    env["raises"] = _tc_raises
    results = []
    real = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = io.StringIO()
    try:
        for node in ast.parse(tests, name).body:
            if not isinstance(node, ast.Assert):
                try:
                    exec(compile(ast.Module([node], []), name, "exec"), env)
                except BaseException as exc:
                    results.append({"ok": False, "label": ast.get_source_segment(tests, node), "detail": f"{type(exc).__name__}: {exc}"})
                continue
            test, detail = node.test, ""
            label = node.msg.value if isinstance(node.msg, ast.Constant) else ast.get_source_segment(tests, test)
            try:
                if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
                    got = eval(compile(ast.Expression(test.left), name, "eval"), env)
                    want = eval(compile(ast.Expression(test.comparators[0]), name, "eval"), env)
                    ok = bool(got == want)
                    if not ok:
                        detail = f"expected {want!r}, got {got!r}"
                else:
                    ok = bool(eval(compile(ast.Expression(test), name, "eval"), env))
            except BaseException as exc:
                ok, detail = False, f"{type(exc).__name__}: {exc}"
            results.append({"ok": ok, "label": label, "detail": detail})
    finally:
        sys.stdout, sys.stderr = real
    return json.dumps(results)
`;

let booting = null;   // Promise<{ py, run, check }>, created by the first job
let chain = Promise.resolve();

function boot() {
  return import(PYODIDE_BASE + "pyodide.mjs").then(async (mod) => {
    const py = await mod.loadPyodide({ indexURL: PYODIDE_BASE });
    py.setStdin({ stdin: () => null });   // no terminal here: input() meets end-of-file, as with an empty pipe
    py.runPython(RUNNER);
    return { py, run: py.globals.get("_tc_run"), check: py.globals.get("_tc_check") };
  });
}

async function handle({ id, code, prelude, tests }) {
  const { py, run, check } = await (booting || (booting = boot()));
  let lines = 0, chars = 0, cut = false;
  const emit = (type, text) => {
    if (cut) return;
    lines += text.split("\n").length - 1;
    chars += text.length;
    if (lines > MAX_LINES || chars > MAX_CHARS) { cut = true; postMessage({ id, type: "cut" }); return; }
    postMessage({ id, type, text });
  };
  postMessage({ id, type: "start" });
  const earlier = py.toPy(prelude || []);
  let finished;
  try { finished = run(emit, code, earlier); } finally { earlier.destroy(); }
  if (tests != null) postMessage({ id, type: "checks", ran: finished, results: finished ? JSON.parse(check(tests)) : [] });
  postMessage({ id, type: "done" });
}

onmessage = (ev) => {
  const job = ev.data;
  chain = chain.then(() => handle(job)).catch((err) => {
    console.error(err);
    postMessage({ id: job.id, type: "fatal", text: String((err && err.stack) || err) });
  });
};
