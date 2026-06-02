(function () {
  var root = document.documentElement;
  var storageKey = "tailskills-theme";
  var navToggle = document.querySelector(".nav-toggle");
  var navLinks = document.querySelector("#nav-links");
  var themeToggle = document.querySelector("[data-theme-toggle]");
  var heroSection = document.querySelector("#hero");
  var compressionSlider = document.querySelector("#compression-slider");
  var retentionOutput = document.querySelector("#retention-output");
  var retentionValue = document.querySelector("[data-retention-value]");
  var depthLabel = document.querySelector("[data-depth-label]");
  var depthButtons = document.querySelectorAll("[data-depth]");
  var taxonomyTriggers = document.querySelectorAll(".taxonomy-trigger");

  function getCssVar(name) {
    return getComputedStyle(root).getPropertyValue(name).trim();
  }

  function systemPrefersDark() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function preferredTheme() {
    var saved = window.localStorage.getItem(storageKey);
    if (saved === "light" || saved === "dark") {
      return saved;
    }
    return systemPrefersDark() ? "dark" : "light";
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    var isDark = theme === "dark";
    if (themeToggle) {
      themeToggle.setAttribute("aria-label", isDark ? "Switch to light theme" : "Switch to dark theme");
      var icon = themeToggle.querySelector(".theme-toggle__icon");
      if (icon) {
        icon.textContent = isDark ? "\u263e" : "\u263c";
      }
    }
    document.dispatchEvent(new CustomEvent("tailskills:themechange", {
      detail: {
        theme: theme,
        colors: {
          tail: getCssVar("--accent-tail"),
          common: getCssVar("--accent-common"),
          highlight: getCssVar("--accent-highlight")
        }
      }
    }));
  }

  applyTheme(preferredTheme());

  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      window.localStorage.setItem(storageKey, next);
      applyTheme(next);
    });
  }

  if (navToggle && navLinks) {
    navToggle.addEventListener("click", function () {
      var isOpen = navLinks.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });

    navLinks.addEventListener("click", function (event) {
      if (event.target && event.target.tagName === "A") {
        navLinks.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  var revealTargets = document.querySelectorAll(".page-section");
  revealTargets.forEach(function (section) {
    section.classList.add("reveal");
  });

  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.16 });
    revealTargets.forEach(function (section) {
      observer.observe(section);
    });
  } else {
    revealTargets.forEach(function (section) {
      section.classList.add("is-visible");
    });
  }

  window.TailSkills = window.TailSkills || {};
  window.TailSkills.getCssVar = getCssVar;

  var compressionStates = [
    { label: "S1 baseline skill", retention: 100.0, opacity: 1.0, blur: 0 },
    { label: "S2 shorter rewrite", retention: 43.5, opacity: 0.68, blur: 1 },
    { label: "S3 standardized rewrite", retention: 22.7, opacity: 0.42, blur: 2 },
    { label: "S4 compressed skill", retention: 15.7, opacity: 0.2, blur: 3 }
  ];

  function updateCompression(depth) {
    if (!heroSection) {
      return;
    }
    var index = Math.max(0, Math.min(compressionStates.length - 1, Number(depth) || 0));
    var state = compressionStates[index];
    var retained = state.retention.toFixed(1) + "%";
    var commonShare = Math.max(0, 100 - state.retention).toFixed(1) + "%";
    heroSection.style.setProperty("--tail-opacity", String(state.opacity));
    heroSection.style.setProperty("--tail-blur", state.blur + "px");
    heroSection.style.setProperty("--tail-retention", retained);
    heroSection.style.setProperty("--common-share", commonShare);
    heroSection.style.setProperty("--slider-progress", ((index / 3) * 100).toFixed(1) + "%");
    if (compressionSlider) {
      compressionSlider.value = String(index);
    }
    if (retentionOutput) {
      retentionOutput.value = retained;
      retentionOutput.textContent = retained;
    }
    if (retentionValue) {
      retentionValue.textContent = retained;
    }
    if (depthLabel) {
      depthLabel.textContent = state.label;
    }
    depthButtons.forEach(function (button) {
      button.classList.toggle("is-active", Number(button.getAttribute("data-depth")) === index);
    });
  }

  if (compressionSlider) {
    compressionSlider.addEventListener("input", function (event) {
      updateCompression(event.target.value);
    });
  }

  depthButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      updateCompression(button.getAttribute("data-depth"));
    });
  });

  updateCompression(0);

  taxonomyTriggers.forEach(function (trigger) {
    trigger.addEventListener("click", function () {
      var detail = document.getElementById(trigger.getAttribute("aria-controls"));
      var isOpen = trigger.getAttribute("aria-expanded") === "true";
      trigger.setAttribute("aria-expanded", String(!isOpen));
      if (detail) {
        detail.hidden = isOpen;
      }
    });
  });
})();
