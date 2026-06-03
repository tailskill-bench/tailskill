(function () {
  var taxonomyTriggers = document.querySelectorAll(".taxonomy-trigger");
  var taskSearch = document.querySelector("#task-search");
  var filterButtons = document.querySelectorAll("[data-filter]");
  var taskGrid = document.querySelector("#task-grid");
  var galleryCount = document.querySelector("#gallery-count");
  var taskState = {
    tasks: [],
    filter: "all",
    query: ""
  };

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

  function categoryClass(category) {
    return "category-" + String(category || "").toLowerCase();
  }

  function resultLabel(generation, value) {
    var passed = Number(value) >= 1;
    return "<span class=\"result-pill " + (passed ? "result-pill--pass" : "result-pill--fail") + "\">" + generation.toUpperCase() + " " + (passed ? "PASS" : "FAIL") + "</span>";
  }

  function taskMatches(task) {
    var query = taskState.query.trim().toLowerCase();
    var variants = task.variants || [];
    var categoryMatch = taskState.filter === "all" || variants.some(function (variant) {
      return variant.category === taskState.filter;
    });
    if (!categoryMatch) {
      return false;
    }
    if (!query) {
      return true;
    }
    var haystack = [
      task.id,
      task.domain
    ].concat(variants.map(function (variant) {
      return [variant.type, variant.category_name, variant.variant_name, variant.fragility].join(" ");
    })).join(" ").toLowerCase();
    return haystack.indexOf(query) !== -1;
  }

  function renderTask(task) {
    var variants = task.variants || [];
    var primaryCategory = variants[0] ? variants[0].category : "";
    var s4Passes = variants.filter(function (variant) {
      return Number(variant.results && variant.results.s4) >= 1;
    }).length;
    var tags = variants.map(function (variant) {
      return "<span class=\"variant-tag " + categoryClass(variant.category) + "\">" + variant.type.replace(/_/g, " ") + "</span>";
    }).join("");
    var detail = variants.map(function (variant) {
      var results = variant.results || {};
      return "<div class=\"variant-result\"><strong>" + variant.variant_name + "</strong><span>" + variant.category_name + " / " + variant.fragility + " fragility</span><div class=\"result-strip\">" +
        resultLabel("s1", results.s1) +
        resultLabel("s2", results.s2) +
        resultLabel("s3", results.s3) +
        resultLabel("s4", results.s4) +
        "</div></div>";
    }).join("");
    return "<article class=\"task-card " + categoryClass(primaryCategory) + "\"><button type=\"button\" class=\"task-card__button\" aria-expanded=\"false\"><span class=\"task-card__title\">" + task.id + "</span><span class=\"variant-tags\">" + tags + "</span><span class=\"task-card__meta\"><span>Domain: " + task.domain + "</span><span>Base task: oracle verified / Variants passing at S4: " + s4Passes + "/" + variants.length + "</span></span></button><div class=\"task-detail\" hidden>" + detail + "</div></article>";
  }

  function renderGallery() {
    if (!taskGrid || !galleryCount) {
      return;
    }
    var visible = taskState.tasks.filter(taskMatches);
    galleryCount.textContent = visible.length + " sample tasks shown from placeholder data";
    taskGrid.innerHTML = visible.map(renderTask).join("");
    taskGrid.querySelectorAll(".task-card__button").forEach(function (button) {
      button.addEventListener("click", function () {
        var detail = button.parentElement.querySelector(".task-detail");
        var isOpen = button.getAttribute("aria-expanded") === "true";
        button.setAttribute("aria-expanded", String(!isOpen));
        if (detail) {
          detail.hidden = isOpen;
        }
      });
    });
  }

  function loadTasks() {
    if (!taskGrid) {
      return;
    }
    fetch("data/tasks.json")
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Task data unavailable");
        }
        return response.json();
      })
      .then(function (data) {
        taskState.tasks = data.tasks || [];
        renderGallery();
      })
      .catch(function () {
        if (galleryCount) {
          galleryCount.textContent = "Task data could not be loaded. Use a local HTTP server or GitHub Pages to view the gallery.";
        }
      });
  }

  if (taskSearch) {
    taskSearch.addEventListener("input", function (event) {
      taskState.query = event.target.value;
      renderGallery();
    });
  }

  filterButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      taskState.filter = button.getAttribute("data-filter") || "all";
      filterButtons.forEach(function (candidate) {
        candidate.classList.toggle("is-active", candidate === button);
      });
      renderGallery();
    });
  });

  loadTasks();
})();
