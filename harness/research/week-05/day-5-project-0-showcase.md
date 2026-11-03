# w05d5 — Project 0 showcase

gate: full
verified: 2026-11-03
week: 5 · Gen AI introduction
day: 5 · project-0-showcase

version-stamps:
  - python: 3.15 (verified 2026-11-03)
  - no library imported: demoFormat none, no walkthrough and no code typed today, nothing installs; each pair's P0 job runs on the pins in its own `requirements.txt`. The desk's pins at 55f65d7 (`ticket-desk/requirements.txt`, read from the demo repo 2026-11-03) are pandas==3.0.6, google-cloud-bigquery==3.47.0, matplotlib==3.11.2, db-dtypes==1.9.0, pyarrow==26.0.0, pytest==9.1.1; quote these pins, not any other figure (verified 2026-11-03)
  - BigQuery console (BigQuery Studio, sandbox): current service (verified 2026-11-03); classic saved queries are DEPRECATED in favour of BigQuery Studio saved queries (Dataform-backed), timeline under review
  - LLM in the week config: `claude-haiku-4-5` (verified 2026-11-03) — FLAG: the models overview lists Claude Haiku 4.5 under "Legacy models (still available)"; the current Haiku is `claude-haiku-5-5`; the deprecations table shows `claude-haiku-4-5-20251001` Active with retirement "Not sooner than October 15, 2026", a date already passed, so it can be deprecated with 60 days' notice. Week 5 makes no API call, so nothing today depends on it; re-check before week 6 writes any SDK call.

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- A chart's headline title should communicate the chart's headline message (a statement such as "Increase in number of people living alone"), and a separate statistical subtitle says what the data is, its geography and its time period — [Data visualisation: charts (Government Analysis Function)](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/)
- A quick test of a chart: if its message cannot be described over the phone in a few sentences, simplify it or split it into several charts; one chart should not carry too many messages — [Data visualisation: charts (Government Analysis Function)](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/)
- Keep charts as simple as possible: remove shaded backgrounds, borders, shadows and 3D shapes; about four lines on a line chart and five or fewer categories on a pie chart — [Data visualisation: charts (Government Analysis Function)](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/)
- The assertion-evidence approach builds each slide on a succinct sentence message rather than a phrase topic, supported by visual evidence rather than a bulleted list — [The Assertion-Evidence Approach (Penn State)](https://www.assertion-evidence.com/)
- Being upfront about quality, uncertainty and limitations protects the integrity of findings, and overstated certainty risks "inappropriate decisions"; the analyst's role is to explain how limitations feed through into the decisions users take — [Communicating quality, uncertainty and change (Government Analysis Function)](https://analysisfunction.civilservice.gov.uk/policy-store/communicating-quality-uncertainty-and-change/)
- Define an audience by role first, then by how close it is to the knowledge; experts suffer a "curse of knowledge" and skip steps, and as the audience widens "assume that you must explain more" — [Audience (Google Technical Writing One)](https://developers.google.com/tech-writing/one/audience)
- In the BigQuery query editor a valid query shows a check mark and the amount of data the query will process before it runs; results appear in the Results tab of the Query results pane — [Run a query (BigQuery)](https://docs.cloud.google.com/bigquery/docs/running-queries)
- Console queries run as interactive jobs by default, which "are intended to start executing as quickly as possible"; batch queries are lower priority and may queue — [Run a query (BigQuery)](https://docs.cloud.google.com/bigquery/docs/running-queries)
- Running the exact same query text again returns results from a cached table (typically about 24 hours, best-effort); any change to the text, even whitespace or a comment, prevents the cache hit; Job information then shows "0 B (results cached)" — [Using cached query results (BigQuery)](https://docs.cloud.google.com/bigquery/docs/cached-results)
- Saved queries are BigQuery Studio code assets powered by Dataform, available only in the console; classic saved queries are deprecated and will be fully replaced — [Introduction to saved queries (BigQuery)](https://docs.cloud.google.com/bigquery/docs/saved-queries-introduction)
- A query is saved with Save > Save query (Control+S) and opened again from the Files or Explorer pane; if a query cannot be saved, the Dataform API might not be enabled for the project — [Create saved queries (BigQuery)](https://docs.cloud.google.com/bigquery/docs/work-with-saved-queries)
- Personal history in the Explorer pane lists recent jobs, and "Open as new query" on a past job puts its SQL back in the editor to run again — [Manage jobs (BigQuery)](https://docs.cloud.google.com/bigquery/docs/managing-jobs)
- The sandbox gives a lifetime 10 GiB of storage that "is not refunded upon data deletion", 1 TiB of processed query data a month, a 60-day automatic expiration on tables, views and partitions, and no DML, streaming or Data Transfer Service — [BigQuery sandbox](https://docs.cloud.google.com/bigquery/docs/sandbox)
- Google Slides presenter view shows speaker notes; presenting on a second screen needs Chrome and an extra monitor, and "You can't use the 'Presenter view' and 'Full screen' at the same time with one monitor" — [Present slides (Google Docs Editors Help)](https://support.google.com/docs/answer/1696787)
- PowerPoint Presenter View shows the current slide, the next slide and the speaker notes, with a slide timer that can be paused or reset — [Use Presenter View in PowerPoint (Microsoft Support)](https://support.microsoft.com/en-us/office/use-presenter-view-in-powerpoint-fe7638e4-76fb-4349-8d81-5eb6679f49d7)
- STAR splits an interview answer into Situation (about 20%), Task (about 10%), Action (about 60%) and Result (about 10%); the Action is the steps "you personally took" and the Result includes quantifiable outcomes — [STAR Method of Interviewing (UW Career & Internship Center)](https://careers.uw.edu/resources/star-method-of-interviewing/)
- Show ownership with "I" statements rather than "we", prepare 3 to 5 stories in bullet notes, and do not memorise scripts, which sound unnatural and do not adapt to the question asked — [The STAR method for behavioral interviews (MIT CAPD)](https://capd.mit.edu/resources/the-star-method-for-behavioral-interviews/)
- Amazon calls STAR "the cornerstone" of its behavioural interviews, asks for "precise metrics and data that quantify your impact", applies a "so what?" test, and contrasts "we improved customer satisfaction" with a first-person sentence naming the action and the number — [Amazon interview guide (About Amazon)](https://www.aboutamazon.com/news/workplace/amazon-interview-guide)
- Behavioural questions ask candidates to describe prior achievements; hypothetical questions present a job-related situation; planned follow-up questions "help elicit a high level of detail"; answers are scored against a shared rubric of poor, borderline, solid and outstanding — [A guide to structured interviewing (Google re:Work)](https://rework.withgoogle.com/intl/en/guides/a-guide-to-structured-interviewing-for-better-hiring-practices)
- The Sprint Review inspects the outcome of the Sprint with key stakeholders and "is a working session and the Scrum Team should avoid limiting it to a presentation"; it is timeboxed to four hours for a one-month Sprint — [The Scrum Guide](https://scrumguides.org/scrum-guide.html)
- A README tells people what the project does, why it is useful and how to get started; GitHub shows it from `.github`, the root or `docs` — [About READMEs (GitHub Docs)](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- Association does not imply causality: a correlation can never prove cause and effect, so a correlation slide states the relationship and a line on why it may not be a cause — [NIST/SEMATECH e-Handbook: Scatter plot](https://www.itl.nist.gov/div898/handbook/eda/section3/eda33q.htm)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

No exit criterion is mapped to w05d5 (the prompt's list is empty), so no question below carries an id. Notes steps: 1 business case and the finding as the title; 2 the recommendation and the risk; 3 what technical and non-technical managers ask; 4 running queries live; 5 telling a project in an interview; 6 the Project 0 showcase; then Check yourself (may recap the week's Gen AI ideas, no new content).

### Presenting data work to a client
- Interview questions: You have ten minutes with a non-technical manager to present an analysis: what goes on the first slide and why?; What is the difference between a topic title ("Monthly rides by station") and a finding title ("Three downtown stations carry 40% of weekday rides"), and which belongs on a client slide?; Follow-up (a level beyond): your strongest chart supports a recommendation the data only partly backs. How do you present the uncertainty without burying the recommendation?
- Adjacent concept: Knowing the audience (role and proximity to the knowledge) — the next question after "how would you present this" is "to whom"; a mixed audience of technical and non-technical managers needs the business case and the finding first and the method on request — [Audience (Google Technical Writing One)](https://developers.google.com/tech-writing/one/audience)
- Trade-off or limit: a finding title commits to one message per slide; a chart that cannot be summarised in a few sentences carries too many messages and should be split — [Data visualisation: charts (Government Analysis Function)](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/)
- Recognise on sight: a deck whose slide titles are column names ("avg_duration by member_type") or topics ("Results"), against one whose titles are sentences with a number ("Members ride half as long as casual riders", illustrative); a first slide that names the client and the question before any table. Course-spec context (not a sourced claim): the P0 spec (`projects/official/P0-dataset-to-warehouse.md`) names the audience as "technical and non-technical managers who care about what the data says, not how it was stored", and the deck opens with the client and what they asked and closes with the recommendation.
- Claims:
  - A chart's headline title states the message; the subtitle states what the data is, where and when — [Data visualisation: charts (Government Analysis Function)](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/)
  - Slides built on sentence messages with visual evidence replace phrase topics and bullet lists — [The Assertion-Evidence Approach (Penn State)](https://www.assertion-evidence.com/)
  - Limitations are stated so the decision-maker can judge what the numbers support; overstated certainty leads to inappropriate decisions — [Communicating quality, uncertainty and change (Government Analysis Function)](https://analysisfunction.civilservice.gov.uk/policy-store/communicating-quality-uncertainty-and-change/)
  - A correlation slide never claims a cause; it states the relationship and why it may not be causal — [NIST/SEMATECH e-Handbook: Scatter plot](https://www.itl.nist.gov/div898/handbook/eda/section3/eda33q.htm)
  - Experts skip steps that feel obvious (the curse of knowledge); a wider audience needs more explained — [Audience (Google Technical Writing One)](https://developers.google.com/tech-writing/one/audience)
  - Presenting results to stakeholders is a Scrum event: in the Sprint Review "The Scrum Team presents the results of their work to key stakeholders", and then "attendees collaborate on what to do next", so a data talk ends on a recommendation the audience can act on — [The Scrum Guide](https://scrumguides.org/scrum-guide.html)

### Running a live demo
- Notes-author warning: the subtopic's own name contains the `metrics.notes.deliveryPhrases` entry "live demo"; the page's h2 and prose use "running queries live" or "a live query" instead.
- Interview questions: Why run a query live rather than show a screenshot, and what do you say before you press Run?; The warehouse stalls mid-presentation: what do you do in the next thirty seconds?; Follow-up (a level beyond): the same query ran in two seconds at rehearsal and now reports "0 B (results cached)". What does that tell the audience, and when would you turn the cache off before presenting?
- Adjacent concept: The Sprint Review as a working session — a showcase of working data to stakeholders is the same move a Scrum team makes at the end of each Sprint, where the guide warns against limiting it to a presentation — [The Scrum Guide](https://scrumguides.org/scrum-guide.html)
- Trade-off or limit: the cache makes a rehearsed query come back instantly and free, but only for identical text within about 24 hours on a best-effort basis; editing the query (even a comment) runs it fresh and costs bytes from the sandbox's 1 TiB a month — [Using cached query results (BigQuery)](https://docs.cloud.google.com/bigquery/docs/cached-results)
- Recognise on sight: the editor's check mark with "This query will process N MB when run"; Job information showing "0 B (results cached)"; a Files pane of saved queries named after the client's questions; Personal history with "Open as new query".
- Claims:
  - The editor validates the query and shows the bytes it will process before Run; results land in the Results tab — [Run a query (BigQuery)](https://docs.cloud.google.com/bigquery/docs/running-queries)
  - Console queries are interactive jobs that start as fast as possible; batch priority may queue — [Run a query (BigQuery)](https://docs.cloud.google.com/bigquery/docs/running-queries)
  - Saving a query needs the Dataform API on the project; if Save fails, the pair opens its `.sql` file from the repo and pastes it instead — [Create saved queries (BigQuery)](https://docs.cloud.google.com/bigquery/docs/work-with-saved-queries)
  - Personal history keeps recent jobs, and "Open as new query" restores a past query to rerun — [Manage jobs (BigQuery)](https://docs.cloud.google.com/bigquery/docs/managing-jobs)
  - With one monitor, Google Slides cannot run presenter view and full screen together, so a single-projector switch between deck and console is rehearsed — [Present slides (Google Docs Editors Help)](https://support.google.com/docs/answer/1696787)
  - Sandbox tables expire 60 days after creation and storage spent is not refunded on deletion, so the morning check queries the tables already loaded rather than reloading everything — [BigQuery sandbox](https://docs.cloud.google.com/bigquery/docs/sandbox)

### Telling a project in an interview
- Interview questions: Tell me about a project you built with a partner: what was your part?; Walk me through a data pipeline you built from raw file to answer; Follow-up (a level beyond): what would you change if the dataset were a hundred times bigger, and what did you get wrong the first time?
- Adjacent concept: Behavioural versus hypothetical questions — "tell me about a time" asks for a past story (STAR), "what would you do if" asks for reasoning about a new situation; interviewers plan follow-ups to dig into detail, so a story must survive a second and third question — [A guide to structured interviewing (Google re:Work)](https://rework.withgoogle.com/intl/en/guides/a-guide-to-structured-interviewing-for-better-hiring-practices)
- Trade-off or limit: a memorised script sounds unnatural and does not adapt to the question; prepare 3 to 5 stories as bullet notes instead — [The STAR method for behavioral interviews (MIT CAPD)](https://capd.mit.edu/resources/the-star-method-for-behavioral-interviews/)
- Recognise on sight: an answer that is 80% situation ("so the dataset was about bikes, and there were stations, and...") with no action or number, against one that spends most of its time on "I wrote the rejects table so the job carried on past bad rows" and ends on a result with a number.
- Claims:
  - STAR proportions: Situation about 20%, Task 10%, Action 60%, Result 10% — [STAR Method of Interviewing (UW Career & Internship Center)](https://careers.uw.edu/resources/star-method-of-interviewing/)
  - The Action is the steps you personally took, even on a team; use "I" statements — [The STAR method for behavioral interviews (MIT CAPD)](https://capd.mit.edu/resources/the-star-method-for-behavioral-interviews/)
  - Precise metrics quantify impact, and the "so what?" test asks for the impact, not the task list — [Amazon interview guide (About Amazon)](https://www.aboutamazon.com/news/workplace/amazon-interview-guide)
  - Answers are scored against a shared rubric of poor, borderline, solid and outstanding — [A guide to structured interviewing (Google re:Work)](https://rework.withgoogle.com/intl/en/guides/a-guide-to-structured-interviewing-for-better-hiring-practices)
  - A README that says what the project does, why it is useful and how to start is the link a candidate can hand an interviewer — [About READMEs (GitHub Docs)](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
  - On a pair project, `git log --author=<pattern>` limits the history to commits whose author line matches the pattern, so a candidate can list and name their own part before telling it with "I" — [git-log Documentation (git-scm.com)](https://git-scm.com/docs/git-log)

### Project 0 showcase
- Interview questions: What does a strong 15-minute data presentation hold, minute by minute?; How do two presenters hand over without losing the thread?; Follow-up (a level beyond): a manager asks a question your data cannot answer. What do you say in two sentences?
- Adjacent concept: The rubric as the definition of done — the P0 spec's "What we look for" (the story lands, the warehouse is real from a fresh clone, the analysis matters) is the showcase's acceptance criteria, the same way a Sprint Review inspects a defined outcome — [The Scrum Guide](https://scrumguides.org/scrum-guide.html)
- Trade-off or limit: running every query live proves the warehouse is real, but each fresh run spends bytes from the sandbox's 1 TiB of processed query data a month and waits on the job, while a rehearsed query returns from the cache at "0 B (results cached)" only when its text is identical and only best-effort for about 24 hours; so the strong slot runs one or two rehearsed queries live and shows the rest from the deck (with many pairs the course plan caps the live part at one query) — [BigQuery sandbox](https://docs.cloud.google.com/bigquery/docs/sandbox); [Using cached query results (BigQuery)](https://docs.cloud.google.com/bigquery/docs/cached-results)
- Recognise on sight: the P0 spec's Presentation block (15 minutes, technical and non-technical managers, queries live not screenshots, both partners speak) and Hand-in list (`projects/P0/` in one partner's repo with README, config with placeholders, code and tests, `.sql` files, diagram, charts, deck, sample load log and rejects). Course-spec context (not sourced claims): the P0 README opens with the business case in one or two paragraphs a non-technical manager can read and lets someone run all of it from a fresh clone; credentials stay out of the hand-in, in an environment variable or a file outside the repository, and the config file carries placeholders for anything private (`projects/official/P0-dataset-to-warehouse.md`). The slot length rule (105 minutes divided by the pairs present, floor 10) is the course plan's (`harness/plans/week-05.md`).
- Claims:
  - A README's job is what, why and how to start — [About READMEs (GitHub Docs)](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
  - Credentials live outside the repository: `gcloud auth application-default login` saves the credential file at `%APPDATA%\gcloud\application_default_credentials.json` on Windows (`$HOME/.config/gcloud/application_default_credentials.json` on Linux and macOS), and the `GOOGLE_APPLICATION_CREDENTIALS` environment variable can point at a credential JSON file instead — [How Application Default Credentials works (Google Cloud)](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
  - "Service account keys create a security risk and are not recommended": a leaked key works for an attacker with no other information, so no key file goes into `projects/P0/` — [How Application Default Credentials works (Google Cloud)](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
  - A `.gitignore` tells Git which files to ignore on commit, but a file already checked in must be untracked (`git rm --cached`) before a rule ignores it, so a config with real values that was committed once is still in the history — [Ignoring files (GitHub Docs)](https://docs.github.com/en/get-started/git-basics/ignoring-files)
  - Each chart is titled for the client with the message, not the column names — [Data visualisation: charts (Government Analysis Function)](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/)
  - Speaker notes and a slide timer in presenter view keep a pair inside its slot — [Use Presenter View in PowerPoint (Microsoft Support)](https://support.microsoft.com/en-us/office/use-presenter-view-in-powerpoint-fe7638e4-76fb-4349-8d81-5eb6679f49d7)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Data visualisation: charts (Government Analysis Function) — https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/
- Communicating quality, uncertainty and change (Government Analysis Function) — https://analysisfunction.civilservice.gov.uk/policy-store/communicating-quality-uncertainty-and-change/
- The Assertion-Evidence Approach (Penn State) — https://www.assertion-evidence.com/
- Audience (Google Technical Writing One) — https://developers.google.com/tech-writing/one/audience
- Run a query (BigQuery) — https://docs.cloud.google.com/bigquery/docs/running-queries
- Using cached query results (BigQuery) — https://docs.cloud.google.com/bigquery/docs/cached-results
- Introduction to saved queries (BigQuery) — https://docs.cloud.google.com/bigquery/docs/saved-queries-introduction
- Create saved queries (BigQuery) — https://docs.cloud.google.com/bigquery/docs/work-with-saved-queries
- Manage jobs (BigQuery) — https://docs.cloud.google.com/bigquery/docs/managing-jobs
- BigQuery sandbox — https://docs.cloud.google.com/bigquery/docs/sandbox
- Present slides (Google Docs Editors Help) — https://support.google.com/docs/answer/1696787
- Use Presenter View in PowerPoint (Microsoft Support) — https://support.microsoft.com/en-us/office/use-presenter-view-in-powerpoint-fe7638e4-76fb-4349-8d81-5eb6679f49d7
- STAR Method of Interviewing (UW Career & Internship Center) — https://careers.uw.edu/resources/star-method-of-interviewing/
- The STAR method for behavioral interviews (MIT CAPD) — https://capd.mit.edu/resources/the-star-method-for-behavioral-interviews/
- Amazon interview guide (About Amazon) — https://www.aboutamazon.com/news/workplace/amazon-interview-guide
- A guide to structured interviewing (Google re:Work) — https://rework.withgoogle.com/intl/en/guides/a-guide-to-structured-interviewing-for-better-hiring-practices
- The Scrum Guide — https://scrumguides.org/scrum-guide.html
- About READMEs (GitHub Docs) — https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- How Application Default Credentials works (Google Cloud) — https://docs.cloud.google.com/docs/authentication/application-default-credentials
- Ignoring files (GitHub Docs) — https://docs.github.com/en/get-started/git-basics/ignoring-files
- git-log Documentation (git-scm.com) — https://git-scm.com/docs/git-log
- NIST/SEMATECH e-Handbook: Scatter plot — https://www.itl.nist.gov/div898/handbook/eda/section3/eda33q.htm (verified 2026-11-02 in the w04d5 brief, D-0080)
- Models overview (Claude Platform docs; LLM id check only) — https://platform.claude.com/docs/en/docs/about-claude/models/overview
- Model deprecations (Claude Platform docs; LLM id check only) — https://platform.claude.com/docs/en/about-claude/model-deprecations

Note: cloud.google.com/bigquery/docs/* now 301-redirects to docs.cloud.google.com/bigquery/docs/*; cite the docs.cloud.google.com form.

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- business case | The one or two paragraphs that say who the client is, what they want to know and why it matters to them, written so a non-technical manager can read it. | aka: problem statement
- finding title | A slide or chart title written as a full sentence stating what the data shows, instead of a topic or a column name. | aka: headline title, action title, sentence headline
- stakeholder | A person who has an interest in a project's outcome and decides or is affected by what it recommends, such as a client's manager. | aka: stakeholders, key stakeholders
- STAR method | A way to answer an interview question with a past story in four parts: the situation, the task you owned, the actions you took, and the result. | aka: situation task action result, STAR answer
- behavioural question | An interview question that asks how you handled a real past situation, usually opening "Tell me about a time". | aka: behavioral question, behavioural interview, behavioral interview
- cached result | A query result BigQuery keeps for about a day and returns again, free, when exactly the same query text is run. | aka: query cache, cache hit, results cached
- saved query | A query stored by name in the BigQuery console so it can be opened and run again without retyping it. | aka: saved queries

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Slide titles left as topics or column names ("Results", "avg_trip_minutes by month"): the manager has to work out the finding, so the recommendation never lands; rewrite each as a sentence with a number.
- Opening with the pipeline (staging tables, the star schema, the SCD columns) instead of the client and the question; the spec's audience cares what the data says, not how it was stored, so the method goes after the answer or into the one technical question.
- A live query that fails on the presenting laptop: signed in as the wrong Google account, the sandbox project not selected, a saved query that would not save because the Dataform API is off, or tables missing after expiry; the setup check runs one query per pair on that laptop as the owning partner, and every `.sql` file is also open from the repo as the fallback.
- One partner speaks for twelve minutes and the other clicks; both partners speak, with a planned hand-over sentence, and in the interview each tells the story with "I" for their own part instead of "we did everything".
- Claiming a cause from the correlation slide, or giving a recommendation with no risk or limitation; managers ask "how sure are you", and the answer is the limitation stated up front.
- A STAR answer that is all situation and no result: three minutes on the dataset, no number at the end; the action carries about 60% and the result names a figure (rows loaded, rejects caught, a question answered).

## Demo plan hints (2–4; what must be shown live for this topic to land)

- demoFormat none: no walkthrough and nothing typed on the demo repo. In the Facilitation: Presenting data work to a client, the trainer rewrites two topic titles into finding titles on the board (one from the desk's `warehouse/questions.sql`, for example a topic "Tickets by priority" becoming a finding sentence, marked illustrative, not a real count), so the pairs see the move before rewriting their own decks.
- The trainer models one live query in the sandbox from a saved query or an open `.sql` file: say what it will show before pressing Run, point at the bytes estimate, read one number aloud, and, if it stalls, say what the query asks, move on and come back; a rerun shows Job information "0 B (results cached)", which is why the morning rehearsal makes the afternoon run fast (best-effort, identical text only).
- Single-projector check after lunch: each pair switches from the deck to the BigQuery console and back on the projector, since Google Slides presenter view and full screen cannot run together on one monitor.
- The one manager question per pair is answered in two sentences (the answer, then the evidence or the limitation); rehearse it in the AM slot with another pair playing technical and non-technical managers.
