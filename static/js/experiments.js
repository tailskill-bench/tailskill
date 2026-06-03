(function () {
  var chartInstances = [];

  function getCssVar(name) {
    return window.TailSkills.getCssVar(name);
  }

  function colorWithAlpha(color, alpha) {
    return window.TailSkills.colorWithAlpha(color, alpha);
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
    var overallCanvas = document.getElementById("overall-chart");
    var categoryCanvas = document.getElementById("category-chart");
    var retentionCanvas = document.getElementById("retention-chart");
    if (!overallCanvas && !categoryCanvas && !retentionCanvas) {
      return;
    }
    destroyCharts();
    var colors = chartColors();
    var labels = ["S1 (8K)", "S2 (5.6K)", "S3 (3.9K)", "S4 (2.7K)"];

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

  window.TailSkills = window.TailSkills || {};
  window.TailSkills.initCharts = initCharts;

  initCharts();
  document.addEventListener("tailskills:themechange", initCharts);
})();
