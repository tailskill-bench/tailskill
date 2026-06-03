# TailSkills 网页优化 — 第三轮迭代需求 (v3)

> 本文档是 Codex 第三轮迭代的完整需求。请先完整阅读本文档，再阅读现有代码。

## 0. 项目信息

- **项目路径**: `D:\codes\tailskill\`
- **分支**: `gh-pages`（不要切换分支）
- **线上**: https://tailskill-bench.github.io/tailskill/
- **技术栈**: 纯 HTML5 + CSS3 + vanilla JavaScript，无框架无 npm
- **字体**: Instrument Serif + DM Sans + JetBrains Mono（已加载）
- **Chart.js**: 4.4.6 CDN（仅在 experiments.html 加载）
- **颜色**: `--accent-tail: #e2abb8` (tailpink), `--accent-common: #b2d9b3` (commongreen)

## 1. 本轮核心目标

修复 v2 的 6 个问题：

1. **首页无任何论文图片** → 添加 3 张论文图预览，点击跳转详情页
2. **Skill Autopsy 滚动不动声色** → 3 层视觉强化（入口 overlay + 顶部进度条 + 内容层增强）
3. **Explore 导航卡片被埋在底部** → 添加数量 badge 和 mini 预览
4. **benchmark-pipeline.png 未使用** → 放到首页 Figure Preview Gallery
5. **首页与子页面无内容衔接** → 首页添加 mini collapse chart + figure gallery
6. **Tasks 只有 8 个 placeholder** → 准备好接收 208 任务的结构（UI 改造优先，数据后续填）

## 2. 首页重构（index.html）

### 2.1 首页 5 屏布局

首页应该是论文的 **movie trailer**——每屏一个钩子，让访客产生"想看更多"的欲望。

```
Screen 1: HERO (保留，不改)
  └─ 压缩滑块 + "but Fragile" 淡出 → 已有

Screen 2: CORE FINDINGS (增强)
  └─ 3 个 stat cards (保留)
  └─ 新增: mini collapse chart 预览
  └─ 新增: "View full results →" 链接到 experiments.html

Screen 3: FIGURE PREVIEW GALLERY (全新 section)
  └─ 3 张论文图并排展示
  └─ 点击跳转到 experiments.html 对应锚点

Screen 4: SKILL AUTOPSY (增强，详见 2.2)
  └─ 保留 300vh sticky scroll
  └─ 3 层视觉强化

Screen 5: EXPLORE + BIBTEX (增强)
  └─ 3 张导航卡片 (增强 badge)
  └─ BibTeX (保留)
```

### 2.2 Screen 2: Core Findings 增强

在现有 `#core-findings` section 的 `finding-stat-grid` 之后，添加一个 **mini collapse chart**：

```html
<!-- Mini chart preview -->
<div class="mini-chart-preview">
  <div class="chart-wrap" style="height: 12rem;">
    <canvas id="mini-collapse-chart" aria-label="Preview: tail-case pass rate collapse curve" role="img"></canvas>
  </div>
  <a class="chart-link" href="experiments.html#main-results">
    View full interactive results <span aria-hidden="true">&rarr;</span>
  </a>
</div>
```

**CSS 规格**:
```css
.mini-chart-preview {
  max-width: 560px;
  margin: 2rem auto 0;
  padding: 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.chart-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.75rem;
  font-family: var(--font-code);
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--accent-highlight);
  text-decoration: none;
  transition: gap 0.2s ease;
}

.chart-link:hover {
  gap: 0.65rem;
}
```

**JS (home.js)**:
- 只在首页加载 Chart.js（动态 import，懒加载）
- 画一个简单的 2-dataset 折线图（common-case 和 tail-case）
- 数据和 experiments.js 中 `overall-chart` 完全一致
- 不需要交互式 tooltip（mini chart 是静态预览）
- 如果加载 Chart.js 失败（CDN 问题），静默隐藏 mini chart 区域

