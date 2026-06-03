# TailSkills 网页优化 — 第二轮迭代需求 (v2)

> 读取此文件后严格按照要求执行。每完成一个阶段 commit + push。
> 分支: gh-pages | 项目: D:\codes\tailskill
> 线上验证: https://tailskill-bench.github.io/tailskill/

---

## 0. 设计哲学

论文的核心不是"数据表格"而是**"消失"**。所有交互都应让访客**感受到**知识在压缩中逐渐消失。

首页叙事节奏（4 屏，约 3-4 次滚动）：

```
吸引（Hero）→ 震撼（数字）→ 体验（Autopsy）→ 引导（导航卡片）
```

每一屏都有清晰的视觉焦点，大量留白，不堆砌。

---

## 1. 架构变更

### 1.1 三页结构

```
index.html          → 首页（精简叙事，4 屏，约 3-4 次滚动）
tasks.html          → Benchmark 任务展示（全部 208 任务）
experiments.html    → 实验结果与分析（图表、消融、case study）
```

### 1.2 JS 拆分

```
static/js/main.js          → 通用：主题切换、导航、IntersectionObserver、getCssVar()
static/js/home.js           → 首页：压缩滑块、滚动动效、数字计数、Skill Autopsy
static/js/tasks.js          → 任务页：Gallery 渲染/过滤/搜索、Taxonomy 展开
static/js/experiments.js    → 实验页：Chart.js 初始化、主题变更重建
```

### 1.3 页面加载方式

```html
<!-- index.html -->
<script src="static/js/main.js" defer></script>
<script src="static/js/home.js" defer></script>

<!-- tasks.html -->
<script src="static/js/main.js" defer></script>
<script src="static/js/tasks.js" defer></script>

<!-- experiments.html -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.6/dist/chart.umd.min.js" defer></script>
<script src="static/js/main.js" defer></script>
<script src="static/js/experiments.js" defer></script>
```

Chart.js 只在 experiments 页加载。首页和 tasks 页不需要。

---

## 2. 全局样式调整

### 2.1 标题字体缩小（约 35%）

```css
/* 修改前 */
h1 { font-size: clamp(4.5rem, 17vw, 12rem); }
h2 { font-size: clamp(2.3rem, 7vw, 5.2rem); }
h3 { font-size: clamp(1.25rem, 2.2vw, 1.75rem); }

/* 修改后 */
h1 { font-size: clamp(2.6rem, 7vw, 4.5rem); }
h2 { font-size: clamp(1.5rem, 3.5vw, 2.6rem); }
h3 { font-size: clamp(1.05rem, 1.6vw, 1.3rem); }
```

Hero 标题 `.hero-title` 同步缩小。

### 2.2 图片尺寸缩小

所有图片限制 max-width 并居中：

```css
.image-frame {
  max-width: 720px;    /* 之前无限制 */
  margin: 0 auto;
}
.intro-figure { max-width: 640px; }    /* 之前 920px */
.pipeline-figure { max-width: 700px; } /* 之前 980px */
.case-figure { max-width: 700px; }     /* 之前 980px */
```

### 2.3 导航栏添加页面链接 + 当前页高亮

```html
<div class="nav-links" id="nav-links">
  <a href="index.html" class="nav-link">Home</a>
  <a href="tasks.html" class="nav-link">Tasks</a>
  <a href="experiments.html" class="nav-link">Experiments</a>
</div>
```

当前页面链接加 `is-current` class：
```css
.nav-link.is-current {
  color: var(--accent-highlight);
  font-weight: 700;
}
```

每个 HTML 文件的 `<body>` 上加一个标识 class，JS 根据它高亮当前页：
```html
<!-- index.html -->
<body data-page="home">

<!-- tasks.html -->
<body data-page="tasks">

<!-- experiments.html -->
<body data-page="experiments">
```

### 2.4 页面切换过渡动画（全局）

所有页面加载时 body 淡入：

```css
@keyframes page-enter {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
body { animation: page-enter 0.35s ease; }
```

---

## 3. 首页重构 (index.html) — 详细设计

首页是"电影预告片"。4 个 section，每个有明确焦点。

### Section A: Hero（保留现有，微调）

保留压缩滑块交互。调整：
- 标题字体缩小（2.1 已定义）
- Hero 区域 min-height 从 100vh 改为 `min-height: max(85vh, 500px)` — 不占满屏，留出下方预览
- 在 Hero 底部添加一个向下滚动的微妙提示：一个小箭头 bounce 动画

