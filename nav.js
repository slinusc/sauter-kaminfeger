/* Burger-Navigation.
   Delegierte Listener, weil der Canvas-Renderer (support.js) die Elemente
   erst per React einhaengt und Inline-Handler als {{ }}-Ausdruecke
   kompiliert wuerden. */
(function () {
  "use strict";
  var root = document.documentElement;

  function nav() { return document.getElementById("hauptnavigation"); }
  function toggleBtn() { return document.querySelector("[data-nav-toggle]"); }

  function setOpen(open) {
    var btn = toggleBtn();
    if (open) root.setAttribute("data-nav-open", "1");
    else root.removeAttribute("data-nav-open");
    if (btn) {
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.setAttribute("aria-label", open ? "Menü schliessen" : "Menü öffnen");
    }
    if (open) {
      var first = nav() && nav().querySelector("a");
      if (first) first.focus();
    } else if (btn && document.activeElement !== document.body) {
      btn.focus();
    }
  }

  function isOpen() { return root.hasAttribute("data-nav-open"); }

  document.addEventListener("click", function (e) {
    if (!e.target.closest) return;
    if (e.target.closest("[data-nav-toggle]")) {
      e.preventDefault();
      setOpen(!isOpen());
      return;
    }
    // Klick auf einen Link im offenen Overlay schliesst es
    if (isOpen() && e.target.closest("#hauptnavigation a")) setOpen(false);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && isOpen()) setOpen(false);
  });

  // Wird der Viewport wieder breit, Overlay-Zustand aufheben.
  var mq = window.matchMedia("(min-width: 901px)");
  (mq.addEventListener ? mq.addEventListener.bind(mq, "change") : mq.addListener.bind(mq))(
    function () { if (mq.matches && isOpen()) setOpen(false); }
  );
})();
