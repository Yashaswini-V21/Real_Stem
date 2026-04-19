/* ═══════════════════════════════════════════════
   RealSTEM — Auth Page JavaScript
   Handles login / register toggle and form submission
   ═══════════════════════════════════════════════ */

(function () {
  "use strict";

  const titleEl = document.getElementById("authTitle");
  const subtitleEl = document.getElementById("authSubtitle");
  const nameRow = document.getElementById("nameRow");
  const submitBtn = document.getElementById("authSubmit");
  const toggleBtn = document.getElementById("authToggle");
  const promptEl = document.getElementById("authPrompt");
  const form = document.getElementById("authForm");

  let isRegister = new URLSearchParams(window.location.search).get("register") === "true";

  function updateUI() {
    if (isRegister) {
      titleEl.textContent = "Create Account";
      subtitleEl.textContent = "Join RealSTEM and begin creating AI-powered STEM lessons.";
      submitBtn.textContent = "Initialize Account";
      toggleBtn.textContent = "Log In";
      promptEl.textContent = "Already have an account?";
      nameRow.classList.add("visible");
    } else {
      titleEl.textContent = "Access Portal";
      subtitleEl.textContent = "Welcome back. Log in to your RealSTEM dashboard.";
      submitBtn.textContent = "Authenticate";
      toggleBtn.textContent = "Sign Up";
      promptEl.textContent = "Don't have an account?";
      nameRow.classList.remove("visible");
    }
  }

  // Initialize state
  updateUI();

  // Toggle handler
  toggleBtn.addEventListener("click", function () {
    isRegister = !isRegister;
    updateUI();
    // Update URL without reload
    const url = new URL(window.location);
    if (isRegister) {
      url.searchParams.set("register", "true");
    } else {
      url.searchParams.delete("register");
    }
    window.history.replaceState({}, "", url);
  });

  // Form submission
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
      shakeCard();
      return;
    }

    if (isRegister) {
      const name = document.getElementById("fullName").value.trim();
      if (!name) {
        shakeCard();
        return;
      }
      // Store user info
      localStorage.setItem("realstem_user", JSON.stringify({ name: name, email: email }));
    } else {
      // Check for existing user or create default
      let user = localStorage.getItem("realstem_user");
      if (!user) {
        localStorage.setItem("realstem_user", JSON.stringify({ name: "Teacher", email: email }));
      }
    }

    // Add success animation
    submitBtn.textContent = "✓ Success";
    submitBtn.style.background = "linear-gradient(135deg, #10b981, #059669)";
    submitBtn.disabled = true;

    setTimeout(function () {
      window.location.href = "/dashboard.html";
    }, 800);
  });

  function shakeCard() {
    const card = document.getElementById("authCard");
    card.style.animation = "none";
    card.offsetHeight; // Force reflow
    card.style.animation = "shake 0.4s ease";
  }

  // Add shake keyframe dynamically
  const style = document.createElement("style");
  style.textContent = "@keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translateX(-8px)}40%{transform:translateX(8px)}60%{transform:translateX(-4px)}80%{transform:translateX(4px)}}";
  document.head.appendChild(style);

})();
