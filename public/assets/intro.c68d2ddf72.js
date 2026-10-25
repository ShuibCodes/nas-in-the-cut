/* Runs before the page paints: decides whether the intro film shows. */
(function () {
  var d = document.documentElement, seen = false, q = location.search;
  try { seen = sessionStorage.getItem("nitc-intro") === "seen"; } catch (e) {}
  if (/[?&]intro\b/.test(q)) seen = false;
  if (/[?&]nointro\b/.test(q)) seen = true;
  d.classList.add(seen ? "ready" : "intro-on");
})();
