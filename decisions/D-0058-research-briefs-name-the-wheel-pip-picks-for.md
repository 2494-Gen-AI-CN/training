# D-0058 — Research briefs name the wheel pip picks for the course Python for every third-party library the demos install (cpXYZ-cpXYZ-win_amd64 or py3-none-any / py2.py3-none-any, checked on PyPI); a library with neither fails the brief and names the newest Python every library of the week supports. The Python 3.15 pin (D-0041) stands for week 3: mysql-connector-python 26.7.0 installs from its pure-Python wheel

- Date: 2026-10-16
- Status: accepted
- Decision: Research briefs name the wheel pip picks for the course Python for every third-party library the demos install (cpXYZ-cpXYZ-win_amd64 or py3-none-any / py2.py3-none-any, checked on PyPI); a library with neither fails the brief and names the newest Python every library of the week supports. The Python 3.15 pin (D-0041) stands for week 3: mysql-connector-python 26.7.0 installs from its pure-Python wheel
- Why: O-16 asked for a wheel check at every week's research; making it a research-critic item (10) and a template comment means the check happens inside the day run instead of as an open item re-opened every week. Checked 2026-10-16 on PyPI: mysql-connector-python 26.7.0 (requires_python >=3.10) ships cp310-cp314 win_amd64 wheels and a py2.py3-none-any wheel but no cp315 wheel, so on 3.15 pip takes the pure-Python wheel and the pure protocol runs (no C extension), which is fine for class-size data; PyMySQL 1.2.3 (2026-09-17) is pure Python and is the fallback. Week 2 verified cp315 win_amd64 wheels for numpy 2.5.4, pandas 3.0.6 and matplotlib 3.11.2 (D-0054).
- Affects: harness/critics/research.md (item 10 wheel rule, item 12 example MySQL 9.x), harness/templates/research.md (stamp comment), STATUS.md O-16, decisions/D-0041 (revisit list now runs through research critic item 10)
- Supersedes: —
- Superseded-by: —

## Notes

Stamp placement: the wheel text goes after the version, inside the trailing parenthetical or the # comment (notes_check.brief_header reads the first token after the colon as the version); the week-2 briefs already have this shape. Later weeks the rule covers: BigQuery client wk 4, anthropic wk 5, scikit-learn wk 6, TensorFlow/Keras wk 7, Chroma/Pinecone wk 8, boto3 and LangChain/LangGraph wk 9-10, SageMaker wk 11. W1D2's remaining 3.12 strings (01_tooling_check.md, 03_remote_round_trip.md, key/README.md, runbook.md) are the record of a taught day and stay.
