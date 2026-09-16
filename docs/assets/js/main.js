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

  // --- Vidéo de fond du bandeau ----------------------------------------
  // Chargée uniquement si l'utilisateur ne demande pas de mouvement réduit
  // et n'est pas en économie de données. Sinon l'affiche (poster) suffit.
  var hero = document.querySelector(".hero__video");
  if (hero) {
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var saveData = navigator.connection && navigator.connection.saveData;
    if (!reduced && !saveData) {
      try {
        JSON.parse(hero.getAttribute("data-sources")).forEach(function (s) {
          var el = document.createElement("source");
          el.src = s.src; el.type = s.type;
          hero.appendChild(el);
        });
        hero.load();
        var p = hero.play();
        if (p && p.catch) { p.catch(function () {}); }  // autoplay refusé : l'affiche reste
      } catch (e) {}
    }
    // Économise batterie et bande passante quand l'onglet n'est pas visible.
    document.addEventListener("visibilitychange", function () {
      if (!hero.src && !hero.querySelector("source")) { return; }
      if (document.hidden) { hero.pause(); } else { hero.play().catch(function () {}); }
    });
  }

  // --- Mémorisation de la langue choisie -------------------------------
  document.querySelectorAll(".lang a").forEach(function (a) {
    a.addEventListener("click", function () {
      try { localStorage.setItem("ocw-lang", a.getAttribute("hreflang")); } catch (e) {}
    });
  });
})();
