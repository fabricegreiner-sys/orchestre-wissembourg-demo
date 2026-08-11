/* Orchestre de Chambre de Wissembourg — JS minimal, sans dépendance. */
(function () {
  "use strict";

  // --- Menu mobile -----------------------------------------------------
  var burger = document.querySelector(".burger");
  var nav = document.getElementById("nav");
  if (burger && nav) {
    burger.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // --- Façade vidéo : aucun appel à YouTube tant que l'utilisateur n'a
  //     pas cliqué (pas de cookie tiers au chargement → conforme RGPD).
  document.querySelectorAll(".video__facade").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = btn.getAttribute("data-video");
      var frame = document.createElement("iframe");
      frame.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
      frame.title = btn.getAttribute("data-title") || "Vidéo";
      frame.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; picture-in-picture";
      frame.allowFullscreen = true;
      btn.parentNode.replaceChild(frame, btn);
    });
  });

  // --- Mémorisation de la langue choisie -------------------------------
  document.querySelectorAll(".lang a").forEach(function (a) {
    a.addEventListener("click", function () {
      try { localStorage.setItem("ocw-lang", a.getAttribute("hreflang")); } catch (e) {}
    });
  });
})();
