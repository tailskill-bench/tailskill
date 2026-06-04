(function () {
  var taskSearch = document.querySelector("#task-search");
  var categoryFilter = document.querySelector("#category-filter");
  var difficultyFilter = document.querySelector("#difficulty-filter");
  var tagFilter = document.querySelector("#tag-filter");
  var taskGrid = document.querySelector("#task-grid");
  var galleryCount = document.querySelector("#gallery-count");
  var state = {
    tasks: [],
    filterCategory: "all",
    filterDifficulty: "all",
    filterTag: "all",
    query: ""
  };

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function slugLabel(value) {
    return String(value || "")
      .replace(/[-_]/g, " ")
      .replace(/\b\w/g, function (letter) {
        return letter.toUpperCase();
      });
  }

  function normalize(value) {
    return String(value || "").trim().toLowerCase();
  }

  function toArray(value) {
    if (Array.isArray(value)) {
      return value;
    }
    if (typeof value === "string" && value) {
      return [value];
    }
    return [];
  }

  function firstSentence(text) {
    var compact = String(text || "").replace(/\s+/g, " ").trim();
    if (!compact) {
      return "Detailed task statement is not included in the current public data release.";
    }
    return compact.length > 260 ? compact.slice(0, 260).replace(/\s+\S*$/, "") + "..." : compact;
  }

  function uniqueSorted(values) {
    var seen = {};
    values.forEach(function (value) {
      if (value) {
        seen[value] = true;
      }
    });
    return Object.keys(seen).sort(function (a, b) {
      return a.localeCompare(b);
    });
  }

  function populateSelect(select, values, formatter) {
    if (!select) {
      return;
    }
    var first = select.querySelector("option");
    select.innerHTML = "";
    if (first) {
      select.appendChild(first);
    }
    values.forEach(function (value) {
      var option = document.createElement("option");
      option.value = value;
      option.textContent = formatter ? formatter(value) : value;
      select.appendChild(option);
    });
  }

  function mergeTasks(baseData, detailData) {
    var detailsById = {};
    (detailData.tasks || []).forEach(function (detail) {
      detailsById[detail.id] = detail;
    });
    return (baseData.tasks || []).map(function (task) {
      var detail = detailsById[task.id] || {};
      var metadata = detail.metadata || {};
      return {
        id: task.id,
        domain: task.domain,
        variants: task.variants || [],
        detail: detail,
        name: metadata.name || slugLabel(task.id),
        category: metadata.category || task.domain,
        difficulty: metadata.difficulty || "",
        tags: toArray(metadata.tags),
        instruction: detail.instruction || "",
        instructionAvailable: detail.instruction_available === true,
        sourceUrl: detail.source_url || "",
        author: metadata.author_name || "",
        version: detail.version || ""
      };
    });
  }

  function setupFilters() {
    populateSelect(categoryFilter, uniqueSorted(state.tasks.map(function (task) {
      return task.category || task.domain;
    })), slugLabel);
    populateSelect(difficultyFilter, uniqueSorted(state.tasks.map(function (task) {
      return task.difficulty;
    })), slugLabel);
    var tags = [];
    state.tasks.forEach(function (task) {
      tags = tags.concat(task.tags || []);
    });
    populateSelect(tagFilter, uniqueSorted(tags), function (tag) {
      return "#" + tag;
    });
  }

  function taskMatches(task) {
    var query = normalize(state.query);
    var category = task.category || task.domain;
    if (state.filterCategory !== "all" && category !== state.filterCategory) {
      return false;
    }
    if (state.filterDifficulty !== "all" && task.difficulty !== state.filterDifficulty) {
      return false;
    }
    if (state.filterTag !== "all" && (task.tags || []).indexOf(state.filterTag) === -1) {
      return false;
    }
    if (!query) {
      return true;
    }
    var variantText = (task.variants || []).map(function (variant) {
      return [variant.type, variant.category_name, variant.variant_name, variant.fragility].join(" ");
    }).join(" ");
    var haystack = [
      task.id,
      task.name,
      task.domain,
      task.category,
      task.difficulty,
      (task.tags || []).join(" "),
      task.instruction,
      variantText
    ].join(" ").toLowerCase();
    return haystack.indexOf(query) !== -1;
  }

  function renderTags(tags) {
    var visible = (tags || []).slice(0, 3);
    var html = visible.map(function (tag) {
      return "<span class=\"registry-tag\">#" + escapeHtml(tag) + "</span>";
    }).join("");
    if ((tags || []).length > visible.length) {
      html += "<span class=\"registry-tag registry-tag--muted\">+" + ((tags || []).length - visible.length) + "</span>";
    }
    return html || "<span class=\"registry-tag registry-tag--muted\">metadata</span>";
  }

  function variantSummary(task) {
    var variants = task.variants || [];
    var families = uniqueSorted(variants.map(function (variant) {
      return variant.category_name;
    }));
    return variants.length + " TailSkills variant" + (variants.length === 1 ? "" : "s") + " across " + families.length + " exception family" + (families.length === 1 ? "" : "ies");
  }

  function renderTask(task) {
    var href = "task.html?id=" + encodeURIComponent(task.id);
    var difficulty = task.difficulty ? "<span class=\"difficulty-pill difficulty-pill--" + escapeHtml(task.difficulty) + "\">" + escapeHtml(slugLabel(task.difficulty)) + "</span>" : "";
    var source = task.sourceUrl ? "<a class=\"registry-source\" href=\"" + escapeHtml(task.sourceUrl) + "\" aria-label=\"Open source for " + escapeHtml(task.id) + "\">Source</a>" : "<span class=\"registry-source registry-source--muted\">Source unavailable</span>";
    return "<article class=\"task-registry-card\">" +
      "<a class=\"task-registry-card__main\" href=\"" + href + "\">" +
        "<div class=\"registry-card-topline\">" +
          "<span class=\"category-pill\">" + escapeHtml(slugLabel(task.category || task.domain)) + "</span>" +
          difficulty +
        "</div>" +
        "<h3>" + escapeHtml(task.id) + "</h3>" +
        "<p class=\"task-card-name\">" + escapeHtml(task.name) + "</p>" +
        "<p class=\"task-card-preview\">" + escapeHtml(firstSentence(task.instruction)) + "</p>" +
      "</a>" +
      "<div class=\"task-card-footer\">" +
        "<div class=\"registry-tags\">" + renderTags(task.tags) + "</div>" +
        "<div class=\"registry-card-meta\"><span>" + escapeHtml(variantSummary(task)) + "</span>" + source + "</div>" +
      "</div>" +
    "</article>";
  }

  function renderGallery() {
    if (!taskGrid || !galleryCount) {
      return;
    }
    var visible = state.tasks.filter(taskMatches);
    var visibleVariants = visible.reduce(function (sum, task) {
      return sum + (task.variants || []).length;
    }, 0);
    var totalVariants = state.tasks.reduce(function (sum, task) {
      return sum + (task.variants || []).length;
    }, 0);
    var availableInstructions = state.tasks.filter(function (task) {
      return task.instructionAvailable;
    }).length;
    galleryCount.textContent = "Showing " + visible.length + " of " + state.tasks.length + " tasks (" + visibleVariants + " of " + totalVariants + " variants). " + availableInstructions + " tasks include source-backed instructions.";
    taskGrid.innerHTML = visible.map(renderTask).join("");
  }

  function loadTasks() {
    if (!taskGrid) {
      return;
    }
    Promise.all([
      fetch("data/tasks.json").then(function (response) {
        if (!response.ok) {
          throw new Error("Task variant data unavailable");
        }
        return response.json();
      }),
      fetch("data/task-details.json").then(function (response) {
        if (!response.ok) {
          throw new Error("Task detail data unavailable");
        }
        return response.json();
      })
    ]).then(function (results) {
      state.tasks = mergeTasks(results[0], results[1]);
      setupFilters();
      renderGallery();
    }).catch(function () {
      if (galleryCount) {
        galleryCount.textContent = "Task data could not be loaded. Use a local HTTP server or GitHub Pages to view the registry.";
      }
    });
  }

  if (taskSearch) {
    taskSearch.addEventListener("input", function (event) {
      state.query = event.target.value;
      renderGallery();
    });
  }

  if (categoryFilter) {
    categoryFilter.addEventListener("change", function (event) {
      state.filterCategory = event.target.value;
      renderGallery();
    });
  }

  if (difficultyFilter) {
    difficultyFilter.addEventListener("change", function (event) {
      state.filterDifficulty = event.target.value;
      renderGallery();
    });
  }

  if (tagFilter) {
    tagFilter.addEventListener("change", function (event) {
      state.filterTag = event.target.value;
      renderGallery();
    });
  }

  loadTasks();
})();
