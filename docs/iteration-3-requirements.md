# TailSkills 网页优化 — 第三轮迭代需求 (v3)

> 读取此文件后严格按照要求执行。每完成一个阶段 commit + push。
> 分支: gh-pages | 项目: D:\codes\tailskill
> 线上验证: https://tailskill-bench.github.io/tailskill/

---

## 0. 当前状态（已验证，不要假设）

**三页已完成：** index.html, tasks.html, experiments.html
**JS 已拆分：** main.js, home.js, tasks.js, experiments.js
**tasks.json 已有 54 个任务 / 208 个变体** — 不需要重新生成！
**桌面导航 900px+ 已可见** — 不需要重复添加 CSS
**`.is-current` 导航高亮已实现** — styles.css:322 + main.js:104-123

**已知 bug（必须修复）：**
- `tasks.js:80` — `total` 变量未定义，导致 gallery 显示 "Showing N of undefined task variants"
- `tasks.js:28-31` — `resultLabel()` 没有处理 null 值

**未使用的图片：**
- `benchmark-pipeline.png` (758KB) — 论文核心流程图，目前没有任何页面引用
- `category-collapse-curves.jpg` (140KB) — 被 Chart.js 替代，可以不用

---

## 1. 本轮要解决的 7 个问题

| # | 问题 | 严重程度 |
|---|------|----------|
| P1 | 用户滚动到 Autopsy (300vh) 时以为到底了，不知道还有 Tasks/Experiments 页面 | 🔴 HIGH |
| P2 | 首页内容太空泛，只有数字和文字动画，没有论文实际内容的展示 | 🔴 HIGH |
| P3 | Tasks 页面的 `total` 变量 bug 导致显示异常 | 🔴 HIGH (bug) |
| P4 | Skill Autopsy 滚动效果太不明显，用户感知不到变化 | 🟡 MEDIUM |
| P5 | 首页应该有论文图表的缩略预览，点击跳转到 experiments 详情页 | 🟡 MEDIUM |
| P6 | benchmark-pipeline.png 未被使用，这是论文核心流程图 | 🟡 MEDIUM |
| P7 | 缺少创意交互动效，页面不够有吸引力 | 🟢 LOW |

---

## 2. 设计哲学

论文核心是**"消失"**——tail 知识在压缩中逐渐丢失。所有新增交互都应强化这个主题。

**首页叙事节奏（调整后 5 屏）：**

```
吸引（Hero + 压缩滑块）→ 震撼（数字 + mini chart）→ 预览（论文图表缩略图）→ 体验（Autopsy 增强）→ 引导（Explore 卡片 + BibTeX）
```

**关键原则：**
1. **Trailer 不等于 Movie** — 首页是预告片，不是正片。展示小图预览，点击跳转看大图。
2. **渐进式加载** — 图片用 `loading="lazy"`，大图缩略图用 `width`/`height` 防 CLS。
3. **零依赖首页** — 首页不加载 Chart.js。用 inline SVG 做迷你图表预览（~2KB vs 210KB）。
4. **一次只做一件事** — Autopsy 增强只做 4 项（5a-5d），不做粒子特效。
5. **可访问性不可妥协** — 所有动画尊重 `prefers-reduced-motion`。

---

## 3. 具体实施步骤

### Step 1: 修复已知 bug + 首页结构重组

**1a. 修复 tasks.js bug（P3）**

在 `tasks.js` 的 IIFE 内部，`renderGallery()` 函数之前，添加：

```javascript
// 在 fetch 回调内，taskState.tasks = data.tasks 之后添加:
var total = taskState.tasks.reduce(function (sum, t) {
  return sum + t.variants.length;
}, 0);
```

修改 `resultLabel()` 添加 null 处理：

```javascript
function resultLabel(value) {
  if (value === null || value === undefined) {
    return '<span class="result-pill result-null">—</span>';
  }
  if (value >= 1) {
    return '<span class="result-pill result-pass">PASS</span>';
  }
  return '<span class="result-pill result-fail">FAIL</span>';
}
```

添加 `.result-null` 的 CSS：

```css
.result-null {
  background: var(--bg-secondary);
  color: var(--text-tertiary);
}
```

**1b. 首页结构重组（P1, P2）**

当前首页结构：Hero → Findings → Autopsy(300vh) → Explore → BibTeX

新首页结构：

