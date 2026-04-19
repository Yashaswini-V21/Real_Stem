/* ═══════════════════════════════════════════════
   RealSTEM — Dashboard JavaScript
   Lesson generator, example chips, API integration
   ═══════════════════════════════════════════════ */

(function () {
  "use strict";

  // ─── User Greeting ───
  var userRaw = localStorage.getItem("realstem_user");
  if (userRaw) {
    try {
      var user = JSON.parse(userRaw);
      var greetEl = document.getElementById("dashGreeting");
      var avatarEl = document.getElementById("dashAvatar");
      if (greetEl && user.name) greetEl.textContent = "Welcome, " + user.name;
      if (avatarEl && user.name) avatarEl.textContent = user.name.charAt(0).toUpperCase();
    } catch (_) { /* ignore */ }
  }

  // ─── Elements ───
  var form = document.getElementById("lessonForm");
  var headlineInput = document.getElementById("headline");
  var localeSelect = document.getElementById("locale");
  var gradeSelect = document.getElementById("gradeLevel");
  var subjectSelect = document.getElementById("subject");
  var submitBtn = document.getElementById("genSubmit");
  var errorEl = document.getElementById("genError");
  var outputContent = document.getElementById("outputContent");
  var exampleChips = document.getElementById("exampleChips");

  // ─── Example Chips ───
  if (exampleChips) {
    exampleChips.addEventListener("click", function (e) {
      var chip = e.target.closest(".gen-example-chip");
      if (!chip) return;
      var hl = chip.getAttribute("data-headline");
      if (hl && headlineInput) headlineInput.value = hl;
    });
  }

  // ─── Form Submit ───
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      generateLesson();
    });
  }

  function generateLesson() {
    var headline = headlineInput.value.trim();
    if (!headline) {
      showError("Please enter a news headline.");
      return;
    }

    var payload = {
      headline: headline,
      locale: localeSelect.value,
      gradeLevel: gradeSelect.value,
      subject: subjectSelect.value
    };

    // UI: loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Generating Lesson...';
    errorEl.style.display = "none";

    fetch("/api/generate-lesson", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
      .then(function (res) {
        if (!res.ok) {
          return res.json().then(function (data) {
            throw new Error(data.error || "Generation failed.");
          });
        }
        return res.json();
      })
      .then(function (data) {
        renderLesson(data.lesson);
      })
      .catch(function (err) {
        showError(err.message || "Something went wrong.");
      })
      .finally(function () {
        submitBtn.disabled = false;
        submitBtn.innerHTML = "Generate AI Lesson";
      });
  }

  function showError(msg) {
    errorEl.textContent = msg;
    errorEl.style.display = "block";
  }

  // ─── Render Lesson Result ───
  function renderLesson(lesson) {
    if (!lesson || !outputContent) return;

    // Build standards list
    var standardsHTML = "";
    if (lesson.standards && lesson.standards.length) {
      standardsHTML = '<div class="lesson-block">';
      standardsHTML += '<p class="lesson-block-title">Standards</p>';
      standardsHTML += "<ul>";
      for (var i = 0; i < lesson.standards.length; i++) {
        standardsHTML += "<li>" + escapeHTML(lesson.standards[i]) + "</li>";
      }
      standardsHTML += "</ul></div>";
    }

    // Build lesson flow
    var flowHTML = "";
    if (lesson.lessonFlow && lesson.lessonFlow.length) {
      flowHTML = '<div class="lesson-block">';
      flowHTML += '<p class="lesson-block-title">Lesson Flow</p>';
      flowHTML += "<ul>";
      for (var j = 0; j < lesson.lessonFlow.length; j++) {
        flowHTML += "<li>" + escapeHTML(lesson.lessonFlow[j]) + "</li>";
      }
      flowHTML += "</ul></div>";
    }

    // Build student task
    var taskHTML = "";
    if (lesson.studentTask) {
      taskHTML = '<div class="lesson-block">';
      taskHTML += '<p class="lesson-block-title">Student Task</p>';
      taskHTML += '<div class="lesson-task-box">' + escapeHTML(lesson.studentTask) + "</div>";
      taskHTML += "</div>";
    }

    // Build teacher notes
    var notesHTML = "";
    if (lesson.teacherNotes && lesson.teacherNotes.length) {
      notesHTML = '<div class="lesson-block">';
      notesHTML += '<p class="lesson-block-title">Teacher Notes</p>';
      notesHTML += "<ul>";
      for (var k = 0; k < lesson.teacherNotes.length; k++) {
        notesHTML += "<li>" + escapeHTML(lesson.teacherNotes[k]) + "</li>";
      }
      notesHTML += "</ul></div>";
    }

    outputContent.innerHTML =
      '<div class="lesson-result">' +
        '<div class="lesson-result-header">' +
          '<span class="badge">' + escapeHTML(lesson.gradeLevel) + " · " + escapeHTML(lesson.subject) + "</span>" +
          '<span class="badge badge-live">AI DRAFT</span>' +
        "</div>" +
        "<h4>" + escapeHTML(lesson.topic) + "</h4>" +
        "<p>" + escapeHTML(lesson.relevanceSummary) + "</p>" +
        standardsHTML +
        flowHTML +
        taskHTML +
        notesHTML +
      "</div>";
  }

  // ─── Utility ───
  function escapeHTML(str) {
    if (!str) return "";
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

})();
