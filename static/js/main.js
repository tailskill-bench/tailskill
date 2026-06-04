(function () {
  var root = document.documentElement;
  var storageKey = "tailskills-theme";
  var navToggle = document.querySelector(".nav-toggle");
  var navLinks = document.querySelector("#nav-links");
  var themeToggle = document.querySelector("[data-theme-toggle]");
  var pageName = document.body ? document.body.getAttribute("data-page") : "";

  function getCssVar(name) {
    return getComputedStyle(root).getPropertyValue(name).trim();
  }

  function colorWithAlpha(color, alpha) {
    if (color.indexOf("rgb") === 0) {
      return color.replace("rgb(", "rgba(").replace(")", ", " + alpha + ")");
    }
    var hex = color.replace("#", "");
    if (hex.length === 3) {
      hex = hex.split("").map(function (part) { return part + part; }).join("");
    }
    var value = parseInt(hex, 16);
    var red = (value >> 16) & 255;
    var green = (value >> 8) & 255;
    var blue = value & 255;
    return "rgba(" + red + ", " + green + ", " + blue + ", " + alpha + ")";
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    var textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.top = "-1000px";
    document.body.appendChild(textarea);
    textarea.select();
    var copied = document.execCommand("copy");
    document.body.removeChild(textarea);
    return copied ? Promise.resolve() : Promise.reject(new Error("Copy failed"));
  }

  function preferredTheme() {
    var saved = window.localStorage.getItem(storageKey);
    if (saved === "light" || saved === "dark") {
      return saved;
    }
    return "light";
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

  window.TailSkills = window.TailSkills || {};
  window.TailSkills.getCssVar = getCssVar;
  window.TailSkills.colorWithAlpha = colorWithAlpha;
  window.TailSkills.copyText = copyText;
  window.TailSkills.applyTheme = applyTheme;

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

  if (navLinks && pageName) {
    navLinks.querySelectorAll(".nav-link").forEach(function (link) {
      var href = link.getAttribute("href") || "";
      var targetPage = "";
      if (href.indexOf("tasks.html") !== -1) {
        targetPage = "tasks";
      } else if (href.indexOf("experiments.html") !== -1) {
        targetPage = "experiments";
      } else if (href.indexOf("index.html") !== -1 || href === "./" || href === "/") {
        targetPage = "home";
      }
      var isCurrent = targetPage === pageName;
      link.classList.toggle("is-current", isCurrent);
      if (isCurrent) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
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

  function revealHashTarget() {
    if (!window.location.hash) {
      return;
    }
    var target = document.querySelector(window.location.hash);
    if (target && target.classList.contains("page-section")) {
      target.classList.add("is-visible");
    }
  }

  revealHashTarget();
  window.addEventListener("hashchange", revealHashTarget);
})();
