(function () {
  var PAGE_SIZE = 24;
  var taskSearch = document.querySelector("#task-search");
  var categoryFilter = document.querySelector("#category-filter");
  var difficultyFilter = document.querySelector("#difficulty-filter");
  var tagFilter = document.querySelector("#tag-filter");
  var taskGrid = document.querySelector("#task-grid");
  var galleryCount = document.querySelector("#gallery-count");
  var loadMoreWrap = document.querySelector("#load-more-wrap");
  var loadMoreBtn = document.querySelector("#load-more-btn");
  var state = {
    variants: [],
    filterCategory: "all",
    filterDifficulty: "all",
    filterTag: "all",
    query: "",
    visibleCount: PAGE_SIZE
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
    return compact.length > 240 ? compact.slice(0, 240).replace(/\s+\S*$/, "") + "..." : compact;
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

    var records = [];
    (baseData.tasks || []).forEach(function (task) {
      var detail = detailsById[task.id] || {};
      var metadata = detail.metadata || {};
      var baseTags = toArray(metadata.tags);
      (task.variants || []).forEach(function (variant) {
        var variantType = variant.type || "";
        var categoryCode = variant.category || "";
        var categoryName = variant.category_name || categoryCode || metadata.category || task.domain;
        records.push({
          variantRecordId: task.id + "--" + variantType,
          baseTaskId: task.id,
          domain: task.domain,
          detail: detail,
          name: metadata.name || slugLabel(task.id),
          category: categoryName,
          categoryCode: categoryCode,
          difficulty: metadata.difficulty || "",
          tags: uniqueSorted(baseTags.concat([categoryCode, variantType]).filter(Boolean)),
          instruction: detail.instruction || "",
          instructionAvailable: detail.instruction_available === true,
          sourceUrl: detail.source_url || "",
          author: metadata.author_name || "",
          version: detail.version || "",
          variant: variant,
          variantType: variantType,
          variantName: variant.variant_name || slugLabel(variantType),
          fragility: variant.fragility || "unknown"
        });
      });
    });
    return records;
  }

  function setupFilters() {
    populateSelect(categoryFilter, uniqueSorted(state.variants.map(function (record) {
      return record.category;
    })), slugLabel);
    populateSelect(difficultyFilter, uniqueSorted(state.variants.map(function (record) {
      return record.difficulty;
    })), slugLabel);
    var tags = [];
    state.variants.forEach(function (record) {
      tags = tags.concat(record.tags || []);
    });
    populateSelect(tagFilter, uniqueSorted(tags), function (tag) {
      return "#" + tag;
    });
  }

  function variantMatches(record) {
    var query = normalize(state.query);
    if (state.filterCategory !== "all" && record.category !== state.filterCategory) {
      return false;
    }
    if (state.filterDifficulty !== "all" && record.difficulty !== state.filterDifficulty) {
      return false;
    }
    if (state.filterTag !== "all" && (record.tags || []).indexOf(state.filterTag) === -1) {
      return false;
    }
    if (!query) {
      return true;
    }
    var haystack = [
      record.variantRecordId,
      record.baseTaskId,
      record.variantType,
      record.variantName,
      record.fragility,
      record.name,
      record.domain,
      record.category,
      record.categoryCode,
      record.difficulty,
      (record.tags || []).join(" "),
      record.instruction
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

  function renderTask(record) {
    var href = "task.html?id=" + encodeURIComponent(record.baseTaskId) + "&variant=" + encodeURIComponent(record.variantType);
    var difficulty = record.difficulty ? "<span class=\"difficulty-pill difficulty-pill--" + escapeHtml(record.difficulty) + "\">" + escapeHtml(slugLabel(record.difficulty)) + "</span>" : "";
    var source = record.sourceUrl ? "<a class=\"registry-source\" href=\"" + escapeHtml(record.sourceUrl) + "\" aria-label=\"Open source for " + escapeHtml(record.baseTaskId) + "\">Source</a>" : "<span class=\"registry-source registry-source--muted\">Source unavailable</span>";
    return "<article class=\"task-registry-card\">" +
      "<a class=\"task-registry-card__main\" href=\"" + href + "\">" +
        "<div class=\"registry-card-topline\">" +
          "<span class=\"category-pill\">" + escapeHtml(slugLabel(record.category)) + "</span>" +
          difficulty +
        "</div>" +
        "<h3>" + escapeHtml(record.variantName) + "</h3>" +
        "<p class=\"task-card-name\">" + escapeHtml(record.baseTaskId + " / " + record.variantType) + "</p>" +
        "<p class=\"task-card-preview\">" + escapeHtml(firstSentence(record.instruction)) + "</p>" +
      "</a>" +
      "<div class=\"task-card-footer\">" +
        "<div class=\"registry-tags\">" + renderTags(record.tags) + "</div>" +
        "<div class=\"registry-card-meta\"><span>" + escapeHtml(record.categoryCode || "variant") + " / " + escapeHtml(record.fragility) + " fragility</span>" + source + "</div>" +
      "</div>" +
    "</article>";
  }

  function countBaseTasks(records) {
    var seen = {};
    records.forEach(function (record) {
      seen[record.baseTaskId] = true;
    });
    return Object.keys(seen).length;
  }

  function renderGallery() {
    if (!taskGrid || !galleryCount) {
      return;
    }
    var visible = state.variants.filter(variantMatches);
    var shown = visible.slice(0, state.visibleCount);
    var availableBaseInstructions = countBaseTasks(state.variants.filter(function (record) {
      return record.instructionAvailable;
    }));
    galleryCount.textContent = "Showing " + shown.length + " of " + visible.length + " variants across " + countBaseTasks(visible) + " base tasks. " + availableBaseInstructions + " base tasks include source-backed instructions.";
    taskGrid.innerHTML = shown.map(renderTask).join("");

    if (loadMoreWrap) {
      if (shown.length < visible.length) {
        loadMoreWrap.style.display = "block";
        loadMoreBtn.textContent = "Load more (" + (visible.length - shown.length) + " remaining)";
      } else {
        loadMoreWrap.style.display = "none";
      }
    }
  }

  function resetPagination() {
    state.visibleCount = PAGE_SIZE;
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
      state.variants = mergeTasks(results[0], results[1]);
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
      resetPagination();
      renderGallery();
    });
  }

  if (categoryFilter) {
    categoryFilter.addEventListener("change", function (event) {
      state.filterCategory = event.target.value;
      resetPagination();
      renderGallery();
    });
  }

  if (difficultyFilter) {
    difficultyFilter.addEventListener("change", function (event) {
      state.filterDifficulty = event.target.value;
      resetPagination();
      renderGallery();
    });
  }

  if (tagFilter) {
    tagFilter.addEventListener("change", function (event) {
      state.filterTag = event.target.value;
      resetPagination();
      renderGallery();
    });
  }

  if (loadMoreBtn) {
    loadMoreBtn.addEventListener("click", function () {
      state.visibleCount += PAGE_SIZE;
      renderGallery();
    });
  }

  loadTasks();
})();