```html
<main id="main" class="page-transition">
  <!-- Screen 1: Hero（保持不变，已有压缩滑块） -->
  <section id="hero" ...> ... </section>

  <!-- Screen 2: Core Findings + Mini Chart（新增 mini chart） -->
  <section id="core-findings" ...>
    <!-- 保持 3 个 stat cards -->
    <!-- 新增：inline SVG 迷你图表 -->
    <div class="mini-chart-preview">
      <svg class="mini-collapse-chart" viewBox="0 0 200 120">
        <!-- Common-case line: 50.8, 52.5, 49.2, 49.2 -->
        <polyline points="25,60 75,55 125,62 175,62"
                  fill="none" stroke="var(--accent-common)" stroke-width="2"/>
        <!-- Tail-case line: 50.5, 35.4, 23.4, 23.1 -->
        <polyline points="25,61 75,85 125,100 175,100"
                  fill="none" stroke="var(--accent-tail)" stroke-width="2"/>
        <!-- X axis labels -->
        <text x="25" y="115" font-size="8" fill="var(--text-secondary)" text-anchor="middle">S1</text>
        <text x="75" y="115" font-size="8" fill="var(--text-secondary)" text-anchor="middle">S2</text>
        <text x="125" y="115" font-size="8" fill="var(--text-secondary)" text-anchor="middle">S3</text>
        <text x="175" y="115" font-size="8" fill="var(--text-secondary)" text-anchor="middle">S4</text>
      </svg>
      <a href="experiments.html#main-results" class="chart-expand-link">
        View full interactive chart →
      </a>
    </div>
  </section>

  <!-- Screen 3: Figure Preview Gallery（新增，P2, P5, P6） -->
  <section id="figure-gallery" ...>
    <p class="section-kicker">Paper Figures</p>
    <h2>At a glance</h2>
    <div class="figure-grid">
      <a class="figure-card" href="experiments.html#introduction">
        <img src="static/images/benchmark-pipeline.png"
             alt="TailSkills benchmark pipeline"
             loading="lazy" width="300" height="200"/>
        <span class="figure-label">Benchmark Pipeline</span>
      </a>
      <a class="figure-card" href="experiments.html#introduction">
        <img src="static/images/introduction-infographic.png"
             alt="Skill distillation process"
             loading="lazy" width="300" height="200"/>
        <span class="figure-label">Distillation Process</span>
      </a>
      <a class="figure-card" href="experiments.html#distillation-example">
        <img src="static/images/distillation-example.png"
             alt="S1-S4 skill cards comparison"
             loading="lazy" width="300" height="134"/>
        <span class="figure-label">Skill Cards S1→S4</span>
      </a>
    </div>
  </section>

  <!-- Screen 4: Skill Autopsy（增强，P4） -->
  <section id="skill-autopsy" ...> ... </section>

  <!-- Screen 5: Explore + BibTeX（保持不变） -->
  <section id="explore" ...> ... </section>
  <section id="bibtex" ...> ... </section>
</main>
```

**关键：Figure Preview Gallery 放在 Autopsy 之前。** 这样用户在到达 300vh 的 Autopsy 之前就看到了真实的论文内容。Figure cards 全部链接到 experiments.html 的对应锚点。

**1c. Section indicator dots（P1 辅助方案）**

在首页右侧添加 section 导航圆点，帮助用户了解当前位置：

```css
.section-indicator {
  position: fixed;
  right: 1.5rem;
  top: 50%;
  transform: translateY(-50%);
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-indicator__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--border-primary);
  transition: all 0.3s ease;
  cursor: pointer;
}

.section-indicator__dot.is-active {
  background: var(--accent-tail);
  transform: scale(1.4);
}
```

用 IntersectionObserver 高亮当前 section 对应的圆点。仅在首页显示，仅在桌面端显示（900px+）。

```html
<!-- 在 index.html 的 </main> 之后添加 -->
<nav class="section-indicator" aria-label="Page sections">
  <a class="section-indicator__dot is-active" href="#hero" aria-label="Hero"></a>
  <a class="section-indicator__dot" href="#core-findings" aria-label="Findings"></a>
  <a class="section-indicator__dot" href="#figure-gallery" aria-label="Figures"></a>
  <a class="section-indicator__dot" href="#skill-autopsy" aria-label="Autopsy"></a>
  <a class="section-indicator__dot" href="#explore" aria-label="Explore"></a>
</nav>
```

在 home.js 中添加 IntersectionObserver 逻辑，检测哪个 section 在视口中。

---

### Step 2: Figure Preview Gallery 样式