```css
.scroll-hint {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  animation: bounce-down 2s ease infinite;
  color: var(--text-secondary);
  font-size: 1.2rem;
}
@keyframes bounce-down {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(8px); }
}
```

### Section B: 核心发现（3 个 stat cards + 数字动画）

布局：3 个等宽卡片横排（移动端竖排），居中，max-width 960px。

```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│  27.4pp        │  │  CI = 0.65     │  │  0.3% Gap      │
│  ▼ DROP        │  │  ▼ INDEX       │  │  ▼ BASELINE    │
│                │  │                │  │                │
│  54% relative  │  │  Tail degrades │  │  Oracle-       │
│  degradation   │  │  2× faster     │  │  verified      │
└────────────────┘  └────────────────┘  └────────────────┘
```

**数字计数动画**：进入视口时，数字从 0 平滑滚动到目标值：
- `27.4` — 0→27.4, 600ms, ease-out
- `0.65` — 0.00→0.65, 500ms, ease-out
- `0.3` — 0.0→0.3, 400ms, ease-out

用 `requestAnimationFrame` + `IntersectionObserver` 实现。每个数字独立触发。

**卡片设计**：
- 背景: `var(--bg-secondary)`
- 边框: `1px solid var(--border)`
- 顶部: 3px 色条（tailpink 渐变）
- 数字: `clamp(2rem, 5vw, 3.2rem)`, `--accent-tail` 颜色
- 标签: `var(--font-code)`, `0.78rem`, uppercase

### Section C: Skill Autopsy — 滚动驱动的知识消失动画 🔥

这是首页的**核心创意交互**。与 Hero slider 不同，这个是**被动体验**——访客只需要向下滚动，就能看到 tail 知识在眼前消失。

**布局**：左侧是滚动进度指示器（sticky），右侧是 skill 文本卡片。

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  Watch tail knowledge disappear as you scroll            │
│                                                          │
│  ┌─ Depth ─┐  ┌─── Skill Document ───────────────────┐  │
│  │         │  │                                      │  │
│  │  ● S1   │  │  Dependencies                        │  │
│  │  ○ S2   │  │  pip install numpy scipy cvxpy       │  │
│  │  ○ S3   │  │                                      │  │
│  │  ○ S4   │  │  ┌─ Tail Knowledge ──────────────┐  │  │
│  │         │  │  │ If ModuleNotFoundError:        │  │  │
│  │  100%   │  │  │   pip install --no-cache       │  │  │
│  │  tail   │  │  │   cvxpy==1.4.2                 │  │  │
│  │  left   │  │  └───────────────────────────────┘  │  │
│  │         │  │                                      │  │
│  │         │  │  Analysis Workflow                   │  │
│  │         │  │  1. Load data from CSV               │  │
│  │         │  │  2. Compute trend                    │  │
│  │         │  │  3. Extract dominant factor          │  │
│  │         │  │  4. Run attribution                  │  │
│  │         │  │                                      │  │
│  │         │  │  Solver: prob.solve(cp.CLARABEL)     │  │
│  └─────────┘  └──────────────────────────────────────┘  │
│                                                          │
│  "Tail knowledge retained: 100%"                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**滚动行为**（总滚动距离约 300vh）：

| 滚动位置 | 深度 | Tail 文本状态 | 进度指示器 |
|---------|------|-------------|-----------|
| 0% | S1 | 粉色清晰可见 | ●S1 100% |
| 25% | S2 | 粉色透明度 0.6, 轻微模糊 | ○S2 43.5% |
| 50% | S3 | 粉色透明度 0.3, 模糊 2px, 删除线 | ○S3 22.7% |
| 75% | S4 | 粉色透明度 0.08, 模糊 4px, 几乎不可见 | ○S4 15.7% |

**实现方式**：
- 外层容器 `height: 300vh`，内部 skill 文本 `position: sticky; top: 20vh`
- 用 `window.addEventListener('scroll', ...)` 计算滚动进度 0-1
- 根据进度设置粉色文本的 CSS 变量：
  ```css
  .tail-text {
    opacity: var(--tail-opacity, 1);
    filter: blur(var(--tail-blur, 0px));
    text-decoration: line-through var(--tail-strikethrough-opacity, 0);
  }
  ```
- 进度指示器也随滚动高亮当前深度

**Skill 文本内容**（来自论文 E1 variant 的 Dependencies 部分）：

