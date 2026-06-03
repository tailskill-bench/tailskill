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
})();
