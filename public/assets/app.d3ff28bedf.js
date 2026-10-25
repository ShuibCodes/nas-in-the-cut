(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------------------------------------------------------------- forms
  // The endpoint lives in data-endpoint on each form so the email provider
  // can be swapped without touching this file.
  var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function setMsg(form, text, state) {
    var msg = form.querySelector(".msg");
    msg.textContent = text;
    if (state) msg.setAttribute("data-state", state); else msg.removeAttribute("data-state");
  }

  document.querySelectorAll("form.signup").forEach(function (form) {
    var input = form.querySelector("input[type=email]");
    var button = form.querySelector("button[type=submit]");

    input.addEventListener("input", function () {
      if (input.getAttribute("aria-invalid") === "true" && EMAIL.test(input.value.trim())) {
        input.removeAttribute("aria-invalid");
        setMsg(form, "", null);
      }
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var value = input.value.trim();
      if (form.querySelector(".hp input").value) return;
      if (!EMAIL.test(value)) {
        input.setAttribute("aria-invalid", "true");
        setMsg(form, value ? "That email doesn’t look right. Check it and try again." : "Add your email and issue #1 is yours.", "error");
        input.focus();
        return;
      }
      input.removeAttribute("aria-invalid");
      var endpoint = form.getAttribute("data-endpoint");
      if (!endpoint) {
        setMsg(form, "Sign-ups open at launch. Message @nasinthecut on Instagram to get issue #1 first.", "ok");
        return;
      }
      button.disabled = true;
      setMsg(form, "Signing you up.", null);
      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: value, source: form.id })
      }).then(function (r) {
        if (!r.ok) throw new Error(String(r.status));
        form.reset();
        setMsg(form, "You’re in. Issue #1 is on its way to your inbox.", "ok");
      }).catch(function () {
        setMsg(form, "That didn’t go through. Try again in a minute.", "error");
      }).finally(function () {
        button.disabled = false;
      });
    });
  });

  // ---------------------------------------------------------------- scroll
  var head = document.getElementById("site-head");
  var dock = document.getElementById("dock");
  var heroForm = document.getElementById("subscribe");
  var finalSec = document.getElementById("join");
  var lastY = window.scrollY;
  var ticking = false;

  function setDock(show) {
    if (!dock || show === dock.classList.contains("show")) return;
    dock.classList.toggle("show", show);
    if (show) { dock.removeAttribute("inert"); dock.removeAttribute("aria-hidden"); }
    else { dock.setAttribute("inert", ""); dock.setAttribute("aria-hidden", "true"); }
  }

  function onScroll() {
    ticking = false;
    var y = window.scrollY;
    head.classList.toggle("scrolled", y > 8);
    if (!reduce) {
      if (y > lastY + 4 && y > 240 && !head.contains(document.activeElement)) head.classList.add("away");
      else if (y < lastY - 4 || y < 240) head.classList.remove("away");
    }
    lastY = y;
    if (heroForm && finalSec) {
      setDock(heroForm.getBoundingClientRect().bottom < 0 && finalSec.getBoundingClientRect().top > window.innerHeight);
    }
  }

  window.addEventListener("scroll", function () {
    if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
  }, { passive: true });
  window.addEventListener("resize", onScroll);
  onScroll();
  head.addEventListener("focusin", function () { head.classList.remove("away"); });

  // ---------------------------------------------------------------- progress
  var bar = document.getElementById("progress");
  function setProgress() {
    if (!bar) return;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.transform = "scaleX(" + (max > 0 ? Math.min(1, window.scrollY / max) : 0) + ")";
  }
  window.addEventListener("scroll", setProgress, { passive: true });
  window.addEventListener("resize", setProgress);
  setProgress();

  // ---------------------------------------------------------------- Dubai clock
  // Dubai is UTC+4 all year, with no daylight saving, so a fixed offset is exact.
  var clock = document.getElementById("clock");
  var clock2 = document.getElementById("clock-2");
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function tick() {
    var d = new Date(Date.now() + 4 * 3600 * 1000);
    var h = d.getUTCHours(), m = d.getUTCMinutes();
    var mins = (7 * 60 - (h * 60 + m) + 1440) % 1440 || 1440;
    var wait = Math.floor(mins / 60) + "h " + pad(mins % 60) + "m";
    if (clock) clock.textContent = "Dubai " + pad(h) + ":" + pad(m) + ". Next issue in " + wait + ".";
    if (clock2) clock2.textContent = "The next issue lands in " + wait + ", at 7:00 Dubai time.";
  }
  tick();
  setInterval(tick, 20000);

  // ---------------------------------------------------------------- issues
  document.querySelectorAll(".issue-btn").forEach(function (btn) {
    var panel = document.getElementById(btn.getAttribute("aria-controls"));
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", open ? "false" : "true");
      panel.hidden = open;
    });
  });

  // ---------------------------------------------------------------- rails
  document.querySelectorAll(".rail-ctl").forEach(function (ctl) {
    var rail = document.getElementById(ctl.getAttribute("data-for"));
    if (!rail) return;
    var items = rail.children;
    var cur = ctl.querySelector("[data-cur]");
    var line = ctl.querySelector(".rail-line span");
    var prev = ctl.querySelector('[data-dir="-1"]');
    var next = ctl.querySelector('[data-dir="1"]');
    var index = 0;

    function step() {
      return items.length > 1 ? items[1].offsetLeft - items[0].offsetLeft : rail.clientWidth;
    }
    function update() {
      var max = rail.scrollWidth - rail.clientWidth;
      ctl.classList.toggle("static", max <= 4);
      var atEnd = rail.scrollLeft >= max - 4;
      index = atEnd ? items.length - 1 : Math.round(rail.scrollLeft / step());
      index = Math.max(0, Math.min(items.length - 1, index));
      cur.textContent = pad(index + 1);
      line.style.transform = "scaleX(" + ((index + 1) / items.length) + ")";
      prev.setAttribute("aria-disabled", rail.scrollLeft <= 4 ? "true" : "false");
      next.setAttribute("aria-disabled", atEnd ? "true" : "false");
      for (var i = 0; i < items.length; i++) items[i].classList.toggle("is-cur", i === index);
    }
    function go(dir) {
      var target = Math.max(0, Math.min(items.length - 1, index + dir));
      rail.scrollTo({ left: items[target].offsetLeft - items[0].offsetLeft, behavior: reduce ? "auto" : "smooth" });
    }
    [prev, next].forEach(function (b) {
      b.addEventListener("click", function () {
        if (b.getAttribute("aria-disabled") === "true") return;
        go(+b.getAttribute("data-dir"));
      });
    });
    rail.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); go(1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(-1); }
    });
    var raf = 0;
    rail.addEventListener("scroll", function () {
      if (!raf) raf = requestAnimationFrame(function () { raf = 0; update(); });
    }, { passive: true });
    window.addEventListener("resize", update);
    update();
  });

  // ---------------------------------------------------------------- numbers
  // The real figure is in the HTML. Motion only replays it from zero once,
  // when the band first scrolls into view.
  if ("IntersectionObserver" in window && !reduce) {
    var nums = document.querySelectorAll("[data-count]");
    var nio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        nio.unobserve(en.target);
        var el = en.target, end = +el.getAttribute("data-count"), t0 = 0;
        function frame(t) {
          if (!t0) t0 = t;
          var p = Math.min(1, (t - t0) / 1400);
          el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
          if (p < 1) requestAnimationFrame(frame);
        }
        el.textContent = "0";
        requestAnimationFrame(frame);
      });
    }, { threshold: 0.6 });
    nums.forEach(function (n) { nio.observe(n); });
  }

  // ---------------------------------------------------------------- intro film
  var root = document.documentElement;
  var introEl = document.getElementById("intro");
  if (introEl) (function () {
    var film = document.getElementById("intro-film");
    var audio = document.getElementById("intro-audio");
    var enterBtn = document.getElementById("intro-enter");
    var soundBtn = document.getElementById("intro-sound");
    var bar = document.getElementById("intro-time");
    var replay = document.getElementById("replay");
    var behind = [document.getElementById("site-head"), document.getElementById("main"), document.querySelector(".site-foot")];
    var leaving = false, fadeTimer = 0;

    function setBehind(off) {
      behind.forEach(function (el) { if (!el) return; if (off) el.setAttribute("inert", ""); else el.removeAttribute("inert"); });
    }
    function setSound(on) {
      soundBtn.setAttribute("aria-pressed", on ? "true" : "false");
      soundBtn.querySelector(".lbl").textContent = on ? "Sound off" : "Sound on";
    }
    function playSound() {
      clearInterval(fadeTimer);
      audio.volume = 1;
      var p = audio.play();
      if (p && p.then) p.then(function () { setSound(true); }, function () { setSound(false); });
      else setSound(!audio.paused);
    }
    function fadeOut(done) {
      clearInterval(fadeTimer);
      if (audio.paused) { if (done) done(); return; }
      fadeTimer = setInterval(function () {
        var v = Math.max(0, audio.volume - 0.06);
        audio.volume = v;
        if (v <= 0) { clearInterval(fadeTimer); audio.pause(); if (done) done(); }
      }, 60);
    }
    function start() {
      leaving = false;
      introEl.hidden = false;
      introEl.classList.remove("leaving");
      root.classList.add("intro-on");
      setBehind(true);
      if (!reduce) {
        if (!film.getAttribute("src")) {
          film.setAttribute("src", film.getAttribute(window.matchMedia("(min-width: 700px)").matches ? "data-src-lg" : "data-src-sm"));
        }
        film.muted = true; film.defaultMuted = true;  // muted film may autoplay everywhere, iPhone included
        try { film.currentTime = 0; } catch (e) {}
        var v = film.play();
        if (v && v.catch) v.catch(function () {});
      }
      try { audio.currentTime = 0; } catch (e) {}
      playSound();
      enterBtn.focus({ preventScroll: true });
    }
    function enter() {
      if (leaving) return;
      leaving = true;
      try { sessionStorage.setItem("nitc-intro", "seen"); } catch (e) {}
      fadeOut();
      introEl.classList.add("leaving");
      root.classList.add("ready");
      setTimeout(function () {
        introEl.hidden = true;
        root.classList.remove("intro-on");
        setBehind(false);
        film.pause();
        onScroll();
      }, reduce ? 0 : 1150);
    }

    enterBtn.addEventListener("click", enter);
    soundBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      if (audio.paused) playSound(); else { audio.pause(); setSound(false); }
    });
    introEl.addEventListener("click", function (e) {
      if (!e.target.closest("button")) enter();
    });
    introEl.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { e.preventDefault(); enter(); }
      if (e.key === "Tab") {  // keep focus inside the intro
        var f = [soundBtn, enterBtn], i = f.indexOf(document.activeElement);
        e.preventDefault();
        f[(i + (e.shiftKey ? f.length - 1 : 1)) % f.length].focus();
      }
    });
    film.addEventListener("timeupdate", function () {
      if (film.duration) bar.style.transform = "scaleX(" + Math.min(1, film.currentTime / film.duration) + ")";
    });
    film.addEventListener("ended", enter);
    if (replay) replay.addEventListener("click", function () { window.scrollTo(0, 0); start(); });

    if (root.classList.contains("intro-on")) start();
    else introEl.hidden = true;
  })();

  // ---------------------------------------------------------------- more of this
  // Quietly counts which content people want more of. The count is private.
  var SIG = "nitc-signals";
  function sent() { try { return JSON.parse(localStorage.getItem(SIG) || "[]"); } catch (e) { return []; } }
  var already = sent();
  function record(id) {
    var list = sent(); list.push(id);
    try { localStorage.setItem(SIG, JSON.stringify(list)); } catch (e) {}
    var body = JSON.stringify({ id: id });
    try {
      if (navigator.sendBeacon && navigator.sendBeacon("signal.php", new Blob([body], { type: "application/json" }))) return;
    } catch (e) {}
    if (window.fetch) fetch("signal.php", { method: "POST", headers: { "Content-Type": "application/json" }, body: body, keepalive: true }).catch(function () {});
  }
  // Every "More of this" ends at the newsletter box: the last one on this page, or the home page's.
  function toSignup() {
    var forms = document.querySelectorAll("form.signup");
    var form = forms[forms.length - 1];
    if (!form) { location.href = "./#subscribe"; return; }
    var input = form.querySelector("input[type=email]");
    form.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
    setTimeout(function () { input.focus({ preventScroll: true }); }, reduce ? 0 : 600);
  }
  document.querySelectorAll(".more").forEach(function (b) {
    var id = b.getAttribute("data-signal");
    if (already.indexOf(id) > -1) b.setAttribute("aria-pressed", "true");
    b.addEventListener("click", function () {
      if (b.getAttribute("aria-pressed") !== "true") {
        b.setAttribute("aria-pressed", "true");
        record(id);
      }
      toSignup();
    });
  });

  // ---------------------------------------------------------------- map
  var places = document.querySelectorAll(".place");
  places.forEach(function (p) {
    var mk = document.querySelector('.mk[data-mk="' + p.getAttribute("data-mk") + '"]');
    function on(state) {
      places.forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
      document.querySelectorAll(".mk.on").forEach(function (m) { m.classList.remove("on"); });
      if (state) { p.setAttribute("aria-pressed", "true"); if (mk) mk.classList.add("on"); }
    }
    p.addEventListener("click", function () { on(p.getAttribute("aria-pressed") !== "true"); });
    p.addEventListener("mouseenter", function () { if (mk) mk.classList.add("hot"); });
    p.addEventListener("mouseleave", function () { if (mk) mk.classList.remove("hot"); });
  });

  // ---------------------------------------------------------------- In The Room lightbox
  var lb = document.getElementById("lb");
  var roomData = document.getElementById("room-data");
  if (lb && roomData && lb.showModal) (function () {
    var items = JSON.parse(roomData.textContent);
    var cap = document.getElementById("lb-cap");
    var img = document.createElement("img");  // made on demand, so a closed viewer holds no empty image
    img.id = "lb-img"; img.decoding = "async";
    var count = lb.querySelector(".lb-count"), at = 0, x0 = null;
    function show(i) {
      if (!img.parentNode) document.getElementById("lb-fig").insertBefore(img, cap);
      at = (i + items.length) % items.length;
      img.src = items[at].src; img.alt = items[at].alt;
      cap.textContent = items[at].cap;
      count.textContent = pad(at + 1) + " / " + pad(items.length);
    }
    document.querySelectorAll(".rm-open").forEach(function (b) {
      b.addEventListener("click", function () { show(+b.getAttribute("data-i")); lb.showModal(); });
    });
    lb.querySelectorAll("[data-dir]").forEach(function (b) {
      b.addEventListener("click", function () { show(at + (+b.getAttribute("data-dir"))); });
    });
    lb.querySelector(".lb-close").addEventListener("click", function () { lb.close(); });
    lb.addEventListener("click", function (e) { if (e.target === lb) lb.close(); });
    lb.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") show(at + 1);
      if (e.key === "ArrowLeft") show(at - 1);
    });
    lb.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 50) show(at + (dx < 0 ? 1 : -1));
    }, { passive: true });
  })();

  // ---------------------------------------------------------------- In The Cup seat form
  var cupForm = document.getElementById("cup-form");
  if (cupForm) (function () {
    var msg = document.getElementById("cup-msg");
    var btn = cupForm.querySelector("button[type=submit]");
    var nameEl = document.getElementById("cup-name"), emailEl = document.getElementById("cup-email");
    var modeSet = document.getElementById("cup-mode");
    function say(text, state) {
      msg.textContent = text;
      if (state) msg.setAttribute("data-state", state); else msg.removeAttribute("data-state");
    }
    if (/[?&]seat=saved/.test(location.search)) say("You’re on the list. Table details reach you first.", "ok");
    if (/[?&]seat=error/.test(location.search)) say("That didn’t go through. Check your details and try again.", "error");
    [nameEl, emailEl].forEach(function (el) {
      el.addEventListener("input", function () { if (el.value.trim()) el.removeAttribute("aria-invalid"); });
    });
    cupForm.addEventListener("change", function (e) { if (e.target.name === "mode") modeSet.removeAttribute("aria-invalid"); });
    cupForm.addEventListener("submit", function (e) {
      e.preventDefault();
      if (cupForm.querySelector(".hp input").value) return;
      var mode = cupForm.querySelector("input[name=mode]:checked");
      var bad = [];
      if (!nameEl.value.trim()) bad.push(nameEl);
      if (!EMAIL.test(emailEl.value.trim())) bad.push(emailEl);
      [nameEl, emailEl].forEach(function (el) { if (bad.indexOf(el) > -1) el.setAttribute("aria-invalid", "true"); else el.removeAttribute("aria-invalid"); });
      if (!mode) modeSet.setAttribute("aria-invalid", "true"); else modeSet.removeAttribute("aria-invalid");
      if (bad.length || !mode) {
        say(bad.length ? "Add your name and a valid email to save your seat." : "Choose in person or online.", "error");
        (bad[0] || cupForm.querySelector("input[name=mode]")).focus();
        return;
      }
      btn.disabled = true;
      say("Saving your seat.", null);
      fetch(cupForm.getAttribute("action"), { method: "POST", headers: { "Accept": "application/json" }, body: new FormData(cupForm) })
        .then(function (r) { return r.json().catch(function () { return { ok: false }; }).then(function (d) { return { r: r, d: d }; }); })
        .then(function (x) {
          if (!x.r.ok || !x.d.ok) throw new Error(x.d && x.d.message || "failed");
          cupForm.reset();
          say("You’re on the list. Table details reach you first.", "ok");
        })
        .catch(function (err) {
          var t = err && err.message && err.message !== "failed" && err.message.indexOf("JSON") < 0 ? err.message : "That didn’t go through. Try again in a minute, or message @nasinthecut on Instagram.";
          say(t, "error");
        })
        .finally(function () { btn.disabled = false; });
    });
  })();

  // ---------------------------------------------------------------- reveal
  // Content is visible by default. Only things below the fold get the
  // reveal treatment, so nothing is ever hidden at rest on load.
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -10% 0px" });
    document.querySelectorAll("[data-reveal]").forEach(function (el) {
      if (el.getBoundingClientRect().top > window.innerHeight) {
        el.classList.add("reveal");
        if (el.classList.contains("def")) el.style.transitionDelay = (Array.prototype.indexOf.call(el.parentNode.children, el) * 90) + "ms";
        io.observe(el);
      }
    });
  }
})();