```
Dependencies:
pip install numpy scipy cvxpy==1.4.2

[TAIL] If ModuleNotFoundError: the package may have been removed.
[TAIL] Reinstall with: pip install --no-cache cvxpy==1.4.2

Analysis Workflow:
1. Load data from CSV files
2. Compute trend using linear regression
3. Extract dominant factor via PCA
4. Run attribution analysis

Solver Configuration:
Use prob.solve(solver=cp.CLARABEL)
```

`[TAIL]` 标记的行在 HTML 中用 `<span class="tail-text">` 包裹。

### Section D: 导航卡片（3 张）

3 张卡片横排（移动端竖排），居中，max-width 900px。每张卡片：
- 标题
- 一行简短描述
- 右下角箭头 "→"
- Hover 时整体上浮 4px + 边框变为主题色

```
┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│  Explore the       │  │  View Full         │  │  Read Paper        │
│  Benchmark         │  │  Experiments       │  │                    │
│                    │  │                    │  │                    │
│  14 variant types  │  │  Interactive       │  │  arXiv preprint    │
│  across 6          │  │  collapse curves   │  │  BibTeX citation   │
│  categories        │  │  Ablation studies  │  │                    │
│  208 tasks         │  │  Case study        │  │                    │
│                    │  │                    │  │                    │
│              →     │  │              →     │  │              →     │
└────────────────────┘  └────────────────────┘  └────────────────────┘
```

- 第 1 张链接到 `tasks.html`
- 第 2 张链接到 `experiments.html`
- 第 3 张链接到 arXiv（占位 `#`，论文发布后更新）

### Section E: BibTeX + Footer

从当前首页移植，保持不变。

---

## 4. Tasks 页 (tasks.html) — 详细设计

### 4.1 页面标题区域

```
TailSkills Benchmark
208 oracle-verified exception-heavy task variants with deterministic verifiers
```

### 4.2 Taxonomy 分类网格

从当前首页迁移 6 个 taxonomy cards（保持可展开交互）。

### 4.3 任务 Gallery

从当前首页迁移，保持过滤/搜索功能。

关键修改：
- Gallery 上方显示 "Showing N sample tasks from placeholder data. Full 208-task data will be added."
- 保持 8 个 sample tasks（`data/tasks.json` 不改）

### 4.4 页面底部

简单 footer + 返回首页链接。

---

## 5. Experiments 页 (experiments.html) — 详细设计

### 5.1 页面标题区域

```
Experimental Results
1,048 skill-conditioned agent runs across four distillation depths
```

### 5.2 Introduction 图

从当前首页 Introduction section 迁移：
- `static/images/introduction-infographic.png`
- 3 个 stat cards（common-case retention, tail-logic retention, total skill size）

### 5.3 Main Results

从当前首页迁移：
- 两个 Chart.js 图表（overall collapse + category-specific）
- 数据表格
- 3 个 takeaway cards

### 5.4 Ablation Studies

从当前首页迁移：
- Retention 柱状图（Chart.js）
- 4 个 finding cards
- Deletion callout
- Forgetting rate 表

### 5.5 Case Study

从当前首页迁移：
- `static/images/case-study-comparison.jpg`
- Regular vs Tail-Aware 对比面板

### 5.6 Distillation Example（新增，补缺失图片）

添加 `static/images/distillation-example.png`：
- 这是论文中 S1→S4 skill cards 对比图
- Caption: "Skill text at each distillation depth (energy-market-pricing, E1 variant). Tail-handling knowledge (pink) disappears at S3 while common workflow (green) persists."

### 5.7 页面底部

Footer + 返回首页链接。

---

## 6. 三个新创意动效（详细规格）

### 6.1 数字计数动画

```javascript
// 每个stat card进入视口时触发
function animateCounter(element, target, duration, decimals) {
  var start = 0;
  var startTime = null;
  function step(timestamp) {
    if (!startTime) startTime = timestamp;
    var progress = Math.min((timestamp - startTime) / duration, 1);
    var eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    var current = start + (target - start) * eased;
    element.textContent = current.toFixed(decimals);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}
```

触发方式：IntersectionObserver threshold 0.5。

### 6.2 滚动驱动 Skill Autopsy