```css
/* Figure Preview Gallery */
.figure-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  max-width: 720px;
  margin: 2rem auto 0;
}

@media (max-width: 700px) {
  .figure-grid {
    grid-template-columns: 1fr;
    max-width: 320px;
  }
}

.figure-card {
  display: block;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  text-decoration: none;
}

.figure-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.figure-card img {
  width: 100%;
  height: 160px;
  object-fit: cover;
  display: block;
  transition: opacity 0.3s ease;
}

.figure-card:hover img {
  opacity: 0.9;
}

.figure-label {
  display: block;
  padding: 0.6rem 0.8rem;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
  font-family: "JetBrains Mono", monospace;
}

/* Tail dissolve hover effect on figure cards */
.figure-card::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    transparent 60%,
    var(--accent-tail) 100%
  );
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
}

.figure-card {
  position: relative;
}

.figure-card:hover::after {
  opacity: 0.15;
}
```

---

### Step 3: Mini Chart 样式

```css
.mini-chart-preview {
  max-width: 320px;
  margin: 2rem auto 0;
  text-align: center;
}

.mini-collapse-chart {
  width: 100%;
  height: auto;
  border-radius: 6px;
  background: var(--bg-secondary);
  padding: 0.5rem;
}

.mini-chart-legend {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.mini-chart-legend span::before {
  content: "";
  display: inline-block;
  width: 12px;
  height: 3px;
  margin-right: 0.4rem;
  vertical-align: middle;
}

.mini-chart-legend .legend-common::before {
  background: var(--accent-common);
}

.mini-chart-legend .legend-tail::before {
  background: var(--accent-tail);
}

.chart-expand-link {
  display: inline-block;
  margin-top: 0.75rem;
  font-size: 0.8rem;
  color: var(--accent-tail);
  text-decoration: none;
  transition: opacity 0.2s;
}

.chart-expand-link:hover {
  opacity: 0.7;
}
```

---

### Step 4: 增强 Skill Autopsy 滚动效果（P4）

只做 4 项增强（5a-5d）。**不做粒子特效、不做脉冲点、不做额外 scroll hint。**

**4a. 添加 Autopsy 介绍覆盖层**

在 autopsy 容器顶部添加一个半透明覆盖层，说明这个交互的作用：

```html
<div class="autopsy-intro-overlay" aria-hidden="true">
  <p>↓ Scroll slowly to watch tail knowledge disappear</p>
</div>
```

当用户滚动超过 5% 时淡出这个覆盖层：

```css
.autopsy-intro-overlay {
  position: sticky;
  top: 0;
  z-index: 5;
  text-align: center;
  padding: 2rem 1rem;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.85rem;
  color: var(--accent-tail);
  opacity: 1;
  transition: opacity 0.5s ease;
  pointer-events: none;
}

.autopsy-intro-overlay.is-hidden {
  opacity: 0;
}
```

**4b. 固定进度条**

在 Autopsy section 顶部添加一个水平进度条：

```css
.autopsy-progress-bar {
  position: sticky;
  top: 0;
  z-index: 10;
  height: 3px;
  background: var(--bg-secondary);
}

.autopsy-progress-bar__fill {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--accent-common), var(--accent-tail));
  transition: width 0.1s linear;
}
```

```html
<!-- 在 autopsy-scroll-container 内部最顶部 -->
<div class="autopsy-progress-bar" aria-hidden="true">
  <div class="autopsy-progress-bar__fill"></div>
</div>
```

在 home.js 的 `updateAutopsy()` 函数中更新进度条宽度：
```javascript
progressBar.style.width = (progress * 100) + "%";
```

**4c. 背景色渐变（最关键的增强！）**

滚动时背景色从暖白变为冷灰，这是**最明显的视觉变化**：

在 home.js 的 `updateAutopsy()` 中添加背景色计算：

```javascript
// 在 updateAutopsy() 函数中，progress 计算之后
// 背景色：从暖白 #fafaf8 到冷灰 #f0f0ee
var bgR = Math.round(250 - progress * 10);   // 250 → 240
var bgG = Math.round(250 - progress * 10);   // 250 → 240
var bgB = Math.round(248 - progress * 10);   // 248 → 238
container.style.backgroundColor = "rgb(" + bgR + "," + bgG + "," + bgB + ")";
```

