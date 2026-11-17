(function () {
  // Sticky nav border
  var nav = document.getElementById("nav");
  if (nav) {
    var onScroll = function () { nav.classList.toggle("scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Mobile nav
  document.querySelectorAll("[data-nav-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open);
    });
  });
  document.querySelectorAll(".nav-links a").forEach(function (a) {
    a.addEventListener("click", function () { nav && nav.classList.remove("open"); });
  });

  // Dashboard side menu
  document.querySelectorAll("[data-menu]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelector(".portal").classList.toggle("menu-open");
    });
  });
  var portal = document.querySelector(".portal");
  if (portal) {
    portal.addEventListener("click", function (e) {
      if (portal.classList.contains("menu-open") && !e.target.closest(".side") && !e.target.closest("[data-menu]")) {
        portal.classList.remove("menu-open");
      }
    });
  }

  // Flash messages fade out
  setTimeout(function () {
    document.querySelectorAll(".flash.success, .flash.info").forEach(function (f) { f.remove(); });
  }, 7000);

  // Order form: only show plans for the chosen service
  var cat = document.getElementById("id_category");
  var plan = document.getElementById("id_plan");
  var plansData = document.getElementById("plans-data");
  if (cat && plan && plansData) {
    var plans = JSON.parse(plansData.textContent);
    var initial = plan.value;
    var fill = function () {
      var list = plans[cat.value] || [];
      plan.innerHTML = "";
      list.forEach(function (p) {
        var o = document.createElement("option");
        o.value = p[0]; o.textContent = p[1];
        if (p[0] === initial) o.selected = true;
        plan.appendChild(o);
      });
    };
    cat.addEventListener("change", function () { initial = ""; fill(); });
    fill();
  }

  // 2FA code inputs: digits only
  document.querySelectorAll("input[autocomplete='one-time-code']").forEach(function (i) {
    i.addEventListener("input", function () { i.value = i.value.replace(/[^0-9 ]/g, "").slice(0, 7); });
  });

  // Copy buttons
  document.querySelectorAll("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var text = document.querySelector(b.dataset.copy).innerText;
      navigator.clipboard.writeText(text).then(function () {
        var t = b.textContent; b.textContent = "Copied"; setTimeout(function () { b.textContent = t; }, 1600);
      });
    });
  });
})();