```javascript
// 外层容器 300vh, 内部 sticky
var container = document.querySelector('.autopsy-scroll-container');
var tailTexts = document.querySelectorAll('.tail-text');
var depthIndicators = document.querySelectorAll('.depth-indicator');
var retentionLabel = document.querySelector('.autopsy-retention');

window.addEventListener('scroll', function() {
  var rect = container.getBoundingClientRect();
  var containerHeight = container.offsetHeight - window.innerHeight;
  var scrolled = -rect.top;
  var progress = Math.max(0, Math.min(1, scrolled / containerHeight));

  // 4 stages: 0-0.25=S1, 0.25-0.5=S2, 0.5-0.75=S3, 0.75-1=S4
  var opacity, blur, strikethrough, retention;
  if (progress < 0.25) {
    opacity = 1; blur = 0; strikethrough = 0; retention = 100;
  } else if (progress < 0.5) {
    var t = (progress - 0.25) / 0.25;
    opacity = 1 - 0.4 * t; blur = t * 1.5; strikethrough = t; retention = 100 - 56.5 * t;
  } else if (progress < 0.75) {
    var t = (progress - 0.5) / 0.25;
    opacity = 0.6 - 0.3 * t; blur = 1.5 + t * 1.5; strikethrough = 1; retention = 43.5 - 20.8 * t;
  } else {
    var t = (progress - 0.75) / 0.25;
    opacity = 0.3 - 0.22 * t; blur = 3 + t * 1.5; strikethrough = 1; retention = 22.7 - 7 * t;
  }

  tailTexts.forEach(function(el) {
    el.style.opacity = opacity;
    el.style.filter = 'blur(' + blur + 'px)';
    el.style.textDecorationColor = 'rgba(226, 171, 184, ' + strikethrough + ')';
  });
  retentionLabel.textContent = retention.toFixed(1) + '%';
  // Update depth indicators...
});
```

### 6.3 导航卡片 hover 微动效

```css
.explore-card {
  padding: 2rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
  text-decoration: none;
  color: var(--text-primary);
  display: block;
}
.explore-card:hover {
  transform: translateY(-6px);
  border-color: var(--accent-highlight);
  box-shadow: 0 24px 60px var(--shadow-color);
}
.explore-card .arrow {
  transition: transform 0.3s ease;
}
.explore-card:hover .arrow {
  transform: translateX(4px);
}
```

---

## 7. Commit 策略

| # | 内容 | Message |
|---|------|---------|
| 1 | 创建 tasks.html 和 experiments.html 骨架（从 index.html 复制 header/footer/nav） | `refactor: scaffold tasks.html and experiments.html` |
| 2 | 拆分 main.js → main.js + home.js + tasks.js + experiments.js | `refactor: split JS into page-specific modules` |
| 3 | 更新 styles.css — 缩小标题/图片、添加新组件样式（autopsy, explore cards, counter animation） | `fix: reduce heading/image sizes, add new component styles` |
| 4 | 重构 index.html — Hero 微调 + stat cards + Skill Autopsy + 导航卡片 | `feat: redesign homepage with scroll-driven autopsy and stat counters` |
| 5 | 完善 tasks.html — taxonomy + gallery + variant 说明 | `feat: complete tasks page with taxonomy and gallery` |
| 6 | 完善 experiments.html — charts + ablation + case study + distillation-example.png | `feat: complete experiments page with all results and missing figure` |
| 7 | 统一导航栏 + 当前页高亮 + 页面过渡动画 | `feat: unified navigation with current page highlight and transitions` |
| 8 | 最终 QA — 测试三页、主题切换、移动端、修复问题 | `fix: final QA and polish across all three pages` |

每次 commit 后：
```bash
cd D:\codes\tailskill
git add -A
git commit -m "<message>"
git push origin gh-pages
```

---

## 8. 关键约束

1. **保持现有 CSS 变量系统** — 颜色、主题切换不变
2. **保持所有数据不变** — 图表/表格/taxonomy 数据与论文一致
3. **纯 HTML/CSS/JS** — 无框架、无 npm
4. **不要删除图片** — 特别是 `distillation-example.png` 要在 experiments 页展示
5. **分支是 gh-pages** — 不要切换
6. **不用 emoji 做图标** — 用 CSS 几何图形或 SVG
7. **字体不变** — Instrument Serif + DM Sans + JetBrains Mono
8. **亮色主题默认** — #fafaf8
9. **移动端适配** — 640px 断点
10. **无障碍** — 保持 skip link, aria-labels, prefers-reduced-motion

---

## 9. 立即开始

1. 读取 `docs/iteration-2-requirements.md`（本文件）
2. 读取现有文件: `index.html`, `static/css/styles.css`, `static/js/main.js`
3. 按 commit 策略逐步执行
4. 每次 push 后等 1-2 分钟，验证 https://tailskill-bench.github.io/tailskill/
