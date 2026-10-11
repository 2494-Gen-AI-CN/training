"""01 - Tooling check: the whole on-ramp in one file.

PURPOSE
  The only on-ramp demo of the day. Confirm which interpreter the shell runs,
  see that CPython compiles to bytecode before it interprets (the __pycache__
  folder that appears is the segue into .gitignore in demo 04), place Python
  in the full-stack picture, and get the three ways to run Python straight:
  the >>> REPL, a saved script, a Jupyter cell.

EXPECTED OUTPUT (version patch level and paths differ per machine)
  STEP 1  Python 3.12.x at C:\\...\\python.exe
  STEP 2  a short dis() listing of greet(), then
          __pycache__ now holds: 01_tooling_check.cpython-312.pyc
  STEP 3  a five-layer full-stack map with Python's two seats marked
  STEP 4  the REPL cheat-sheet (python, _, exit(), python -i, Jupyter)
"""
import dis
import os
import py_compile
import sys

# --- STEP 1: which Python is this shell actually running? ---
print("STEP 1  Python", sys.version.split()[0], "at", sys.executable)
if sys.version_info[:2] != (3, 12):
    print("        expected 3.12: try `py -3.12` or fix the PATH before Wednesday")


# --- STEP 2: interpreter vs compiler - CPython does both ---
def greet(name: str) -> str:
    return f"Hello, {name}"


print("\nSTEP 2  CPython compiled greet() to bytecode before running it:")
dis.dis(greet)
this_file = os.path.abspath(__file__)
py_compile.compile(this_file, doraise=True)  # same thing `import` does on first use
cache_dir = os.path.join(os.path.dirname(this_file), "__pycache__")
mine = [f for f in os.listdir(cache_dir) if f.startswith("01_tooling_check")]
print("        __pycache__ now holds:", ", ".join(mine))
print("        -> build output, not source: it belongs in .gitignore (demo 04)")

# --- STEP 3: why Python, and where it sits in the full stack ---
print("\nSTEP 3  Python is general-purpose (web, scientific, tooling, business,")
print("        education, GUIs). In this course it has two seats in the stack:")
STACK = [
    ("browser / front end", "HTML, CSS, JavaScript", ""),
    ("API / back end", "Python: Flask, FastAPI, Django", "<- here"),
    ("data / ML layer", "Python: pandas, scikit-learn, LLM SDKs", "<- and here"),
    ("database", "PostgreSQL, MongoDB", ""),
    ("infrastructure", "Docker, cloud, CI pipelines", ""),
]
for layer, tools, mark in STACK:
    print(f"        {layer:<22}{tools:<40}{mark}")

# --- STEP 4: three ways to run the same code, then try the REPL live ---
print("\nSTEP 4  Three ways to run `greet('Toronto')`:")
print("        1. REPL      type `python`, see `>>>`, type the call, `_` holds the")
print("                     last result, leave with `exit()` (not `git status`!)")
print("        2. script    `python 01_tooling_check.py`  <- what you are doing now")
print("                     `python -i 01_tooling_check.py` keeps greet() defined")
print("        3. Jupyter   `jupyter notebook`, one cell per snippet: a REPL that")
print("                     remembers every cell, in execution order, not top-down")
print("        Now: open `python`, try `2 + 3`, then `_ * 10`, then `exit()`.")
