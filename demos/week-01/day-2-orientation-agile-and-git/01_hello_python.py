"""01_hello_python.py - Python orientation: a script, the full stack, interpreter
vs compiler, and the REPL.

PURPOSE
  Show how Python runs a saved file, where Python sits in a full-stack app,
  prove that CPython compiles source to bytecode before interpreting it, and
  hand out the REPL / Jupyter survival tips.

RUN
  python 01_hello_python.py        # run the script top to bottom
  python -i 01_hello_python.py     # same, then drop into the REPL: try  stack[1]
  python                           # bare REPL: try  2 + 3  then  _ * 10  then  exit()

EXPECTED OUTPUT (bytecode line numbers / your exact 3.12.x may differ)
  Hello, Gen AI cohort! Today is 2026-10-13.
  Running cpython 3.12.10

  The full stack, top to bottom:
    front end       HTML / CSS / JavaScript in the browser               <- later
    back end        server code: requests, business rules, storage       <- Python
    database        where data persists between requests (e.g. MySQL)    <- SQL
    infrastructure  where it runs: laptop today, cloud (GCP) later       <- ops

  Bytecode CPython produced for add_tax():
    (a dis listing: LOAD_FAST price ... BINARY_OP * ... RETURN_VALUE)
  Cached bytecode written to: __pycache__\\01_hello_python.cpython-312.pyc

  REPL tips:
    ...five tip lines...
"""

import dis
import pathlib
import py_compile
import sys

# --- STEP 1: a script is a text file the interpreter reads top to bottom ---
cohort = "Gen AI"
day = "2026-10-13"
print(f"Hello, {cohort} cohort! Today is {day}.")
print("Running", sys.implementation.name, sys.version.split()[0])

# --- STEP 2: where Python sits in a full-stack application ---
stack = [
    ("front end", "HTML / CSS / JavaScript in the browser", "later"),
    ("back end", "server code: requests, business rules, storage", "Python"),
    ("database", "where data persists between requests (e.g. MySQL)", "SQL"),
    ("infrastructure", "where it runs: laptop today, cloud (GCP) later", "ops"),
]
print("\nThe full stack, top to bottom:")
for layer, what, who in stack:
    print(f"  {layer:<15} {what:<52} <- {who}")

# --- STEP 3: interpreter vs compiler - CPython compiles to bytecode, then interprets it ---
def add_tax(price, rate=0.13):
    return price * (1 + rate)

print("\nBytecode CPython produced for add_tax():")
dis.dis(add_tax)

# The same thing happens for whole files: the .pyc cache lands in __pycache__/
cached = py_compile.compile(__file__)
here = pathlib.Path(__file__).resolve().parent
print("Cached bytecode written to:", pathlib.Path(cached).relative_to(here))

# --- STEP 4: the REPL - open `python`, type 2 + 3, then _ * 10, then exit() ---
print("\nREPL tips:")
print("  >>>     is Python's prompt; PS C:\\> is PowerShell's. Shell commands fail at >>>")
print("  _       holds the last printed result:  2 + 3  then  _ * 10  gives 50")
print("  exit()  leaves the REPL (or Ctrl-Z then Enter on Windows, Ctrl-D elsewhere)")
print("  python -i 01_hello_python.py  runs this file, then lets you inspect `stack`")
print("  Jupyter: each cell is one REPL turn that remembers every cell run before it")
