/* ═══════════════════════════════════════════════
   RealSTEM — Main Application JavaScript
   Splash screen, scroll animations, header state
   ═══════════════════════════════════════════════ */

(function () {
  "use strict";

  // ─── Splash Screen ───
  const splash = document.getElementById("splashScreen");
  if (splash) {
    window.addEventListener("load", function () {
      setTimeout(function () {
        splash.classList.add("fade-out");
        setTimeout(function () {
          splash.remove();
        }, 800);
      }, 2800);
    });
  }

  // ─── Scroll-based Header ───
  const header = document.getElementById("siteHeader");
  if (header) {
    let lastScroll = 0;
    window.addEventListener("scroll", function () {
      const scrollY = window.scrollY;
      if (scrollY > 60) {
        header.classList.add("scrolled");
      } else {
        header.classList.remove("scrolled");
      }
      lastScroll = scrollY;
    }, { passive: true });
  }

  // ─── Scroll Reveal (Intersection Observer) ───
  const revealElements = document.querySelectorAll(".reveal");
  if (revealElements.length > 0 && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );
    revealElements.forEach(function (el) {
      observer.observe(el);
    });
  }

  // ─── Smooth Scroll for Anchor Links ───
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href");
      if (targetId === "#") return;
      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

})();
