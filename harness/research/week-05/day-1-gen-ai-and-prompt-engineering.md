# w05d1 — Gen AI orientation & prompt engineering

gate: full
verified: 2026-11-03
week: 5 · Gen AI introduction
day: 1 · day-1-gen-ai-and-prompt-engineering

version-stamps:
  - python: 3.15 (verified 2026-11-03; `py` on the trainer machine reports 3.15.0)
  - pandas: 3.0.6 (verified 2026-11-03; the desk's pin in `ticket-desk/requirements.txt` at 55f65d7; wheel pandas-3.0.6-cp315-cp315-win_amd64.whl, uploaded 2026-09-17; used only for the Hallucinations docs check, read-only, nothing is typed; the current release is 3.1.0, so the page and pair pack cite the versioned 3.0 reference, whose header reads "pandas 3.0.6 documentation")
  - llm-config: claude-haiku-4-5 (deliberate legacy pin, verified 2026-11-03)   # The Models overview (https://platform.claude.com/docs/en/models/overview) lists Claude Haiku 4.5 under "Legacy models (still available)"; the current Haiku is `claude-haiku-5-5`. Kept as a pin because week 5 makes no API call (no account, no key) and the page prints no model id; update `llm` in the week config before week 6 calls an API.
  - sampling-parameters: unsupported on current Claude models (verified 2026-11-03)   # Source: Claude Platform release notes (https://platform.claude.com/docs/en/release-notes/overview), May 28, 2026: "Setting the sampling parameters `temperature`, `top_p`, or `top_k` to a non-default value returns a 400 error on Claude Opus 4.8, same as on Claude Opus 4.7."; August 20, 2026 (Python SDK v1.0): it "removes ... the `temperature`, `top_p`, and `top_k` parameters on Messages methods". The Claude glossary still defines temperature but does not state this change. Teach temperature as a concept (Google Vertex AI and the Claude glossary still define it); never tell the reader to set it on a named product. This stamp is for the harness only: the notes page names no model version (w05d1 anti-spoiler defers model families to w05d2).
  - openai-fine-tuning: winding down (verified 2026-11-03)   # "OpenAI is winding down the fine-tuning platform." Fine-tuning stays a definition only (week note); do not cite OpenAI's fine-tuning as a service a reader can use.
  - nist-ai-600-1: Generative Artificial Intelligence Profile, July 2024 (verified 2026-11-03)
  - owasp-top-10-llm: 2025 edition (LLM02 Sensitive Information Disclosure, LLM09 Misinformation) (verified 2026-11-03)

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- Artificial intelligence is "A non-human program or model that can solve sophisticated tasks", and "Formally, machine learning is a sub-field of artificial intelligence." — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
- Machine learning is "the process of training a piece of software, called a model, to make useful predictions or generate content (like text, images, audio, or video) from data." — [What is Machine Learning?](https://developers.google.com/machine-learning/intro-to-ml/what-is-ml)
- Google sorts ML systems into supervised, unsupervised, reinforcement learning and generative AI; "Supervised learning models can make predictions after seeing lots of data with the correct answers" — [What is Machine Learning?](https://developers.google.com/machine-learning/intro-to-ml/what-is-ml)
- A label is "the "answer" or "result" portion of an example", which is the desk's `priority` column when titles are the input — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
- "Neural networks are a family of model architectures designed to find nonlinear patterns in data", and "A deep neural network contains more than one hidden layer" (deep learning is learning with such networks) — [Neural networks](https://developers.google.com/machine-learning/crash-course/neural-networks), [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
- Google's Rule #1 is "Don't be afraid to launch a product without machine learning", because "Machine learning is cool, but it requires data"; a hand-written rule is a legitimate first answer — [Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)
- "Generative AI is a class of models that creates content from user input." — [What is Machine Learning?](https://developers.google.com/machine-learning/intro-to-ml/what-is-ml)
- "Generative AI is a type of AI that produces content such as text, audio, code, videos and images", and "Based on the training data, these models generate content that is statistically likely in response to a prompt." — [Guide on the use of generative artificial intelligence](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/generative-ai/guide-use-generative-ai.html)
- A language model "estimates the probability of a token or sequence of tokens occurring within a longer sequence of tokens", and "A token could be a word, a subword (a subset of a word), or even a single character." — [Introduction to Large Language Models](https://developers.google.com/machine-learning/resources/intro-llms)
- How many characters a token covers "depends on the model and the language", and the Claude docs say a newer tokenizer "produces approximately 30 percent more tokens for the same text than earlier models", so any split shown on a board is illustrative (notes: present this only as "the Claude docs say ...", a product named as an example of a chat assistant, never as a model lineup or version list) — [Glossary (Claude docs)](https://platform.claude.com/docs/en/about-claude/glossary)
- Pretrained autoregressive models are "pretrained to predict the next word, given the previous context of text in the document" and "are not inherently good at answering questions or following instructions" until fine-tuning and RLHF refine them — [Glossary (Claude docs)](https://platform.claude.com/docs/en/about-claude/glossary)
- The context window is "all the text a language model can reference when generating a response, including the response itself", different from the training corpus, "a "working memory" for the model"; "As token count grows, accuracy and recall degrade, a phenomenon known as context rot" — [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- "Temperature controls the degree of randomness in token selection"; at temperature 0 "the highest probability tokens are always selected" and responses "are mostly deterministic, but a small amount of variation is still possible." — [Experiment with parameter values](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/adjust-parameter-values)
- "Even with temperature set to 0, the results will not be fully deterministic, and identical inputs might produce different outputs across API calls." — [Glossary (Claude docs)](https://platform.claude.com/docs/en/about-claude/glossary)
- OpenAI states "the content generated from a model is non-deterministic" and recommends "Pinning your production applications to specific model snapshots" — [Prompt engineering (OpenAI)](https://developers.openai.com/api/docs/guides/prompt-engineering)
- A prompt is "Any text entered as input to a large language model to condition the model to behave in a certain way", and prompt engineering is "The art of creating prompts that elicit the desired responses from a large language model." — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
- A zero-shot prompt is "A prompt that does not provide an example of how you want the large language model to respond"; a few-shot prompt "contains more than one (a "few") example demonstrating how the large language model should respond." — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
- The few-shot paper applied a large language model "without any gradient updates or fine-tuning", with "few-shot demonstrations specified purely via text interaction with the model" — [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)
- "Examples are one of the most reliable ways to steer Claude's output format, tone, and structure"; the guide advises "Include 3–5 examples for best results" and wrapping them in `<example>` tags so they are not read as instructions — [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- "Think of Claude as a brilliant but new employee who lacks context on your norms and workflows. The more precisely you explain what you want, the better the result." — [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Google names the components of a prompt as task, system instructions ("passed to the model before any user input in the prompt"), few-shot examples and contextual information — [Introduction to prompting](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/introduction-prompt-design)
- "The Messages API is stateless, which means that you always send the full conversational history to the API"; each turn's input "Contains all previous conversation history plus the current user message" — [Using the Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages), [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- Fine-tuning is "A second, task-specific training pass performed on a pre-trained model to refine its parameters for a specific use case." — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
- "The prompt engineering process may be all you need in order to get great results for your use case"; OpenAI also states "OpenAI is winding down the fine-tuning platform." — [Model optimization (OpenAI)](https://developers.openai.com/api/docs/guides/model-optimization)
- A hallucination is text "that is factually incorrect or inconsistent with the given context"; the guide's defences include allowing "I don't know", verifying with citations and restricting the model to provided documents, and "they don't eliminate them entirely" — [Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- NIST calls it confabulation, "The production of confidently stated but erroneous or false content", and explains "Confabulations are a natural result of the way generative models are designed" — [NIST AI 600-1, Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
- OWASP lists among misinformation risks "The model suggests insecure or non-existent code libraries", and defines overreliance as users who "place excessive trust in LLM-generated content, failing to verify its accuracy" — [LLM09:2025 Misinformation](https://genai.owasp.org/llmrisk/llm092025-misinformation/)
- The pandas 3.0.6 DataFrame reference lists no `count_by`; `Series.value_counts` is "Return a Series containing counts of unique values." (run under `py` 3.15 with pandas 3.0.6: `df.count_by('priority')` raises `AttributeError: 'DataFrame' object has no attribute 'count_by'`) — [DataFrame reference, pandas 3.0.6](https://pandas.pydata.org/pandas-docs/version/3.0/reference/frame.html), [pandas.Series.value_counts, pandas 3.0.6](https://pandas.pydata.org/pandas-docs/version/3.0/reference/api/pandas.Series.value_counts.html)
- Sensitive information "includes personal identifiable information (PII), financial details, health records", security credentials and confidential business data, and users "need to understand the risks of unintentionally providing sensitive data" — [LLM02:2025 Sensitive Information Disclosure](https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/)
- "Public servants must not input personal information into publicly available online generative AI tools", because "the supplier might store a copy of the information", and the user is responsible that generated content "is accurate, non-partisan, unbiased, and doesn't violate intellectual property laws" — [Guide on the use of generative artificial intelligence](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/generative-ai/guide-use-generative-ai.html)
- At 55f65d7 the desk's `desk.redact` is `EMAIL.sub("[email]", text)` with `EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")`, docstring "Return the text with email addresses hidden." — [ticket-desk/desk.py at 55f65d7](https://github.com/2494-Gen-AI-CN/demos/blob/55f65d7/ticket-desk/desk.py)
- The desk's `priorities` rows are `('high', 4), ('normal', 24), ('low', 72)`, and the six seed tickets carry `Login page returns 500` `high`, `Invoice PDF is blank` `normal`, `Typo on pricing page` `normal`, `Checkout button frozen` `high`, `Export is missing rows` `normal`, `Add dark mode` `low` — [ticket-desk/sql/seed.sql at 55f65d7](https://github.com/2494-Gen-AI-CN/demos/blob/55f65d7/ticket-desk/sql/seed.sql)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### ML and DL introduction
- Interview questions: What is the difference between machine learning and a program with hand-written rules?; What is a label, and what would the label be if a model learned the desk's priorities from ticket titles?; When would you ship a hand-written rule instead of a model?
- Adjacent concept: Supervised learning — the rule-learned-from-labelled-examples example is supervised learning, and an interviewer asks for its name right after.
- Trade-off or limit: Machine learning needs data, and Google's first rule is to launch without it when a heuristic does the job ("If machine learning is not absolutely required for your product, don't use it until you have data.") — [Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)
- Recognise on sight: `if "500" in title or "frozen" in title: priority = "high"` is a rule written by a person; "we trained on last year's tickets and their priorities" is a rule learned from labelled examples.
- Claims:
  - Machine learning is "A program or system that trains a model from input data." — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
  - A model is "any mathematical construct that processes input data and returns output." — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
  - "Supervised learning models can make predictions after seeing lots of data with the correct answers" — [What is Machine Learning?](https://developers.google.com/machine-learning/intro-to-ml/what-is-ml)
  - "A complex heuristic is unmaintainable", which is the case for learning a rule once hand-written rules pile up — [Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)
  - Deep learning uses neural networks, "a family of model architectures designed to find nonlinear patterns in data", with more than one hidden layer; details are week 6 — [Neural networks](https://developers.google.com/machine-learning/crash-course/neural-networks)

### GenAI overview
- Interview questions: What is generative AI, and what are its common applications? (qc3.genai-in-development.R01); How does a large language model produce text? (qc3.genai-in-development.R01); Why can the same prompt give two different answers, and why can a fluent answer be false?
- Adjacent concept: The context window — the interviewer's next question after "next-token prediction" is "what does the model actually see", and the answer is only what is in the window.
- Trade-off or limit: A larger context window holds more, but "more context isn't automatically better. As token count grows, accuracy and recall degrade" — [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- Recognise on sight: A tokenizer view that splits `Checkout button frozen` into pieces such as `Check` `out` ` button` ` frozen` (illustrative; every tokenizer splits differently).
- Claims:
  - "Generative AI is a class of models that creates content from user input." — [What is Machine Learning?](https://developers.google.com/machine-learning/intro-to-ml/what-is-ml)
  - Common applications: generative AI "produces content such as text, audio, code, videos and images" and supports tasks like "writing and editing documents and emails" — [Guide on the use of generative artificial intelligence](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/generative-ai/guide-use-generative-ai.html)
  - LLMs "are trained on vast amounts of text data and can generate human-like text, answer questions, summarize information, and more." — [Glossary (Claude docs)](https://platform.claude.com/docs/en/about-claude/glossary)
  - A language model "determines the probabilities of different tokens or sequences of tokens to complete that blank." — [Introduction to Large Language Models](https://developers.google.com/machine-learning/resources/intro-llms)
  - Each token is picked from a probability distribution, and "Temperature controls the degree of randomness in token selection" — [Experiment with parameter values](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/adjust-parameter-values)
  - A model's knowledge has a date: the Claude models overview lists a "Reliable knowledge cutoff" for every model, so a question about something newer is past what the model learned — [Models overview](https://platform.claude.com/docs/en/models/overview)

### AI introduction
- Interview questions: Define artificial intelligence in one sentence; Is every AI system machine learning?; Where does generative AI sit inside AI, machine learning and deep learning?
- Adjacent concept: The nested circles (AI contains ML, ML contains DL, generative AI is built mostly on DL) — interviewers ask candidates to draw or say it.
- Trade-off or limit: Generative AI is "An emerging transformative field with no formal definition", so a candidate should give a working definition and its source, not a fixed one — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
- Recognise on sight: Marketing copy that calls a fixed `if` rule "AI"; under the glossary's wording that is a program solving a task, but not machine learning.
- Claims:
  - AI is "A non-human program or model that can solve sophisticated tasks." — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
  - "Formally, machine learning is a sub-field of artificial intelligence." — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
  - EO 14110 (quoted by NIST) defines generative AI as "the class of AI models that emulate the structure and characteristics of input data in order to generate derived synthetic content." — [NIST AI 600-1, Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)

### Zero-shot prompting
- Interview questions: What is a zero-shot prompt?; Why did "Write a triage rule for our support tickets." produce priorities the desk does not have?; What would you add first to a zero-shot prompt that gives the wrong format?
- Adjacent concept: Context in the prompt — a zero-shot prompt fails mostly from missing context (the three priorities, their SLA hours), not from missing examples.
- Trade-off or limit: A zero-shot answer can be right in substance and wrong in format: the glossary's currency example accepts "Rupee," "INR," or "₹" and notes the format might still matter to you — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
- Recognise on sight: A one-line prompt with no examples, no constraints and no output format, such as `Write a triage rule for our support tickets.`
- Claims:
  - A zero-shot prompt "does not provide an example of how you want the large language model to respond" — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
  - "If you want Claude to do more than the task strictly requires, explicitly request it rather than relying on the model to infer this from vague prompts." — [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  - "Providing context or motivation behind your instructions ... can give Claude more information about your goals" — [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

### Few-shot prompting
- Interview questions: What is few-shot prompting, and how is it different from fine-tuning?; Why give one example per priority rather than three `high` examples?; Your examples are right but the model still mislabels a ticket. Why?
- Adjacent concept: Held-out examples — testing the prompt on titles that are not among its examples is how a team knows the examples generalise.
- Trade-off or limit: Examples teach format and pattern, not an unstated team decision: no example shows that a blank invoice PDF is `normal`, so a model can plausibly answer `high` — [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Recognise on sight: A prompt with labelled pairs before the question, such as `Login page returns 500 -> high` / `Typo on pricing page -> normal` / `Add dark mode -> low`.
- Claims:
  - A few-shot prompt "contains more than one (a "few") example demonstrating how the large language model should respond." — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
  - "Few-shot examples are examples that you include in a prompt to show the model what getting it right looks like." — [Introduction to prompting](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/introduction-prompt-design)
  - Few-shot demonstrations are "specified purely via text interaction with the model", with no gradient updates (the page says "a large language model" and never names the paper's model; model families are w05d2) — [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)
  - Examples should be wrapped in tags "so Claude can distinguish them from instructions", 3 to 5 of them — [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

### Constraints
- Interview questions: What is a constraint in a prompt?; Why add an `unsure` answer?; How does a fixed output format help a program that reads the reply?
- Adjacent concept: Parsing the reply — a constraint like "exactly one of `high`, `normal`, `low`, `unsure`" matters because code (or a person) checks the output against an allowed list.
- Trade-off or limit: A constraint narrows the reply but is not a guarantee: the round-3 reply can still write "This is probably high." where the bare word was asked, so the output is checked before anything uses it — [Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- Recognise on sight: `Answer with exactly one word from: high, normal, low, unsure. Then one reason line.`
- Claims:
  - Giving the model permission to say it does not know "can drastically reduce false information" — [Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
  - "Being specific about the output you want can help enhance results." — [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  - The desk's allowed priorities and SLA hours come from its `priorities` table (`high` 4, `normal` 24, `low` 72), which is what a constraint should name — [ticket-desk/sql/seed.sql at 55f65d7](https://github.com/2494-Gen-AI-CN/demos/blob/55f65d7/ticket-desk/sql/seed.sql)

### Fine-tuning and conditioning
- Interview questions: What is fine-tuning?; What is the difference between fine-tuning a model and putting examples in a prompt?; When would a team fine-tune rather than prompt?
- Adjacent concept: Pretraining — fine-tuning is defined against it ("a second ... training pass" on a pretrained model), so the interviewer often asks what came first.
- Trade-off or limit: Fine-tuning "can be a time-consuming process" and prompting "may be all you need", and OpenAI is "winding down the fine-tuning platform", so this week uses prompting only — [Model optimization (OpenAI)](https://developers.openai.com/api/docs/guides/model-optimization)
- Recognise on sight: A training file of hundreds of input-output pairs and a training job (fine-tuning) against a prompt that carries three examples in its text (conditioning).
- Claims:
  - Fine-tuning is "A second, task-specific training pass performed on a pre-trained model to refine its parameters for a specific use case." — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
  - Fine-tuning "causes the model to start representing and mimicking the patterns and characteristics of the fine-tuning dataset" — [Glossary (Claude docs)](https://platform.claude.com/docs/en/about-claude/glossary)
  - A prompt is text entered "to condition the model to behave in a certain way": conditioning changes the input, not the parameters — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
  - Fine-tuning lets a team "provide more example inputs and outputs than could fit within the context window of a single request" — [Model optimization (OpenAI)](https://developers.openai.com/api/docs/guides/model-optimization)

### Iteration and dialog state
- Interview questions: Why does a chat assistant seem to remember earlier turns?; What does a new chat know about your previous chat?; Why does a long chat drift from your first instructions?
- Adjacent concept: Iterative refinement — a follow-up turn that fixes one line of the previous reply works because the previous reply is in the context window.
- Trade-off or limit: Every turn adds to the window and long contexts degrade ("context rot"), so a fresh chat with a complete prompt can beat a long patched one — [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- Recognise on sight: A follow-up turn such as `Line 1 must be the bare word only. Rewrite just that line.`
- Claims:
  - "The Messages API is stateless, which means that you always send the full conversational history to the API." — [Using the Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages)
  - Each turn's input "Contains all previous conversation history plus the current user message", and each output "becomes part of the input for the next turn" — [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
  - Chat interfaces "can also manage the context window on a rolling "first in, first out" basis", so the oldest turns can fall out — [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
  - "Iterative refinement: Use Claude's outputs as inputs for follow-up prompts, asking it to verify or expand on previous statements." — [Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)

### Instructions and guidelines
- Interview questions: What goes in an instruction block at the top of a prompt?; What is a system prompt?; How do you test whether your instructions are clear?
- Adjacent concept: Role, audience, rules, output format — the four parts of round 4's instruction block, and the usual shape of a team's reusable prompt.
- Trade-off or limit: Instructions are text the model weighs, not code it executes; the reply is still checked against the rules — [Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- Recognise on sight: A block that opens `You are triaging support tickets for a small help desk.` followed by rules and `Output format:`.
- Claims:
  - "System instructions are instructions that get passed to the model before any user input in the prompt." — [Introduction to prompting](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/introduction-prompt-design)
  - "Setting a role in the system prompt focuses Claude's behavior and tone for your use case." — [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  - "developer messages are instructions provided by the application developer, prioritized ahead of user messages." — [Prompt engineering (OpenAI)](https://developers.openai.com/api/docs/guides/prompt-engineering)
  - "Key test: Show your prompt to a colleague with minimal context on the task and ask them to follow it. If they'd be confused, Claude will be too." — [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

### Hallucinations
- Interview questions: What is a hallucination?; Why does a model invent a method like `DataFrame.count_by`?; How do you check a model's claim about a library before you use it?
- Adjacent concept: Overreliance — the risk is not only that the model is wrong but that the developer does not check.
- Trade-off or limit: Prompting techniques reduce hallucinations but "don't eliminate them entirely. Always validate critical information" — [Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- Recognise on sight: `df.count_by("priority")` in a reply; the docs list `Series.value_counts`, so the fix is `df["priority"].value_counts()`.
- Claims:
  - Confabulation is "The production of confidently stated but erroneous or false content (known colloquially as "hallucinations" or "fabrications")" — [NIST AI 600-1, Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
  - Models "generate outputs that approximate the statistical distribution of their training data", which "can also produce outputs that are factually inaccurate or internally inconsistent." — [NIST AI 600-1, Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
  - "The model suggests insecure or non-existent code libraries" is a named misinformation risk for developers — [LLM09:2025 Misinformation](https://genai.owasp.org/llmrisk/llm092025-misinformation/)
  - The pandas 3.0.6 DataFrame reference lists `DataFrame.count` ("Count non-NA cells for each column or row.") and `DataFrame.value_counts`, and no `count_by` — [DataFrame reference, pandas 3.0.6](https://pandas.pydata.org/pandas-docs/version/3.0/reference/frame.html)
  - `Series.value_counts(normalize=False, sort=True, ascending=False, bins=None, dropna=True)`: "Return a Series containing counts of unique values." — [pandas.Series.value_counts, pandas 3.0.6](https://pandas.pydata.org/pandas-docs/version/3.0/reference/api/pandas.Series.value_counts.html)

### Responsible usage
- Interview questions: Who is responsible for code an assistant wrote?; What do you check before you commit a generated line?; Name two rules you keep when you use a public chat assistant at work.
- Adjacent concept: Code review — a generated line goes through the same review and tests as a hand-written one, which interviewers tie back to team practice.
- Trade-off or limit: Generative AI "can produce content that is discriminatory or not representative", so the person using it reviews for bias as well as accuracy — [Guide on the use of generative artificial intelligence](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/generative-ai/guide-use-generative-ai.html)
- Recognise on sight: A pull request description that says "generated by an assistant, reviewed and tested by me" with the tests that ran.
- Claims:
  - The user is responsible that generated content "is accurate, non-partisan, unbiased, and doesn't violate intellectual property laws." — [Guide on the use of generative artificial intelligence](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/generative-ai/guide-use-generative-ai.html)
  - Overreliance "occurs when users place excessive trust in LLM-generated content, failing to verify its accuracy." — [LLM09:2025 Misinformation](https://genai.owasp.org/llmrisk/llm092025-misinformation/)
  - NIST lists "automation bias, over-reliance" under its Human-AI Configuration risk — [NIST AI 600-1, Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)

### Security
- Interview questions: What must never go into a public chat assistant?; How would you make a stack trace safe to paste?; Why is the employer's code different from your own project's README?
- Adjacent concept: Redaction — removing emails, names, hosts, users and passwords from text before it leaves the developer's machine.
- Trade-off or limit: The desk's `desk.redact` hides email addresses only; run under `py` at 55f65d7 it leaves `host=127.0.0.1 user=desk_app password=s3cret` unchanged and turns `mysql://desk_app:s3cret@db.internal:3306/ticket_desk` into `mysql://desk_app:[email]:3306/ticket_desk` (the pattern happens to match `s3cret@db.internal`, the user stays), so a connection string is cleaned by hand — [ticket-desk/desk.py at 55f65d7](https://github.com/2494-Gen-AI-CN/demos/blob/55f65d7/ticket-desk/desk.py)
- Recognise on sight: `export DESK_DB_PASSWORD=...` or `password=os.environ["DESK_DB_PASSWORD"]` next to a literal value in pasted text; any line with `@example.com`.
- Claims:
  - Sensitive information "includes personal identifiable information (PII), financial details, health records", plus security credentials and confidential business data — [LLM02:2025 Sensitive Information Disclosure](https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/)
  - OWASP recommends user education that gives "guidance on avoiding the input of sensitive information." — [LLM02:2025 Sensitive Information Disclosure](https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/)
  - The input must not include "personal, protected, classified or other sensitive information" — [Guide on the use of generative artificial intelligence](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/generative-ai/guide-use-generative-ai.html)
  - NIST's Data Privacy risk covers "leakage and unauthorized use, disclosure, or de-anonymization of ... personally identifiable information or sensitive data." — [NIST AI 600-1, Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
  - The desk reads its password from the environment (`password=os.environ["DESK_DB_PASSWORD"]` in `db.py`), so the export line that sets it is a credential — [ticket-desk/db.py at 55f65d7](https://github.com/2494-Gen-AI-CN/demos/blob/55f65d7/ticket-desk/db.py)

### Prompt engineering introduction
- Interview questions: What is prompt engineering?; What do you need before you start improving a prompt?; Walk me through how you improved a prompt that gave the wrong answer.
- Adjacent concept: Success criteria — a prompt is improved against a written test (what a correct triage line looks like), the way code is improved against tests.
- Trade-off or limit: "Not every success criterion or failing eval is best solved by prompt engineering"; sometimes a different model or a plain rule is the fix — [Prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
- Recognise on sight: Rounds of the same prompt kept side by side, each with the reply and what changed.
- Claims:
  - Prompt engineering is "The art of creating prompts that elicit the desired responses from a large language model." — [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
  - "Prompt engineering is the process of writing effective instructions for a model" — [Prompt engineering (OpenAI)](https://developers.openai.com/api/docs/guides/prompt-engineering)
  - Before prompt engineering a team needs "A clear definition of the success criteria", "Some ways to empirically test against those criteria" and "A first draft prompt" — [Prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- What is Machine Learning? (Google for Developers) — https://developers.google.com/machine-learning/intro-to-ml/what-is-ml
- Machine Learning Glossary (Google for Developers) — https://developers.google.com/machine-learning/glossary
- Rules of Machine Learning (Google for Developers) — https://developers.google.com/machine-learning/guides/rules-of-ml
- Neural networks, Machine Learning Crash Course (Google for Developers) — https://developers.google.com/machine-learning/crash-course/neural-networks
- Introduction to Large Language Models (Google for Developers) — https://developers.google.com/machine-learning/resources/intro-llms
- Introduction to prompting (Google Cloud Vertex AI) — https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/introduction-prompt-design
- Experiment with parameter values (Google Cloud Vertex AI) — https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/adjust-parameter-values
- Glossary (Claude docs) — https://platform.claude.com/docs/en/about-claude/glossary
- Context windows (Claude docs) — https://platform.claude.com/docs/en/build-with-claude/context-windows
- Using the Messages API (Claude docs) — https://platform.claude.com/docs/en/build-with-claude/working-with-messages
- Models overview (Claude docs) — https://platform.claude.com/docs/en/models/overview
- Prompt engineering overview (Claude docs) — https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview
- Prompting best practices (Claude docs) — https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Reduce hallucinations (Claude docs) — https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations
- Prompt engineering (OpenAI API docs) — https://developers.openai.com/api/docs/guides/prompt-engineering
- Model optimization (OpenAI API docs) — https://developers.openai.com/api/docs/guides/model-optimization
- Language Models are Few-Shot Learners (Brown et al., 2020) — https://arxiv.org/abs/2005.14165
- NIST AI 600-1, Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile (July 2024) — https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- OWASP Top 10 for LLM Applications, LLM02:2025 Sensitive Information Disclosure — https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/
- OWASP Top 10 for LLM Applications, LLM09:2025 Misinformation — https://genai.owasp.org/llmrisk/llm092025-misinformation/
- Guide on the use of generative artificial intelligence (Government of Canada, modified 2026-09-24) — https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/generative-ai/guide-use-generative-ai.html
- DataFrame API reference, pandas 3.0.6 documentation — https://pandas.pydata.org/pandas-docs/version/3.0/reference/frame.html
- pandas.Series.value_counts, pandas 3.0.6 documentation — https://pandas.pydata.org/pandas-docs/version/3.0/reference/api/pandas.Series.value_counts.html
- pandas 3.0.6 release metadata (PyPI JSON API) — https://pypi.org/pypi/pandas/3.0.6/json
- ticket-desk/desk.py at 55f65d7 (demo repo) — https://github.com/2494-Gen-AI-CN/demos/blob/55f65d7/ticket-desk/desk.py
- ticket-desk/sql/seed.sql at 55f65d7 (demo repo) — https://github.com/2494-Gen-AI-CN/demos/blob/55f65d7/ticket-desk/sql/seed.sql
- ticket-desk/sql/schema.sql at 55f65d7 (demo repo) — https://github.com/2494-Gen-AI-CN/demos/blob/55f65d7/ticket-desk/sql/schema.sql

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- machine learning | Building a program by training a model on example data instead of writing every rule by hand. | aka: ML
- deep learning | Machine learning with neural networks that have more than one hidden layer, the approach behind most generative AI. | aka: DL, deep neural network
- generative AI | AI models that create new content, such as text, code or images, from what a user types in. | aka: GenAI, gen AI, GAI
- zero-shot prompting | Asking a model to do a task with no example of the answer you want in the prompt. | aka: zero-shot, zero-shot prompt
- few-shot prompting | Putting a few worked examples of input and correct answer in the prompt so the model copies their pattern and format. | aka: few-shot, multishot prompting, few-shot examples
- temperature | A sampling setting that controls how much randomness goes into picking each next token, from near-repeatable to varied. | aka: sampling temperature
- system prompt | Instructions placed before the user's input that set the model's role, rules and output format for the whole conversation. | aka: system instructions, system message, instruction block
- PII | Personally identifiable information: anything that identifies a person, such as a name with an email address, which never goes into a public chat. | aka: personally identifiable information, personal information

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Trusting a fluent reply: learners accept `df.count_by("priority")` because it reads like pandas; the 3.0.6 reference lists no `count_by`, `py` raises `AttributeError: 'DataFrame' object has no attribute 'count_by'`, and the fix is `df["priority"].value_counts()`.
- Believing the model knows the desk or remembers yesterday's chat: it sees only the context window, re-sent each turn; a new chat starts empty, so the three priorities and their SLA hours have to be in the prompt.
- Expecting examples to carry a decision they never show: the few-shot prompt has no billing example, so `Invoice PDF is blank` can come back `high`; the fix is a constraint (`unsure` when the title gives no evidence) and a person who decides, not more guessing.
- Treating `desk.redact` as a scrubber: it hides email addresses only, leaves the name `Dana Whitfield`, leaves a `host=... user=... password=...` line untouched and half-masks a `mysql://user:pass@host` URL (the user stays), which looks cleaned but is not.
- Calling few-shot examples "fine-tuning": examples in the prompt condition the model for that request only; fine-tuning is a separate training pass that changes the model's parameters.
- Expecting the same prompt to give the same answer every time, or quoting "the model says X" as a fact about a named product: sampling varies replies even at temperature 0, and replies change between model versions.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- demoFormat none: nothing runs and nothing is typed on the desk; every reply the room reads is printed in the runbook and the pair pack and labelled `Illustrative reply (written for this page)`, and each round's prompt is a fenced block labelled `Prompt`.
- Keep rounds 1 to 4 of the triage prompt side by side on the board (zero-shot, few-shot, constraints, instruction block) with each printed reply and what changed, using the seed's real titles and the `priorities` rows (`high` 4, `normal` 24, `low` 72); the room reads each reply against the expected output before the next round.
- The Hallucinations check is the pandas 3.0.6 reference as printed (URL plus the quoted lines: the `DataFrame.count` and `DataFrame.value_counts` entries with no `count_by`, and the `Series.value_counts` signature and description); the live docs page is optional.
- The paste sort needs the printed `desk.redact` source and its real outputs on the two connection-string forms (shown above under Security), so pairs see why a regex for email addresses is not a redaction policy before the poster is written.
