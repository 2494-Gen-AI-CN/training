// theme.js — light/dark theme for the training site.
//
// Loaded in <head> (render-blocking, before <body>) so the saved/system theme is
// applied to <html data-theme> before first paint — no flash of the wrong theme.
// Also injects the branded favicon and a topbar theme-toggle, so individual pages
// don't have to hand-wire either. Pages without a standard topbar are
// handled by the floating-toggle fallback.
//
// The page view (D-0044) lives here for the same two reasons: <html data-view>
// is set before first paint, and the Full / Compact / Focus switch is injected
// next to the theme toggle on every page that has the reading layout.
(function () {
  "use strict";
  var KEY = "tc_theme";
  var VIEW_KEY = "tc_view";
  var VIEWS = ["full", "compact", "focus"];
  var root = document.documentElement;

  function saved() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function resolve() {
    // Dark is the designed default (D-0020); light is the optional toggle and is
    // remembered once chosen. The OS preference is deliberately not consulted.
    var s = saved();
    return (s === "dark" || s === "light") ? s : "dark";
  }
  function current() { return root.getAttribute("data-theme") === "dark" ? "dark" : "light"; }
  function apply(t) { root.setAttribute("data-theme", t); }

  // Full is the absence of the attribute, so the stylesheet's base rules are the Full view.
  // A reader who has not chosen yet gets Compact; any choice, Full included, is remembered.
  var DEFAULT_VIEW = "compact";
  function knownView(v) { return (v === "compact" || v === "focus") ? v : "full"; }
  function savedView() {
    try {
      var v = localStorage.getItem(VIEW_KEY);
      return VIEWS.indexOf(v) === -1 ? DEFAULT_VIEW : v;
    } catch (e) { return DEFAULT_VIEW; }
  }
  function currentView() { return knownView(root.getAttribute("data-view")); }
  function applyView(v) {
    if (v === "full") root.removeAttribute("data-view");
    else root.setAttribute("data-view", v);
  }

  // 1) Apply ASAP (this runs before <body> exists → no flash).
  apply(resolve());
  applyView(savedView());

  // 2) Inject the favicon, resolved relative to THIS script's URL so it works from
  //    any directory depth (root pages, weeks/**).
  (function injectFavicon() {
    try {
      var src = (document.currentScript && document.currentScript.src) || "";
      var href = src.replace(/assets\/js\/theme\.js.*$/, "assets/favicon.svg");
      if (!href || href === src) return;
      if (document.querySelector('link[rel~="icon"]')) return; // respect a page's own icon
      var link = document.createElement("link");
      link.rel = "icon";
      link.type = "image/svg+xml";
      link.href = href;
      (document.head || root).appendChild(link);
    } catch (e) { /* no-op */ }
  })();

  // 3) Toggle button.
  var SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  var btn = null;

  function updateBtn() {
    if (!btn) return;
    var dark = current() === "dark";
    var label = dark ? "Switch to light mode" : "Switch to dark mode";
    btn.innerHTML = dark ? SUN : MOON; // show the action you'd switch TO
    btn.setAttribute("aria-label", label);
    btn.title = label;
  }
  function setTheme(t) {
    apply(t);
    try { localStorage.setItem(KEY, t); } catch (e) { /* no-op */ }
    updateBtn();
  }

  function injectToggle() {
    if (btn) return;
    btn = document.createElement("button");
    btn.type = "button";
    btn.className = "theme-toggle";
    btn.addEventListener("click", function () { setTheme(current() === "dark" ? "light" : "dark"); });

    var right = document.querySelector(".topbar-right");
    var bar = document.querySelector(".topbar");
    if (right) {
      right.insertBefore(btn, right.firstChild);
    } else if (bar) {
      bar.appendChild(btn);
    } else {
      // No standard topbar: float it out of the way.
      btn.className = "theme-toggle theme-toggle--float";
      (document.body || root).appendChild(btn);
    }
    updateBtn();
  }

  // 4) Page view switch (D-0044): Full / Compact / Focus, reading pages only.
  var VIEW_UI = {
    full: {
      label: "Full",
      title: "Full view: page menu, notes and live diagram",
      icon: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8 4v16M15 4v16"/>'
    },
    compact: {
      label: "Compact",
      title: "Compact view: wider notes, slim menu and buttons",
      icon: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M6 4v16M18 4v16"/>'
    },
    focus: {
      label: "Focus",
      title: "Focus view: the notes on their own",
      icon: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8 9h8M8 12h8M8 15h5"/>'
    }
  };
  var viewBtns = {};
  var dgmBtn = null;

  function updateSwitch() {
    var now = currentView();
    VIEWS.forEach(function (v) {
      if (viewBtns[v]) viewBtns[v].setAttribute("aria-pressed", v === now ? "true" : "false");
    });
  }

  // The notes column changes width with the view, so the text reflows. Hold the
  // first block that starts inside the window where it was; when one long block
  // fills the window, hold that one.
  function keepPlace(change) {
    var col = document.querySelector(".reading-col");
    if (!col || window.scrollY < 4) { change(); return; }
    var bar = document.querySelector(".topbar");
    var floor = bar ? bar.getBoundingClientRect().bottom : 0;
    var blocks = col.querySelectorAll("h1, h2, h3, p, pre, li, table, details, .callout");
    var anchor = null, was = 0;
    for (var i = 0; i < blocks.length; i++) {
      var r = blocks[i].getBoundingClientRect();
      if (r.height <= 0 || r.bottom <= floor) continue;
      if (!anchor) { anchor = blocks[i]; was = r.top; }
      if (r.top >= window.innerHeight) break;
      if (r.top >= floor) { anchor = blocks[i]; was = r.top; break; }
    }
    change();
    if (!anchor) return;
    var fix = function () {
      var d = anchor.getBoundingClientRect().top - was;
      if (Math.abs(d) < 1) return;
      var smooth = root.style.scrollBehavior;
      root.style.scrollBehavior = "auto";   // the stylesheet scrolls smoothly; this move must not be seen
      window.scrollBy(0, d);
      root.style.scrollBehavior = smooth;
    };
    fix();
    if (window.requestAnimationFrame) window.requestAnimationFrame(fix);
  }

  function dgmOpen() { return root.getAttribute("data-dgm") === "open"; }
  function setDgm(open, refocus) {
    if (open) root.setAttribute("data-dgm", "open");
    else root.removeAttribute("data-dgm");
    if (dgmBtn) {
      dgmBtn.setAttribute("aria-expanded", open ? "true" : "false");
      if (!open && refocus) dgmBtn.focus();
    }
  }

  function setView(v) {
    if (v === currentView()) return;
    keepPlace(function () { setDgm(false); applyView(v); });
    try { localStorage.setItem(VIEW_KEY, v); } catch (e) { /* no-op */ }
    updateSwitch();
    // glossary.js listens: Focus switches the inline term tips off.
    try { document.dispatchEvent(new CustomEvent("tc-view", { detail: { view: v } })); } catch (e) { /* no-op */ }
  }

  // Compact has no diagram in the rail; this button brings it back as a panel.
  function injectDiagramPeek() {
    var cards = document.querySelector(".side-cards");
    var dgm = document.querySelector(".side-diagram");
    if (!cards || !dgm) return;
    if (!dgm.id) dgm.id = "side-diagram";

    dgmBtn = document.createElement("button");
    dgmBtn.type = "button";
    dgmBtn.className = "side-dgm-btn";
    dgmBtn.textContent = "Diagram";
    dgmBtn.setAttribute("aria-expanded", "false");
    dgmBtn.setAttribute("aria-controls", dgm.id);
    dgmBtn.addEventListener("click", function () { setDgm(!dgmOpen()); });
    cards.insertBefore(dgmBtn, cards.firstChild);

    var x = document.createElement("button");
    x.type = "button";
    x.className = "side-dgm-close";
    x.textContent = "✕";
    x.setAttribute("aria-label", "Close diagram");
    x.addEventListener("click", function () { setDgm(false, true); });
    dgm.appendChild(x);   // not inside .stage-title: diagram.js rewrites that on every render
  }

  function typingIn(t) {
    return !!(t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName || "")));
  }
  function dialogOpen() {
    return !!document.querySelector(".modal-overlay:not([hidden]), .gloss-modal-overlay.show");
  }
  function onKey(e) {
    if (e.defaultPrevented || typingIn(e.target) || dialogOpen()) return;
    if (e.key === "Escape") {
      if (dgmOpen()) setDgm(false, true);
    } else if (e.altKey && e.shiftKey && !e.ctrlKey && !e.metaKey && e.code === "KeyF") {
      // Alt+Shift+F cycles the views. Not a bare letter: speech input and screen readers send those.
      e.preventDefault();
      setView(VIEWS[(VIEWS.indexOf(currentView()) + 1) % VIEWS.length]);
    }
  }

  function injectViewSwitch() {
    var right = document.querySelector(".topbar-right");
    if (!right || !document.querySelector(".reading2col") || right.querySelector(".view-switch")) return;
    var group = document.createElement("div");
    group.className = "view-switch";
    group.setAttribute("role", "group");
    group.setAttribute("aria-label", "Page view");
    VIEWS.forEach(function (v) {
      var ui = VIEW_UI[v];
      var b = document.createElement("button");
      b.type = "button";
      b.title = ui.title + " (Alt+Shift+F switches view)";
      b.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ui.icon + '</svg>' +
        '<span class="vs-t">' + ui.label + '</span>';
      b.addEventListener("click", function () { setView(v); });
      viewBtns[v] = b;
      group.appendChild(b);
    });
    right.insertBefore(group, right.firstChild);   // order: view switch, theme toggle, progress bar
    updateSwitch();
    injectDiagramPeek();
    document.addEventListener("keydown", onKey);
  }

  function boot() { injectToggle(); injectViewSwitch(); }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  // 5) Follow the OS theme while the user hasn't set an explicit preference.
  try {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    var onChange = function (e) { if (!saved()) setTheme(e.matches ? "dark" : "light"); };
    if (mq.addEventListener) mq.addEventListener("change", onChange);
    else if (mq.addListener) mq.addListener(onChange);
  } catch (e) { /* no-op */ }
})();