暗色模式下反过来 — 从暗色到更深：
```javascript
if (document.documentElement.getAttribute("data-theme") === "dark") {
  bgR = Math.round(26 + progress * 6);   // 26 → 32
  bgG = Math.round(26 + progress * 6);
  bgB = Math.round(35 + progress * 6);
}
```

**4d. 放大 Retention 计数器**

当前 retention 数字太小（跟随 depth-rail 布局）。改为大号居中显示：

```css
.autopsy-retention {
  display: block;
  font-size: 3rem;
  font-weight: 700;
  font-family: "Instrument Serif", serif;
  color: var(--accent-tail);
  transition: opacity 0.16s ease;
  line-height: 1.1;
}

@media (max-width: 640px) {
  .autopsy-retention {
    font-size: 2rem;
  }
}
```

将 retention 数值从 depth-rail 的侧面位置移到 autopsy 布局的顶部居中：

```html
<!-- autopsy-sticky 内部，h2 之后 -->
<div class="autopsy-stats">
  <p class="autopsy-retention-wrap">
    Tail knowledge retained:
    <span class="autopsy-retention">100.0%</span>
  </p>
</div>
```

---

### Step 5: 创意交互（P7，轻量级）

**5a. Stat card hover 展开额外信息**

当鼠标悬停在 stat card 上时，显示额外的上下文文字：

```css
.finding-stat-card p {
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: max-height 0.4s ease, opacity 0.3s ease, margin 0.3s ease;
  margin-top: 0;
}

.finding-stat-card:hover p,
.finding-stat-card:focus-within p {
  max-height: 100px;
  opacity: 1;
  margin-top: 0.5rem;
}

@media (max-width: 640px) {
  /* 移动端始终显示 */
  .finding-stat-card p {
    max-height: 100px;
    opacity: 1;
    margin-top: 0.5rem;
  }
}
```

**5b. Explore 卡片增强**

在 Explore 卡片上添加微妙的上移 + 阴影效果（已有部分，增强）：

```css
.explore-card {
  position: relative;
  overflow: hidden;
}

/* 左侧彩色条 */
.explore-card::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--accent-tail);
  transform: scaleY(0);
  transition: transform 0.3s ease;
  transform-origin: top;
}

.explore-card:hover::before {
  transform: scaleY(1);
}
```

**5c. 数字计数动画增加小数点后位数滚动**

当前计数动画从 0 滚动到目标值。为 `data-decimals="1"` 的计数器添加小数点分隔的视觉强调 — 小数部分用 `opacity: 0.6` 和更小字号：

```css
.counter-decimals {
  font-size: 0.75em;
  opacity: 0.6;
}
```

这个只需要在 home.js 的计数动画中，将结果分为整数和小数部分分别用 span 包裹即可。

---

### Step 6: Experiments 页面补充

**6a. 添加 benchmark-pipeline.png（P6）**

在 experiments.html 的 Introduction section 中，将 `introduction-infographic.png` 替换为 `benchmark-pipeline.png`，或者在 introduction section 中**同时展示两张图**：

```html
<section id="introduction" ...>
  <div class="section-inner">
    <div class="figure-pair">
      <figure>
        <img src="static/images/benchmark-pipeline.png"
             alt="TailSkills benchmark construction pipeline"
             loading="lazy"/>
        <figcaption>Benchmark Construction Pipeline</figcaption>
      </figure>
      <figure>
        <img src="static/images/introduction-infographic.png"
             alt="Skill distillation process overview"
             loading="lazy"/>
        <figcaption>Skill Distillation Process</figcaption>
      </figure>
    </div>
    <!-- 保留现有 stat cards -->
  </div>
</section>
```

```css
.figure-pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  max-width: 720px;
  margin: 0 auto 2rem;
}

@media (max-width: 700px) {
  .figure-pair {
    grid-template-columns: 1fr;
  }
}

.figure-pair figcaption {
  text-align: center;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  font-family: "JetBrains Mono", monospace;
}
```

---

## 4. Git Commit 策略（5 步）

### Commit 1: Bug fixes + structure
```
fix: tasks.js undefined variable bug + restructure homepage sections

- Fix undefined 'total' variable in tasks.js:80
- Add null handling to resultLabel() in tasks.js:28
- Add figure-gallery section placeholder to index.html
- Add mini chart SVG preview to core-findings section
```
Files: `tasks.js`, `index.html`

