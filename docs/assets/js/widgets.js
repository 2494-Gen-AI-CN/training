/* widgets.js — small inline learning widgets for notes pages.
   Declared via markup; auto-initialized on DOMContentLoaded. Pure client-side.

   1. Interaction legend:   <div class="ix-legend"></div>
   2. Predict-then-reveal:  <div class="ix-predict" data-q="..." data-a="..."></div>
   3. Spot-the-problem:     <div class="ix-spot" data-snippet="..." data-q="..." data-a="..."></div>
*/
(function () {
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
        `<span class="ixl-chip">click diagram nodes</span>`;
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    legend(document.querySelectorAll(".ix-legend"));
    predict(document.querySelectorAll(".ix-predict"));
    spot(document.querySelectorAll(".ix-spot"));
  });
})();
