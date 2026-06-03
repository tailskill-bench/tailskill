(function () {
  var heroSection = document.querySelector("#hero");
  var compressionSlider = document.querySelector("#compression-slider");
  var retentionOutput = document.querySelector("#retention-output");
  var retentionValue = document.querySelector("[data-retention-value]");
  var depthLabel = document.querySelector("[data-depth-label]");
  var depthButtons = document.querySelectorAll("[data-depth]");
  var copyButton = document.querySelector("[data-copy-bibtex]");
  var copyStatus = document.querySelector("[data-copy-status]");
  var bibtexCode = document.querySelector("#bibtex-code");
  var counters = document.querySelectorAll("[data-counter]");
  var autopsyContainer = document.querySelector(".autopsy-scroll-container");
  var tailTexts = document.querySelectorAll(".tail-text");
  var depthIndicators = document.querySelectorAll(".depth-indicator");
  var retentionLabel = document.querySelector(".autopsy-retention");
  var prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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

  if (copyButton && bibtexCode) {
    copyButton.addEventListener("click", function () {
      window.TailSkills.copyText(bibtexCode.textContent).then(function () {
        if (copyStatus) {
          copyStatus.textContent = "Copied BibTeX to clipboard.";
        }
      }).catch(function () {
        if (copyStatus) {
          copyStatus.textContent = "Copy failed. Select the BibTeX text manually.";
        }
      });
    });
  }

  function animateCounter(element, target, duration, decimals) {
    var start = 0;
    var startTime = null;
    function step(timestamp) {
      if (!startTime) {
        startTime = timestamp;
      }
      var progress = Math.min((timestamp - startTime) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var current = start + (target - start) * eased;
      element.textContent = current.toFixed(decimals);
      if (progress < 1) {
        requestAnimationFrame(step);
      }
    }
    requestAnimationFrame(step);
  }

  function setupCounters() {
    if (!counters.length) {
      return;
    }
    counters.forEach(function (counter) {
      var target = Number(counter.getAttribute("data-target")) || 0;
      var decimals = Number(counter.getAttribute("data-decimals")) || 0;
      var duration = Number(counter.getAttribute("data-duration")) || 500;
      if (prefersReducedMotion || !("IntersectionObserver" in window)) {
        counter.textContent = target.toFixed(decimals);
        counter.setAttribute("data-counted", "true");
      } else {
        counter.textContent = (0).toFixed(decimals);
        var observer = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting && counter.getAttribute("data-counted") !== "true") {
              counter.setAttribute("data-counted", "true");
              animateCounter(counter, target, duration, decimals);
              observer.unobserve(counter);
            }
          });
        }, { threshold: 0.5 });
        observer.observe(counter);
      }
    });
  }

  function setActiveDepth(index) {
    depthIndicators.forEach(function (indicator) {
      indicator.classList.toggle("is-active", Number(indicator.getAttribute("data-depth-stage")) === index);
    });
  }

  function updateAutopsy() {
    if (!autopsyContainer || !tailTexts.length) {
      return;
    }
    var rect = autopsyContainer.getBoundingClientRect();
    var containerHeight = autopsyContainer.offsetHeight - window.innerHeight;
    var scrolled = -rect.top;
    var progress = Math.max(0, Math.min(1, scrolled / Math.max(1, containerHeight)));
    var opacity;
    var blur;
    var strikethrough;
    var retention;

    if (progress < 0.25) {
      opacity = 1;
      blur = 0;
      strikethrough = 0;
      retention = 100;
    } else if (progress < 0.5) {
      var s2 = (progress - 0.25) / 0.25;
      opacity = 1 - 0.4 * s2;
      blur = s2 * 1.5;
      strikethrough = s2;
      retention = 100 - 56.5 * s2;
    } else if (progress < 0.75) {
      var s3 = (progress - 0.5) / 0.25;
      opacity = 0.6 - 0.3 * s3;
      blur = 1.5 + s3 * 1.5;
      strikethrough = 1;
      retention = 43.5 - 20.8 * s3;
    } else {
      var s4 = (progress - 0.75) / 0.25;
      opacity = 0.3 - 0.22 * s4;
      blur = 3 + s4 * 1.5;
      strikethrough = 1;
      retention = 22.7 - 7 * s4;
    }

    var strikeColor = window.TailSkills.colorWithAlpha(window.TailSkills.getCssVar("--accent-tail"), strikethrough);
    autopsyContainer.style.setProperty("--tail-opacity", String(opacity));
    autopsyContainer.style.setProperty("--tail-blur", blur + "px");
    autopsyContainer.style.setProperty("--autopsy-tail-strike", strikeColor);
    if (retentionLabel) {
      retentionLabel.textContent = retention.toFixed(1) + "%";
    }
    setActiveDepth(Math.min(3, Math.floor(progress * 4)));
  }

  function setupAutopsy() {
    if (!autopsyContainer) {
      return;
    }
    if (prefersReducedMotion) {
      autopsyContainer.style.setProperty("--tail-opacity", "1");
      autopsyContainer.style.setProperty("--tail-blur", "0px");
      autopsyContainer.style.setProperty("--autopsy-tail-strike", "transparent");
      if (retentionLabel) {
        retentionLabel.textContent = "100.0%";
      }
      setActiveDepth(0);
      return;
    }
    updateAutopsy();
    window.addEventListener("scroll", updateAutopsy, { passive: true });
    window.addEventListener("resize", updateAutopsy);
  }

  setupCounters();
  setupAutopsy();
})();
