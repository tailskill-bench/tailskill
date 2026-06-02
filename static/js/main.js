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
  var chartInstances = [];

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

  function chartColors() {
    return {
      tail: getCssVar("--accent-tail"),
      common: getCssVar("--accent-common"),
      highlight: getCssVar("--accent-highlight"),
      text: getCssVar("--text-secondary"),
      grid: getCssVar("--border"),
      neutral: getCssVar("--chart-neutral"),
      a: getCssVar("--category-a"),
      b: getCssVar("--category-b"),
      c: getCssVar("--category-c"),
      d: getCssVar("--category-d"),
      e: getCssVar("--category-e"),
      g: getCssVar("--category-g")
    };
  }

  function baseChartOptions(colors) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: "index"
      },
      plugins: {
        legend: {
          labels: {
            color: colors.text,
            usePointStyle: true,
            boxWidth: 8
          }
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return context.dataset.label + ": " + context.parsed.y.toFixed(1) + "%";
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: colorWithAlpha(colors.grid, 0.45) },
          ticks: { color: colors.text }
        },
        y: {
          min: 0,
          max: 100,
          grid: { color: colorWithAlpha(colors.grid, 0.45) },
          ticks: {
            color: colors.text,
            callback: function (value) {
              return value + "%";
            }
          }
        }
      }
    };
  }

  function destroyCharts() {
    chartInstances.forEach(function (chart) {
      chart.destroy();
    });
    chartInstances = [];
  }

  function initCharts() {
    if (!window.Chart) {
      return;
    }
    destroyCharts();
    var colors = chartColors();
    var labels = ["S1 (8K)", "S2 (5.6K)", "S3 (3.9K)", "S4 (2.7K)"];
    var overallCanvas = document.getElementById("overall-chart");
    var categoryCanvas = document.getElementById("category-chart");
    var retentionCanvas = document.getElementById("retention-chart");

    if (overallCanvas) {
      chartInstances.push(new Chart(overallCanvas, {
        type: "line",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Common-case",
              data: [50.8, 52.5, 49.2, 49.2],
              borderColor: colors.common,
              backgroundColor: colorWithAlpha(colors.common, 0.18),
              pointBackgroundColor: colors.common,
              borderWidth: 3,
              tension: 0.32,
              fill: true
            },
            {
              label: "Tail-case",
              data: [50.5, 35.4, 23.4, 23.1],
              borderColor: colors.tail,
              backgroundColor: colorWithAlpha(colors.tail, 0.18),
              pointBackgroundColor: colors.tail,
              borderWidth: 3,
              tension: 0.32,
              fill: true
            }
          ]
        },
        options: baseChartOptions(colors)
      }));
    }

    if (categoryCanvas) {
      chartInstances.push(new Chart(categoryCanvas, {
        type: "line",
        data: {
          labels: labels,
          datasets: [
            { label: "A: Encoding", data: [43.5, 26.0, 17.4, 14.3], borderColor: colors.a, backgroundColor: colorWithAlpha(colors.a, 0.12), tension: 0.3, borderWidth: 2, pointBackgroundColor: colors.a },
            { label: "B: File System", data: [51.7, 38.3, 30.9, 28.3], borderColor: colors.b, backgroundColor: colorWithAlpha(colors.b, 0.12), tension: 0.3, borderWidth: 2, pointBackgroundColor: colors.b },
            { label: "C: Data Quality", data: [39.5, 28.2, 17.6, 5.1], borderColor: colors.c, backgroundColor: colorWithAlpha(colors.c, 0.12), tension: 0.3, borderWidth: 2, pointBackgroundColor: colors.c },
            { label: "D: Network", data: [48.4, 34.3, 14.3, 34.3], borderColor: colors.d, backgroundColor: colorWithAlpha(colors.d, 0.12), tension: 0.3, borderWidth: 2, pointBackgroundColor: colors.d },
            { label: "E: Dependency", data: [81.8, 59.1, 40.0, 45.5], borderColor: colors.e, backgroundColor: colorWithAlpha(colors.e, 0.12), tension: 0.3, borderWidth: 2, pointBackgroundColor: colors.e }
          ]
        },
        options: baseChartOptions(colors)
      }));
    }

    if (retentionCanvas) {
      chartInstances.push(new Chart(retentionCanvas, {
        type: "bar",
        data: {
          labels: ["S1", "S2", "S3", "S4"],
          datasets: [
            {
              label: "Total Words Retention",
              data: [100.0, 70.9, 52.9, 45.6],
              backgroundColor: colorWithAlpha(colors.neutral, 0.72),
              borderColor: colors.neutral,
              borderWidth: 1
            },
            {
              label: "Regular Content Retention",
              data: [100.0, 73.5, 56.1, 48.7],
              backgroundColor: colorWithAlpha(colors.common, 0.72),
              borderColor: colors.common,
              borderWidth: 1
            },
            {
              label: "Tail-Logic Retention",
              data: [100.0, 43.5, 22.7, 15.7],
              backgroundColor: colorWithAlpha(colors.tail, 0.72),
              borderColor: colors.tail,
              borderWidth: 1
            }
          ]
        },
        options: baseChartOptions(colors)
      }));
    }
  }

  initCharts();
  document.addEventListener("tailskills:themechange", initCharts);
})();