```javascript
// home.js 中添加（在现有 setupCounters 之后）
function setupMiniChart() {
  var canvas = document.getElementById("mini-collapse-chart");
  if (!canvas) return;

  var script = document.createElement("script");
  script.src = "https://cdn.jsdelivr.net/npm/chart.js@4.4.6/dist/chart.umd.min.js";
  script.onload = function () {
    var colors = {
      tail: window.TailSkills.getCssVar("--accent-tail"),
      common: window.TailSkills.getCssVar("--accent-common"),
      text: window.TailSkills.getCssVar("--text-secondary"),
      grid: window.TailSkills.getCssVar("--border")
    };
    new Chart(canvas, {
      type: "line",
      data: {
        labels: ["S1 (8K)", "S2 (5.6K)", "S3 (3.9K)", "S4 (2.7K)"],
        datasets: [
          {
            label: "Common-case",
            data: [50.8, 52.5, 49.2, 49.2],
            borderColor: colors.common,
            backgroundColor: "transparent",
            borderWidth: 2.5,
            tension: 0.3,
            pointRadius: 3,
            pointBackgroundColor: colors.common
          },
          {
            label: "Tail-case",
            data: [50.5, 35.4, 23.4, 23.1],
            borderColor: colors.tail,
            backgroundColor: "transparent",
            borderWidth: 2.5,
            tension: 0.3,
            pointRadius: 3,
            pointBackgroundColor: colors.tail
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: colors.text, usePointStyle: true, boxWidth: 6, font: { size: 11 } }
          },
          tooltip: { enabled: false }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: colors.text, font: { size: 10 } }
          },
          y: {
            min: 0,
            max: 70,
            grid: { color: colors.grid + "44" },
            ticks: {
              color: colors.text,
              font: { size: 10 },
              callback: function(v) { return v + "%"; }
            }
          }
        }
      }
    });
  };
  document.head.appendChild(script);
}
setupMiniChart();
```

### 2.3 Screen 3: Figure Preview Gallery（全新 section）

在 `#core-findings` 和 `#skill-autopsy` 之间插入新 section：

```html
<section class="page-section" id="figure-preview" aria-labelledby="preview-title">
  <div class="section-inner">
    <p class="section-kicker">Paper Figures</p>
    <h2 id="preview-title">Key visuals at a glance</h2>
    <p class="page-subtitle">Click any figure to view the full version with interactive analysis.</p>
    <div class="preview-grid">
      <a class="preview-card" href="experiments.html#introduction">
        <div class="preview-frame">
          <img src="static/images/introduction-infographic.png"
               alt="Skill distillation conveyor belt infographic"
               width="500" height="642" loading="lazy" decoding="async">
        </div>
        <span class="preview-label">Skill Distillation Pipeline</span>
      </a>
      <a class="preview-card" href="experiments.html#main-results">
        <div class="preview-frame">
          <img src="static/images/benchmark-pipeline.png"
               alt="TailSkills benchmark construction pipeline"
               width="500" height="400" loading="lazy" decoding="async">
        </div>
        <span class="preview-label">Benchmark Construction</span>
      </a>
      <a class="preview-card" href="experiments.html#distillation-example">
        <div class="preview-frame">
          <img src="static/images/distillation-example.png"
               alt="S1 to S4 skill text with tail knowledge disappearing"
               width="500" height="224" loading="lazy" decoding="async">
        </div>
        <span class="preview-label">What Gets Erased</span>
      </a>
    </div>
  </div>
</section>
```

**CSS 规格**:
```css
.preview-grid {
  display: grid;
  gap: 1rem;
  margin-top: 2rem;
}

.preview-card {
  display: grid;
  gap: 0.65rem;
  padding: 0.75rem;
  color: var(--text-primary);
  text-decoration: none;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: 0 12px 32px var(--shadow-color);
  transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.preview-card:hover,
.preview-card:focus-visible {
  transform: translateY(-4px);
  border-color: var(--accent-highlight);
  box-shadow: 0 20px 50px var(--shadow-color);
}

.preview-frame {
  overflow: hidden;
  border-radius: calc(var(--radius) - 2px);
  background: var(--bg-tertiary);
}

.preview-frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  aspect-ratio: 5 / 3;
  transition: transform 0.4s ease;
}

.preview-card:hover .preview-frame img {
  transform: scale(1.04);
}

.preview-label {
  padding: 0 0.25rem;
  font-family: var(--font-code);
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.preview-card:hover .preview-label {
  color: var(--accent-highlight);
}

@media (min-width: 900px) {
  .preview-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
```

### 2.4 Screen 4: Skill Autopsy 滚动增强

#### 2.4.1 入口 Overlay

在 autopsy-scroll-container 的开头（`.autopsy-sticky` 之前）添加一个 intro overlay：

```html
<div class="autopsy-intro" aria-hidden="true">
  <p class="autopsy-intro__title">Scroll to observe knowledge loss</p>
  <div class="autopsy-intro__arrow"></div>
</div>
```

