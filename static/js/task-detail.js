(function () {
  var root = document.querySelector("#task-detail-root");
  var titleElement = document.querySelector("#task-detail-title");

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

  function param(name) {
    return new URLSearchParams(window.location.search).get(name);
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

  function findTask(baseData, detailData, id, variantType) {
    var base = (baseData.tasks || []).filter(function (task) {
      return task.id === id;
    })[0];
    var detail = (detailData.tasks || []).filter(function (task) {
      return task.id === id;
    })[0];
    if (!base && !detail) {
      return null;
    }
    var metadata = (detail && detail.metadata) || {};
    var variants = (base && base.variants) || [];
    var selectedVariant = variants.filter(function (variant) {
      return variant.type === variantType;
    })[0] || variants[0] || null;
    return {
      id: id,
      domain: (base && base.domain) || (detail && detail.domain) || "",
      variants: variants,
      selectedVariant: selectedVariant,
      selectedVariantType: selectedVariant ? selectedVariant.type : "",
      detail: detail || {},
      metadata: metadata,
      name: metadata.name || slugLabel(id),
      difficulty: metadata.difficulty || "",
      category: metadata.category || ((base && base.domain) || ""),
      tags: toArray(metadata.tags),
      instruction: (detail && detail.instruction) || "",
      instructionAvailable: detail && detail.instruction_available === true,
      sourceUrl: (detail && detail.source_url) || "",
      version: (detail && detail.version) || "",
      verifier: (detail && detail.verifier) || {}
    };
  }

  function renderTags(tags) {
    return (tags || []).map(function (tag) {
      return "<span class=\"registry-tag\">#" + escapeHtml(tag) + "</span>";
    }).join("");
  }

  function renderMeta(task) {
    var parts = [];
    if (task.version) {
      parts.push("v" + task.version);
    }
    if (task.category) {
      parts.push(slugLabel(task.category));
    }
    if (task.difficulty) {
      parts.push(slugLabel(task.difficulty));
    }
    if (task.metadata.author_name) {
      parts.push(task.metadata.author_name);
    }
    return parts.map(function (part) {
      return "<span>" + escapeHtml(part) + "</span>";
    }).join("");
  }

  function renderVariants(task) {
    if (!task.variants.length) {
      return "<p class=\"empty-state\">No TailSkills variant metadata is available for this task.</p>";
    }
    return "<div class=\"detail-variant-list\">" + task.variants.map(function (variant) {
      var isActive = task.selectedVariantType === variant.type;
      var href = "task.html?id=" + encodeURIComponent(task.id) + "&variant=" + encodeURIComponent(variant.type || "");
      return "<article class=\"detail-variant" + (isActive ? " is-active" : "") + "\">" +
        "<a href=\"" + href + "\">" +
          "<strong>" + escapeHtml(variant.variant_name || variant.type) + "</strong>" +
          "<span>" + escapeHtml(variant.category_name || variant.category) + " / " + escapeHtml(variant.fragility || "unknown") + " fragility</span>" +
        "</a>" +
      "</article>";
    }).join("") + "</div>";
  }

  function renderSelectedVariant(task) {
    if (!task.selectedVariant) {
      return "";
    }
    var variant = task.selectedVariant;
    return "<section class=\"variant-context\" aria-label=\"Selected TailSkills variant\">" +
      "<div>" +
        "<span class=\"section-kicker\">Selected Variant</span>" +
        "<h2>" + escapeHtml(variant.variant_name || variant.type) + "</h2>" +
        "<p>" + escapeHtml(task.id + " / " + (variant.type || "variant")) + "</p>" +
      "</div>" +
      "<dl class=\"detail-definition-list\">" +
        "<div><dt>Category</dt><dd>" + escapeHtml(variant.category_name || variant.category || "not listed") + "</dd></div>" +
        "<div><dt>Variant code</dt><dd>" + escapeHtml(variant.type || "not listed") + "</dd></div>" +
        "<div><dt>Fragility</dt><dd>" + escapeHtml(variant.fragility || "unknown") + "</dd></div>" +
      "</dl>" +
    "</section>";
  }

  function renderInstruction(task) {
    if (!task.instructionAvailable || !task.instruction) {
      return "<p class=\"empty-state\">Detailed task statement is not included in the current public TailSkills data for this task. No synthetic instruction was generated.</p>";
    }
    return "<pre class=\"instruction-block\"><code>" + escapeHtml(task.instruction) + "</code></pre>";
  }

  function renderVerifier(task) {
    var sourceLink = task.sourceUrl ? task.sourceUrl + "/tests/test_outputs.py" : "";
    return "<div class=\"detail-note\">" +
      "<p>The verifier is part of the original SkillsBench task package. TailSkills keeps the agent-visible instruction fixed and injects tail conditions in the task environment.</p>" +
      "<dl class=\"detail-definition-list\">" +
        "<div><dt>Verifier timeout</dt><dd>" + escapeHtml(task.verifier.timeout_sec || "not listed") + " seconds</dd></div>" +
        "<div><dt>Verifier path</dt><dd>" + escapeHtml(task.verifier.source_path || "not available") + "</dd></div>" +
      "</dl>" +
      (sourceLink ? "<a class=\"section-link\" href=\"" + escapeHtml(sourceLink) + "\">Open verifier source -&gt;</a>" : "") +
    "</div>";
  }

  function renderUnavailable(kind) {
    return "<p class=\"empty-state\">" + kind + " data is not included in this static website release. The page intentionally avoids fabricating per-task evidence.</p>";
  }

  function activateTab(targetId) {
    root.querySelectorAll("[role=\"tab\"]").forEach(function (tab) {
      var selected = tab.getAttribute("aria-controls") === targetId;
      tab.setAttribute("aria-selected", String(selected));
      tab.classList.toggle("is-active", selected);
    });
    root.querySelectorAll("[role=\"tabpanel\"]").forEach(function (panel) {
      panel.hidden = panel.id !== targetId;
    });
  }

  function renderTask(task) {
    if (titleElement) {
      titleElement.textContent = task.id;
    }
    var source = task.sourceUrl ? "<a class=\"button-link button-link--secondary\" href=\"" + escapeHtml(task.sourceUrl) + "\">Source</a>" : "";
    root.innerHTML = "<p class=\"section-kicker\">Task Detail</p>" +
      "<h1 id=\"task-detail-title\" class=\"page-title\">" + escapeHtml(task.id) + "</h1>" +
      "<p class=\"task-detail-name\">" + escapeHtml(task.name) + "</p>" +
      "<div class=\"task-detail-meta\">" + renderMeta(task) + "</div>" +
      "<div class=\"registry-tags task-detail-tags\">" + renderTags(task.tags) + "</div>" +
      "<div class=\"task-detail-actions\"><a class=\"button-link\" href=\"tasks.html\">Back to Registry</a>" + source + "</div>" +
      "<p class=\"task-detail-summary\">" + escapeHtml(task.instructionAvailable ? task.instruction.replace(/\s+/g, " ").slice(0, 340) + (task.instruction.length > 340 ? "..." : "") : "Detailed task statement is not available for this task in the current public data.") + "</p>" +
      renderSelectedVariant(task) +
      renderVariants(task) +
      "<div class=\"detail-tabs\" role=\"tablist\" aria-label=\"Task detail tabs\">" +
        "<button type=\"button\" class=\"detail-tab is-active\" role=\"tab\" aria-selected=\"true\" aria-controls=\"detail-instruction\">Instruction</button>" +
        "<button type=\"button\" class=\"detail-tab\" role=\"tab\" aria-selected=\"false\" aria-controls=\"detail-verifier\">Verifier</button>" +
        "<button type=\"button\" class=\"detail-tab\" role=\"tab\" aria-selected=\"false\" aria-controls=\"detail-trajectory\">Trajectory</button>" +
      "</div>" +
      "<section id=\"detail-instruction\" class=\"detail-panel\" role=\"tabpanel\">" + renderInstruction(task) + "</section>" +
      "<section id=\"detail-verifier\" class=\"detail-panel\" role=\"tabpanel\" hidden>" + renderVerifier(task) + "</section>" +
      "<section id=\"detail-trajectory\" class=\"detail-panel\" role=\"tabpanel\" hidden>" + renderUnavailable("Execution trajectory") + "</section>";

    root.querySelectorAll("[role=\"tab\"]").forEach(function (tab) {
      tab.addEventListener("click", function () {
        activateTab(tab.getAttribute("aria-controls"));
      });
    });
  }

  function renderMissing(id) {
    root.innerHTML = "<p class=\"section-kicker\">Task Detail</p><h1 id=\"task-detail-title\" class=\"page-title\">Task not found</h1><p class=\"empty-state\">No task matched <code>" + escapeHtml(id || "") + "</code>.</p><a class=\"button-link\" href=\"tasks.html\">Back to Registry</a>";
  }

  function loadTask() {
    var id = param("id");
    var variantType = param("variant");
    if (!root || !id) {
      renderMissing(id);
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
      var task = findTask(results[0], results[1], id, variantType);
      if (!task) {
        renderMissing(id);
      } else {
        renderTask(task);
      }
    }).catch(function () {
      root.innerHTML = "<p class=\"section-kicker\">Task Detail</p><h1 class=\"page-title\">Task data unavailable</h1><p class=\"empty-state\">Use a local HTTP server or GitHub Pages to view task details.</p>";
    });
  }

  loadTask();
})();
