/* glossary.js — centralized technical-terminology glossary for every notes page.
 *
 * ONE source of truth (GLOSSARY below). At load time this script:
 *   1. scans the page prose (.reading-col) for any glossary term that appears,
 *   2. underlines each occurrence and attaches a hover tooltip,
 *   3. builds a "Key terms" block in the left rail listing only the terms
 *      present on THIS page — click opens a popup with the definitions.
 *
 * Definitions are deliberately short: one plain-language sentence.
 * The harness Wire step APPENDS new entries from each day's research brief
 * between the GLOSSARY:BEGIN / GLOSSARY:END markers. Keep entries unique
 * (case-insensitive across term + aka); tests/test_glossary.py enforces it.
 *
 * Entry shape: { term: display form, def: one sentence, aka?: [alt surface forms] }
 * Simple trailing-"s" plurals are matched automatically; add irregulars to aka.
 */
(function () {
  "use strict";

  // ---- THE GLOSSARY (single source of truth) --------------------------------
  var GLOSSARY = [
    // GLOSSARY:BEGIN
    // — programming fundamentals —
    { term: "interpreter", def: "A program that runs your code line by line without producing a separate compiled file." },
    { term: "compiler", def: "A program that translates your whole source code into machine code before it runs." },
    { term: "REPL", def: "Read-Eval-Print Loop — an interactive prompt where you type one expression at a time and see the result.", aka: ["read-eval-print loop"] },
    { term: "variable", def: "A named slot that holds a value you can read and change.", aka: ["variables"] },
    { term: "function", def: "A named, reusable block of code that takes inputs and returns a result.", aka: ["functions"] },
    { term: "class", def: "A blueprint that defines the data and behaviour shared by objects of one kind.", aka: ["classes"] },
    { term: "object", def: "A single instance built from a class, with its own data.", aka: ["objects", "instance", "instances"] },
    { term: "inheritance", def: "A class reusing and extending the behaviour of a parent class.", aka: ["inherit", "inherits", "subclass", "subclasses"] },
    { term: "module", def: "A single Python file whose functions and classes you can import elsewhere.", aka: ["modules"] },
    { term: "package", def: "A folder of related modules that import as one unit.", aka: ["packages"] },
    { term: "virtual environment", def: "An isolated folder of installed packages so one project cannot break another.", aka: ["venv", "virtualenv"] },
    { term: "exception", def: "An error object raised when something goes wrong, which you can catch and handle.", aka: ["exceptions"] },
    { term: "iterator", def: "An object that hands you items one at a time until none are left.", aka: ["iterators", "iterable", "iterables"] },
    { term: "unit test", def: "A small automated check that one piece of code does what it should.", aka: ["unit tests", "unit testing"] },
    { term: "JSON", def: "A plain-text format for structured data that almost every language and API can read." },
    { term: "API", def: "Application Programming Interface — the set of calls one program exposes so other programs can use it.", aka: ["APIs"] },

    // — version control —
    { term: "version control", def: "Tracking every change to a codebase so you can review, undo and collaborate.", aka: ["source control"] },
    { term: "commit", def: "A saved snapshot of your changes with a message describing them.", aka: ["commits"] },
    { term: "branch", def: "A separate line of work in a repository that can later be merged back.", aka: ["branches"] },
    { term: "merge", def: "Combining the changes from one branch into another.", aka: ["merges", "merging"] },
    { term: "pull request", def: "A request to merge your branch, where teammates review the changes first.", aka: ["pull requests", "PR", "PRs"] },

    // — data & SQL —
    { term: "schema", def: "A defined shape for data — which tables, fields and types exist.", aka: ["schemas"] },
    { term: "primary key", def: "The column that uniquely identifies each row in a table.", aka: ["primary keys"] },
    { term: "foreign key", def: "A column that points to the primary key of another table to link rows.", aka: ["foreign keys"] },
    { term: "join", def: "Combining rows from two tables based on a matching column.", aka: ["joins"] },
    { term: "transaction", def: "A group of database operations that either all succeed or all roll back.", aka: ["transactions"] },
    { term: "ACID", def: "Atomicity, Consistency, Isolation, Durability — the guarantees a reliable database transaction gives." },
    { term: "normalization", def: "Organising tables so each fact is stored once, reducing duplication and update errors.", aka: ["normalize", "normalized"] },
    { term: "ETL", def: "Extract, Transform, Load — pulling data from sources, reshaping it, and loading it into a store.", aka: ["ELT"] },
    { term: "data warehouse", def: "A database optimised for analysis across large volumes of historical data.", aka: ["data warehouses", "warehouse"] },
    { term: "OLTP", def: "Online Transaction Processing — databases tuned for many small, fast reads and writes." },
    { term: "OLAP", def: "Online Analytical Processing — databases tuned for big aggregate queries over history." },

    // — machine learning —
    { term: "model", def: "A function learned from data that maps inputs to predictions.", aka: ["models"] },
    { term: "training", def: "Adjusting a model's internal numbers so its predictions match known examples.", aka: ["train", "trained"] },
    { term: "inference", def: "Running a trained model to get an answer, as opposed to training it." },
    { term: "feature", def: "One measurable input a model uses to make a prediction.", aka: ["features"] },
    { term: "label", def: "The known correct answer for a training example.", aka: ["labels"] },
    { term: "overfitting", def: "When a model memorises its training data and performs badly on new data.", aka: ["overfit", "overfits"] },
    { term: "tensor", def: "A multi-dimensional array of numbers — the basic data structure in deep learning.", aka: ["tensors"] },
    { term: "neural network", def: "A model built from layers of simple units whose connections are tuned during training.", aka: ["neural networks", "neural net"] },
    { term: "epoch", def: "One full pass through the training data.", aka: ["epochs"] },

    // — generative AI —
    { term: "LLM", def: "Large Language Model — an AI trained on huge amounts of text to predict and generate language.", aka: ["LLMs", "large language model", "large language models"] },
    { term: "token", def: "A chunk of text (roughly a word-piece) that a model reads and counts one at a time.", aka: ["tokens"] },
    { term: "context window", def: "The fixed amount of text a model can hold in view at once — its working memory.", aka: ["context windows"] },
    { term: "prompt", def: "The text instructions and context you give a model to steer its answer.", aka: ["prompts"] },
    { term: "hallucination", def: "When a model states something fluent and confident that is simply false.", aka: ["hallucinations", "hallucinate"] },
    { term: "embedding", def: "A list of numbers that captures a text's meaning so similar texts land near each other.", aka: ["embeddings", "embed"] },
    { term: "vector", def: "An ordered list of numbers; here, the numeric form of a text's meaning.", aka: ["vectors"] },
    { term: "vector store", def: "A database built to find the stored vectors nearest a query vector, fast.", aka: ["vector database", "vector databases", "vector stores"] },
    { term: "RAG", def: "Retrieval-Augmented Generation — fetch relevant documents, then answer using them.", aka: ["retrieval-augmented generation", "retrieval augmented generation"] },
    { term: "fine-tuning", def: "Continuing to train a model on your own data so new behaviour lives in its weights.", aka: ["fine-tune", "fine-tuned", "finetuning"] },
    { term: "agent", def: "A program that lets a model decide which tools to call, in what order, to reach a goal.", aka: ["agents", "agentic"] },

    // — w01d2: orientation, Agile & Git —
    { term: "repository", def: "A folder whose full change history Git tracks in a hidden .git directory.", aka: ["repo", "repositories"] },
    { term: "staging area", def: "The holding area where you put changes with git add before they become part of the next commit.", aka: ["staged", "git index"] },
    { term: "remote", def: "A copy of a repository hosted elsewhere (such as GitHub) that you push to and pull from.", aka: ["origin"] },
    { term: "SDLC", def: "Software Development Life Cycle — the stages software goes through from idea to retirement: plan, design, build, test, deploy, maintain.", aka: ["software development life cycle"] },
    { term: "Scrum", def: "An Agile framework that delivers work in short fixed-length Sprints with defined roles, events and artifacts.", aka: ["scrum framework"] },
    { term: "sprint", def: "A fixed time-box of one month or less in which a Scrum team turns backlog items into a usable increment." },
    { term: "story point", def: "A relative, unit-less estimate of how much effort a backlog item takes compared with other items, not a number of hours." },
    { term: "Jupyter notebook", def: "A browser document of code and text cells where each code cell runs in a live kernel and shows its output underneath.", aka: ["notebook", "Jupyter", ".ipynb"] },
    { term: "Agile", def: "A way of building software in short iterations that each deliver working software and welcome changing requirements, as set out in the 2001 Agile Manifesto.", aka: ["Agile Manifesto", "agile methodology"] },
    { term: "waterfall", def: "A sequential delivery model where each SDLC phase is finished and signed off before the next begins, so working software appears only at the end.", aka: ["waterfall model"] },
    { term: "backlog", def: "The ordered list of everything the product might need, owned by the Product Owner; the Sprint Backlog is the slice the team commits to for one Sprint.", aka: ["product backlog", "sprint backlog"] },
    { term: "Daily Scrum", def: "A 15-minute event where the Developers inspect progress toward the Sprint Goal and plan the next day's work.", aka: ["stand-up", "standup", "daily stand-up"] },
    { term: "DVCS", def: "Distributed Version Control System — every clone holds the full history, so commits, branches and logs work offline and only push, pull and fetch touch the network.", aka: ["distributed version control", "distributed version control system"] },
    { term: "merge conflict", def: "What Git reports when both branches changed the same lines; it writes the three conflict markers into the file so you can edit, stage and commit the version you want.", aka: ["conflict markers"] },
    { term: "fast-forward", def: "A merge where the target branch has no new commits of its own, so Git simply moves the branch pointer forward and creates no merge commit.", aka: ["fast-forward merge", "ff merge"] },
    { term: "upstream", def: "The remote branch a local branch tracks, set by git push -u, so that plain git push and git pull know where to go.", aka: ["upstream branch", "tracking branch"] }
    // GLOSSARY:END
  ];

  // ---- build lookup: every surface form → entry ------------------------------
  var BY_FORM = {};        // lowercased surface form → entry
  var FORMS = [];          // all surface forms, for regex (longest first)
  function addForm(form, entry) {
    var k = form.toLowerCase();
    if (!BY_FORM[k]) { BY_FORM[k] = entry; FORMS.push(form); }
  }
  GLOSSARY.forEach(function (e) {
    addForm(e.term, e);
    (e.aka || []).forEach(function (a) { addForm(a, e); });
  });
  // longest first so "context window" wins over "context"
  FORMS.sort(function (a, b) { return b.length - a.length; });

  function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
  // optional trailing "s" for simple plurals; \b word boundaries
  var RE = new RegExp("\\b(" + FORMS.map(esc).join("|") + ")(s?)\\b", "gi");

  // ---- tooltip (hover) -------------------------------------------------------
  var tip;
  function ensureTip() {
    if (tip) return tip;
    tip = document.createElement("div");
    tip.className = "gloss-tip";
    tip.setAttribute("role", "tooltip");
    document.body.appendChild(tip);
    return tip;
  }
  function showTip(el) {
    var t = ensureTip();
    t.innerHTML = '<b>' + el.dataset.glossTerm + '</b>' + el.dataset.glossDef;
    t.classList.add("show");
    var r = el.getBoundingClientRect();
    var tw = t.offsetWidth, th = t.offsetHeight;
    var left = r.left + r.width / 2 - tw / 2 + window.scrollX;
    left = Math.max(10 + window.scrollX, Math.min(left, window.scrollX + document.documentElement.clientWidth - tw - 10));
    var top = r.top + window.scrollY - th - 9;
    var below = false;
    if (top < window.scrollY + 6) { top = r.bottom + window.scrollY + 9; below = true; }
    t.style.left = left + "px";
    t.style.top = top + "px";
    t.classList.toggle("below", below);
  }
  function hideTip() { if (tip) tip.classList.remove("show"); }

  // ---- glossary modal (opened by the Key-terms block or any inline term) -----
  var modal;
  function buildModal(order, found) {
    modal = document.createElement("div");
    modal.className = "gloss-modal-overlay";
    var rows = order.map(function (t) {
      var e = found[t];
      return '<div class="gm-row" data-term="' + t.toLowerCase() + '">' +
        '<dt class="gm-term">' + t + '</dt><dd class="gm-def">' + e.def + '</dd></div>';
    }).join("");
    modal.innerHTML =
      '<div class="gloss-modal" role="dialog" aria-modal="true" aria-label="Glossary">' +
        '<button class="gloss-modal-x" aria-label="Close">✕</button>' +
        '<div class="gm-k">Glossary</div>' +
        '<h2 class="gm-h">Key terms on this page</h2>' +
        '<p class="gm-sub">' + order.length + ' term' + (order.length === 1 ? '' : 's') +
          ' · plain-language definitions, shared across every page.</p>' +
        '<dl class="gm-list">' + rows + '</dl>' +
      '</div>';
    document.body.appendChild(modal);
    modal.addEventListener("click", function (e) {
      if (e.target === modal || e.target.classList.contains("gloss-modal-x")) closeModal();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeModal(); });
  }
  function openModal(highlight) {
    if (!modal) return;
    modal.querySelectorAll(".gm-row.on").forEach(function (r) { r.classList.remove("on"); });
    modal.classList.add("show");
    if (highlight) {
      var row = modal.querySelector('.gm-row[data-term="' + highlight.toLowerCase() + '"]');
      if (row) {
        row.classList.add("on");
        row.scrollIntoView({ block: "center" });
      }
    } else {
      modal.querySelector(".gloss-modal").scrollTop = 0;
    }
  }
  function closeModal() { if (modal) modal.classList.remove("show"); }

  function wire(el) {
    el.addEventListener("mouseenter", function () { showTip(el); });
    el.addEventListener("mouseleave", hideTip);
    el.addEventListener("focus", function () { showTip(el); });
    el.addEventListener("blur", hideTip);
    el.addEventListener("click", function (e) {
      e.preventDefault();
      hideTip();
      openModal(el.dataset.glossTerm);
    });
  }

  // ---- scan the page, wrap occurrences of each term --------------------------
  var SKIP = { CODE: 1, PRE: 1, A: 1, BUTTON: 1, H1: 1, H2: 1, H3: 1, SCRIPT: 1, STYLE: 1, SVG: 1 };
  function skipNode(node) {
    for (var p = node.parentNode; p && p.nodeType === 1; p = p.parentNode) {
      if (SKIP[p.tagName]) return true;
      if (p.classList && (p.classList.contains("tag") ||
        p.classList.contains("reading-sources") ||
        p.classList.contains("gloss-term"))) return true;
    }
    return false;
  }

  function run() {
    var root = document.querySelector(".reading-col");
    if (!root) return;
    var found = {};
    var foundOrder = [];

    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (!n.nodeValue || !n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        if (skipNode(n)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var textNodes = [];
    var tn;
    while ((tn = walker.nextNode())) textNodes.push(tn);

    textNodes.forEach(function (node) {
      var text = node.nodeValue;
      RE.lastIndex = 0;
      var m, hits = [];
      while ((m = RE.exec(text))) {
        var entry = BY_FORM[m[1].toLowerCase()];
        if (!entry) continue;
        if (!found[entry.term]) { found[entry.term] = entry; foundOrder.push(entry.term); }
        hits.push({ start: m.index, end: m.index + m[0].length, entry: entry, text: m[0] });
      }
      if (!hits.length) return;
      var frag = document.createDocumentFragment();
      var cursor = 0;
      hits.forEach(function (h) {
        if (h.start > cursor) frag.appendChild(document.createTextNode(text.slice(cursor, h.start)));
        var span = document.createElement("span");
        span.className = "gloss-term";
        span.tabIndex = 0;
        span.textContent = h.text;
        span.dataset.glossTerm = h.entry.term;
        span.dataset.glossDef = h.entry.def;
        wire(span);
        frag.appendChild(span);
        cursor = h.end;
      });
      if (cursor < text.length) frag.appendChild(document.createTextNode(text.slice(cursor)));
      node.parentNode.replaceChild(frag, node);
    });

    buildKeyTerms(foundOrder, found);
  }

  // ---- "Key terms" block → opens the glossary modal --------------------------
  function buildKeyTerms(order, found) {
    if (!order.length) return;
    order.sort(function (a, b) { return a.toLowerCase().localeCompare(b.toLowerCase()); });
    buildModal(order, found);

    var block = document.createElement("button");
    block.type = "button";
    block.className = "gloss-block";
    block.innerHTML =
      '<span class="gb-k">Glossary</span>' +
      '<span class="gb-t">Key terms on this page</span>' +
      '<span class="gb-n">' + order.length + ' term' + (order.length === 1 ? '' : 's') +
        ' · tap to define</span>';
    block.addEventListener("click", function () { openModal(); });

    var toc = document.querySelector(".toc");
    var tocVisible = toc && getComputedStyle(toc).display !== "none";
    if (tocVisible) {
      toc.appendChild(block);
    } else {
      block.classList.add("gloss-block-inline");
      var src = document.querySelector(".reading-sources");
      if (src) src.parentNode.insertBefore(block, src);
      else document.querySelector(".reading-col").appendChild(block);
    }
  }

  // Expose for tests / tooling (read-only).
  window.GLOSSARY = GLOSSARY;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