**CSS**:
```css
.autopsy-intro {
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 50vh;
  text-align: center;
  pointer-events: none;
  z-index: 2;
  opacity: var(--autopsy-intro-opacity, 1);
  transition: opacity 0.1s linear;
}

.autopsy-intro__title {
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  color: var(--accent-tail);
  max-width: 20ch;
}

.autopsy-intro__arrow {
  margin-top: 1.5rem;
  width: 2rem;
  height: 2rem;
  border-right: 2px solid var(--accent-tail);
  border-bottom: 2px solid var(--accent-tail);
  transform: rotate(45deg);
  animation: bounce-down 2s ease infinite;
}
```

#### 2.4.2 顶部进度条

在 body 中（或 autopsy-scroll-container 内）添加一个 fixed 进度条：

```html
<div class="scroll-progress-bar" id="scroll-progress-bar" aria-hidden="true">
  <div class="scroll-progress-bar__fill" id="scroll-progress-fill"></div>
</div>
```

**CSS**:
```css
.scroll-progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  z-index: 60;
  background: var(--bg-tertiary);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.scroll-progress-bar.is-active {
  opacity: 1;
}

.scroll-progress-bar__fill {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--accent-tail), var(--accent-highlight));
  transition: width 0.1s linear;
}
```

#### 2.4.3 Retention 数字放大

现有 `.autopsy-retention` 的 `font-size: 1.35rem` 太小。改为：

```css
.autopsy-retention {
  display: block;
  color: var(--accent-tail);
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 6vw, 4rem);
  font-weight: 400;
  line-height: 1;
}
```

#### 2.4.4 JS 更新 (home.js)

在 `updateAutopsy()` 函数中添加：

```javascript
// 进度条
var progressBar = document.getElementById("scroll-progress-bar");
var progressFill = document.getElementById("scroll-progress-fill");
var autopsyContainer = document.querySelector(".autopsy-scroll-container");
var autopsyIntro = document.querySelector(".autopsy-intro");

// 在 updateAutopsy() 末尾添加:
if (progressBar && progressFill) {
  var isInAutopsy = progress > 0 && progress < 1;
  progressBar.classList.toggle("is-active", isInAutopsy);
  progressFill.style.width = (progress * 100).toFixed(1) + "%";
}

// Intro overlay 淡出
if (autopsyIntro) {
  var introOpacity = Math.max(0, 1 - progress * 4); // 前 25% 滚动内淡出
  autopsyIntro.style.setProperty("--autopsy-intro-opacity", String(introOpacity));
  autopsyIntro.style.display = introOpacity < 0.01 ? "none" : "";
}
```

### 2.5 Screen 5: Explore 卡片增强

给 3 张 explore-card 添加 badge：

```html
<a class="explore-card" href="tasks.html">
  <h3>Explore the Benchmark</h3>
  <span class="explore-badge">208 tasks &middot; 6 categories</span>
  <p>Browse all oracle-verified exception-heavy variants with deterministic verifiers.</p>
  <span class="arrow" aria-hidden="true">&rarr;</span>
</a>

<a class="explore-card" href="experiments.html">
  <h3>View Full Experiments</h3>
  <span class="explore-badge">6 interactive charts</span>
  <p>Collapse curves, retention analysis, ablation studies, and case comparisons.</p>
  <span class="arrow" aria-hidden="true">&rarr;</span>
</a>

<a class="explore-card" href="#bibtex">
  <h3>Read Paper</h3>
  <span class="explore-badge">EMNLP 2026</span>
  <p>Cite with BibTeX. arXiv preprint coming soon.</p>
  <span class="arrow" aria-hidden="true">&rarr;</span>
</a>
```

**CSS**:
```css
.explore-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  color: var(--accent-highlight);
  font-family: var(--font-code);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  background: color-mix(in srgb, var(--accent-highlight) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--accent-highlight) 40%, var(--border));
  border-radius: 999px;
}
```

## 3. Tasks 页增强（tasks.html）

### 3.1 准备接收 208 任务

当前 `tasks.js` 的结构已能处理任意数量的 tasks。需要改的：

1. **gallery-count 文案**: 把 `"Full 208-task data will be added"` 改为 `"{N} of 208 tasks shown"` 的动态文案
2. **加载状态**: 添加一个 skeleton loading 动画，等 JSON fetch 完成后替换