### Commit 2: Figure preview gallery + mini chart styles
```
feat: add figure preview gallery and inline SVG mini chart to homepage

- Add figure-grid with 3 paper figure thumbnails (links to experiments.html)
- Add inline SVG collapse curve chart (replaces Chart.js, ~2KB vs 210KB)
- Add chart-expand-link to experiments page
- All images use loading="lazy" with explicit width/height
```
Files: `index.html`, `styles.css`

### Commit 3: Enhanced autopsy scroll effects
```
feat: dramatically enhance skill autopsy scroll visibility

- Add intro overlay text that fades on scroll start
- Add sticky progress bar at top of autopsy section
- Add background color shift (warm white → cool gray) on scroll
- Enlarge retention counter (3rem, centered)
- These 4 changes make the scroll effect unmistakably visible
```
Files: `index.html`, `styles.css`, `home.js`

### Commit 4: Creative interactions + section indicator
```
feat: add creative interactions and section navigation dots

- Add stat card hover expand (hidden text reveals on hover)
- Add explore card left-border accent animation
- Add section indicator dots on homepage (fixed right edge)
- Add IntersectionObserver for dot highlighting
- Mobile: stat card text always visible, dots hidden
```
Files: `index.html`, `styles.css`, `home.js`

### Commit 5: Experiments page + final QA
```
feat: add benchmark-pipeline figure to experiments page + QA

- Show both pipeline and infographic in experiments introduction
- Add figure-pair responsive grid layout
- Verify all links between pages work
- Verify all data matches paper
- Verify dark mode on all new components
- Verify mobile responsive
- Test with prefers-reduced-motion
```
Files: `experiments.html`, `styles.css`

---

## 5. 验证清单

每完成一个 commit，在浏览器中验证：

- [ ] 首页 Figure Gallery 3 张图都显示，点击都跳转到 experiments.html 正确锚点
- [ ] 首页 Mini Chart 显示两条线（绿色 common、粉色 tail），"View full chart" 链接有效
- [ ] 首页 Autopsy 滚动时：进度条在顶部增长、背景色变化明显、retention 数字大且清晰
- [ ] 首页右侧 section indicator dots 正确高亮当前 section
- [ ] Stat cards hover 时显示描述文字，移动端始终显示
- [ ] Explore 卡片 hover 时左侧出现粉色竖条
- [ ] Tasks 页面 gallery 计数显示正确的总数（"Showing N of 208 task variants"）
- [ ] Experiments 页显示 benchmark-pipeline.png
- [ ] 所有新组件在暗色模式下正确显示
- [ ] 移动端（375px）布局正常
- [ ] `prefers-reduced-motion` 下所有动画禁用
- [ ] 图片使用 `loading="lazy"`
- [ ] 所有链接可访问（键盘导航 + aria-labels）

---

## 6. 不要做的事

- ❌ 不要在首页加载 Chart.js（用 inline SVG）
- ❌ 不要重新生成 tasks.json（已有 54 tasks / 208 variants）
- ❌ 不要添加粒子/溶解特效（太复杂，可能影响可读性）
- ❌ 不要添加脉冲点动画（不需要）
- ❌ 不要添加额外的 scroll-hint（intro overlay 已足够）
- ❌ 不要使用 emoji 做图标
- ❌ 不要添加 npm/框架
- ❌ 不要修改 main.js 中的导航高亮逻辑（已正确实现）
- ❌ 不要添加 .is-current 的 CSS（已存在于 styles.css:322）

---

## 7. 图片文件参考

```
D:\codes\tailskill\static\images\
├── benchmark-pipeline.png         (758KB) ← 🔴 本轮必须使用（experiments + homepage preview）
├── introduction-infographic.png   (894KB) ← ✅ 已用（experiments），本轮也放 homepage preview
├── distillation-example.png       (3.19MB) ← ✅ 已用（experiments），本轮也放 homepage preview
│                                            ⚠️ 首页缩略图必须用 object-fit:cover 裁剪，
│                                               不要加载 7648px 原图到 300px 容器
├── case-study-comparison.jpg      (132KB) ← ✅ 已用（experiments），不改动
└── category-collapse-curves.jpg   (140KB) ← 不需要使用（被 Chart.js/inline SVG 替代）
```

**⚠️ distillation-example.png 注意事项：**
原图 7648x3419px / 3.19MB。首页 figure-card 中使用时：
- `width="300" height="134"` — 明确指定缩略图尺寸
- `loading="lazy"` — 延迟加载
- `object-fit: cover` — CSS 裁剪显示
- 浏览器会自动缩放，但如果 Lighthouse 分数受影响，后续需要创建专用缩略图
