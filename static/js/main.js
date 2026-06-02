(function () {
  var root = document.documentElement;
  var storageKey = "tailskills-theme";
  var navToggle = document.querySelector(".nav-toggle");
  var navLinks = document.querySelector("#nav-links");
  var themeToggle = document.querySelector("[data-theme-toggle]");

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
})();