修改 tasks.js 中 `renderGallery()`:
```javascript
function renderGallery() {
  if (!taskGrid || !galleryCount) return;
  var visible = taskState.tasks.filter(taskMatches);
  var total = taskState.tasks.length;
  galleryCount.textContent = total === 208
    ? "Showing " + visible.length + " of " + total + " tasks"
    : "Showing " + visible.length + " sample tasks (" + total + " of 208 loaded)";
  // ... rest unchanged
}
```

### 3.2 不需要改 HTML 结构

当前的 taxonomy cards + gallery toolbar + filter + search 结构已经很好，能处理 208 个任务。

## 4. Experiments 页增强（experiments.html）

### 4.1 添加锚点 ID 确保跳转正确

确保 experiments.html 中各 section 的 id 与首页链接的锚点匹配：
- `#introduction` → 已有
- `#main-results` → 已有
- `#distillation-example` → 已有

### 4.2 benchmark-pipeline.png 展示

在 experiments.html 的 `#introduction` section 中，introduction-infographic.png 之后，添加 benchmark-pipeline.png：

```html
<figure class="image-figure pipeline-figure">
  <div class="image-frame">
    <img src="static/images/benchmark-pipeline.png"
         alt="TailSkills benchmark construction pipeline showing task selection, variant injection, and oracle verification."
         width="1000" height="800" loading="lazy" decoding="async">
  </div>
  <figcaption>
    Benchmark construction pipeline: 26 base tasks, 14 variant types, 208 oracle-verified variants.
  </figcaption>
</figure>
```

## 5. 图片尺寸优化

`distillation-example.png` 是 3.2MB（7648x3419），太大了。在引用之前，添加 `loading="lazy"` 并限制显示尺寸（CSS max-width 已控制）。Codex 不需要压缩图片，但需要确保 `loading="lazy"` 在所有 `<img>` 上都有。

## 6. Commit 策略（6 步）

```
Commit 1: feat: add figure preview gallery section to homepage
  - 新增 #figure-preview section HTML
  - 新增 .preview-grid / .preview-card / .preview-frame CSS
  - 引入 benchmark-pipeline.png（之前未使用）

Commit 2: feat: enhance skill autopsy with scroll progress and intro overlay
  - 新增 .autopsy-intro overlay HTML + CSS
  - 新增 .scroll-progress-bar HTML + CSS
  - 放大 .autopsy-retention 字号
  - 更新 home.js updateAutopsy() 添加进度条和 overlay 控制

Commit 3: feat: add mini collapse chart preview on homepage
  - 新增 #mini-collapse-chart canvas HTML
  - 新增 .mini-chart-preview / .chart-link CSS
  - 更新 home.js 添加 setupMiniChart() 函数
  - 首页动态加载 Chart.js

Commit 4: feat: enhance explore cards with badges and improve nav discoverability
  - 3 张 explore-card 添加 .explore-badge
  - 新增 .explore-badge CSS
  - 更新 explore-card 文案

Commit 5: feat: add benchmark-pipeline to experiments page and improve task counter
  - experiments.html 添加 benchmark-pipeline.png
  - tasks.js 更新 gallery-count 动态文案

Commit 6: fix: final QA - check all links, alt text, lazy loading, responsive
  - 验证所有内部链接可跳转
  - 验证所有图片有 loading="lazy"
  - 验证移动端布局
  - 验证暗色模式
  - push 到 origin gh-pages
```

## 7. Git 操作

每次 commit 后:
```bash
cd D:\codes\tailskill
git add -A
git commit -m "<message>"
git push origin gh-pages
```

## 8. 约束（不要违反）

1. **纯 HTML/CSS/JS** — 无框架、无 npm、无构建工具
2. **不修改 experiments.html 中已有的 Chart.js 数据** — 数据已验证正确
3. **不修改 tasks.html 的 taxonomy cards** — 数据已验证正确
4. **保留现有 CSS 变量系统和主题切换**
5. **不用 emoji 做图标**
6. **图片全部 `loading="lazy"` + `decoding="async"`**
7. **保留无障碍**: skip link, aria-labels, prefers-reduced-motion
8. **Chart.js 在首页用动态加载（document.createElement('script')），不要在 index.html 加 `<script src="chart.js">`**

## 9. 立即开始

1. 先 `cat docs/iteration-3-requirements.md` 完整阅读本文档
2. 再 `cat index.html static/css/styles.css static/js/home.js` 了解现有代码
3. 按第 6 节的 6 步 commit 策略逐步执行
4. 每次 push 后等 1-2 分钟验证 https://tailskill-bench.github.io/tailskill/
