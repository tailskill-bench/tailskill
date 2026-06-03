# TailSkills 网页 — 第四轮迭代需求 (v4)

> **不要假设任何东西。先读完这个文档，再读完当前所有代码文件，再开始改。**
> 分支: gh-pages | 项目: D:\codes\tailskill
> 线上: https://tailskill-bench.github.io/tailskill/

---

## 0. 图片内容说明（必须理解）

**在看代码之前，先理解每张图片到底是什么：**

| 文件名 | 内容 | 正确放法 |
|--------|------|----------|
| `introduction-infographic.png` | **Skill Distillation 流程图**：展示 S1→S2→S3→S4 的递归压缩传送带，绿色(common)部分保留，粉色(tail)部分逐步消失 | 首页 "Introduction" section，**大图展示**，类似 XSkill 的 Framework Overview |
| `benchmark-pipeline.png` | **TailSkills Benchmark 构建流程**：从 26 个 base task → 14 种 variant injection → oracle verification → 208 tasks 的完整 pipeline | 首页 "Benchmark" section 或 experiments 页 "Introduction" section |
| `distillation-example.png` | **S1-S4 Skill Cards 对比图**：4 列并排，每列是一个 generation 的 skill 文本，绿色高亮 common 部分，粉色高亮 tail 部分，可以看到 tail 部分从 S3 开始消失 | Experiments 页 "What Gets Erased" section。**首页不放大图，可以在 Autopsy 中引用** |
| `case-study-comparison.jpg` | **Regular vs Tail-Aware 蒸馏对比**：左右两列，展示同一个 C4 extreme-value task 在两种蒸馏策略下的不同结果 | Experiments 页 "Case Study" section |
| `*-preview.png` | 上述图片的缩略版（Codex v3 创建的） | 首页缩略预览用 |

**上次 Codex 犯的错：**
- ❌ 把 benchmark-pipeline.png 放到了 "What Gets Erased" 下面 → 应该放 distillation-example.png
- ❌ 把 case-study-comparison.jpg 放到了 "What Gets Erased" 旁边 → 不对
- ❌ 首页 "At a glance" 把三张图平铺 → 应该分别放在对应内容区域

---

## 1. 参考网站分析（必须先看）

### XSkill (https://xskill-agent.github.io/xskill_page)

**页面结构：**
```
Title + Authors + Affiliations
    ↓
BIG comparison figure (对比图，占页面宽度)
    ↓
Figure caption (描述图片内容的段落)
    ↓
Abstract (完整摘要文本)
    ↓
Framework Overview section
    ├── 大图 (framework.png，占满宽度)
    ├── 图的 caption
    ├── Skill Library 子section
    └── Experience Bank 子section
    ↓
Main Results (大表格)
    ↓
Analysis (多个子section，各有图表)
    ↓
Qualitative Example (详细 walkthrough)
    ↓
BibTeX
```

**关键设计模式：**
1. **图片在前，文字解释在后** — 每个图先显示，下面跟 caption 段落
2. **大图占满内容宽度** — 不是缩略图，是完整宽度的 figure
3. **学术文章的网页化** — 结构完全对应论文，但比 PDF 更易读
4. **每个 section 都有明确的标题和内容** — 没有空白区域

### SkillsBench (https://www.skillsbench.ai/tasks)

**任务卡片设计：**
1. 每个任务是一个卡片，显示**任务描述预览文本**（前几行）
2. 卡片上有 **tags**（#python, #simulation 等）
3. **点击卡片** → 展开或跳转，显示完整的任务 instruction
4. 有搜索和过滤功能

---

## 2. 首页重构（index.html）

### 2.1 首页新结构（参照 XSkill）

```
Section 1: HERO（保留）
  └─ 压缩滑块 + "but Fragile" 淡出 → 不改

Section 2: ABSTRACT（新增，参照 XSkill）
  └─ 论文摘要文本
  └─ 紧凑布局，一行 subtitle + 摘要段落

Section 3: INTRODUCTION + 大图（新增/重构）
  └─ introduction-infographic.png 大图展示（max-width: 800px）
  └─ 图片下方 caption 段落
  └─ 3 个 key stat cards（保留现有 finding-stat-grid）

Section 4: BENCHMARK OVERVIEW（新增/重构，替代 "At a glance"）
  └─ benchmark-pipeline.png 大图展示（max-width: 800px）
  └─ 图片下方 caption 段落
  └─ 6 个 taxonomy mini cards（从 tasks.html 的 taxonomy 简化版）

Section 5: SKILL AUTOPSY（保留，增强）
  └─ 保留滚动交互
  └─ 替换为真实 skill 文本示例
  └─ 移除渐变消失，改为更清晰的视觉区分

Section 6: EXPLORE + BIBTEX（保留）
```

### 2.2 Section 2: Abstract（新增）

参照 XSkill，在 Hero 之后直接放论文 Abstract：

```html
<section class="page-section" id="abstract" aria-labelledby="abstract-title">
  <div class="section-inner is-narrow">
    <h2 id="abstract-title">Abstract</h2>
    <div class="abstract-text">
      <p>When human-authored agent skills are recursively rewritten by language models, the resulting compressed variants preserve common-case knowledge but disproportionately lose rare, exception-handling instructions — the "tail knowledge." We introduce <strong>TailSkills</strong>, a benchmark of 208 oracle-verified exception-heavy task variants with deterministic verifiers, and show that tail pass rate drops from <strong>50.5% to 23.1%</strong> (a 54% relative degradation) while common-case performance stays flat. A Collapse Index of <strong>0.65</strong> at S4 confirms that tail-specific instructions degrade roughly twice as fast as regular workflow content.</p>
    </div>
  </div>
</section>
```

**CSS：**
```css
.abstract-text {
  max-width: 48rem;
  margin: 0 auto;
  font-size: 1.05rem;
  line-height: 1.7;
  color: var(--text-primary);
}

.abstract-text strong {
  color: var(--accent-tail);
}
```

### 2.3 Section 3: Introduction + 大图

**删除现有的 "Core Findings" 标题和 "At a glance" grid。替换为：**

```html
<section class="page-section" id="introduction" aria-labelledby="intro-title">
  <div class="section-inner">
    <p class="section-kicker">Introduction</p>
    <h2 id="intro-title">Recursive skill rewriting erodes rare knowledge</h2>

    <!-- 大图：introduction-infographic.png -->
    <figure class="paper-figure">
      <div class="image-frame intro-figure">
        <img src="static/images/introduction-infographic.png"
             alt="Skill distillation conveyor belt: as skills are recursively rewritten from S1 to S4, common-case workflow instructions (green) persist while tail-case exception handling (pink) progressively disappears."
             width="1000" height="1284" loading="lazy" decoding="async">
      </div>
      <figcaption>
        Recursive skill distillation progressively compresses agent skills.
        Common workflow instructions (green) are preserved across S1 to S4,
        while tail-case exception handling (pink) is progressively lost.
      </figcaption>
    </figure>

    <!-- Key stats（保留现有的 finding-stat-grid，但移除 mini chart） -->
    <div class="finding-stat-grid">
      <!-- 保留现有的 3 个 stat cards，不做改动 -->
    </div>
  </div>
</section>
```

**CSS（新增 paper-figure 样式）：**
```css
.paper-figure {
  max-width: 800px;
  margin: 2rem auto;
}

.paper-figure .image-frame {
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  box-shadow: 0 24px 70px var(--shadow-color);
}

.paper-figure img {
  width: 100%;
  display: block;
}

.paper-figure figcaption {
  max-width: 48rem;
  margin: 1rem auto 0;
  padding: 0 1rem;
  color: var(--text-secondary);
  font-size: 0.92rem;
  line-height: 1.6;
  text-align: center;
}

.intro-figure {
  max-width: 640px;
  margin: 0 auto;
}
```

### 2.4 Section 4: Benchmark Overview

**替代 "At a glance" 3-image grid。改为一张大图 + taxonomy 概览：**

```html
<section class="page-section" id="benchmark" aria-labelledby="benchmark-title">
  <div class="section-inner">
    <p class="section-kicker">Benchmark</p>
    <h2 id="benchmark-title">208 oracle-verified exception-heavy task variants</h2>

    <!-- 大图：benchmark-pipeline.png -->
    <figure class="paper-figure">
      <div class="image-frame pipeline-figure">
        <img src="static/images/benchmark-pipeline.png"
             alt="TailSkills benchmark construction pipeline: 26 base tasks across diverse domains, 14 variant injection types across 6 categories, deterministic oracle verification, producing 208 final task variants."
             width="1960" height="1142" loading="lazy" decoding="async">
      </div>
      <figcaption>
        Benchmark construction pipeline: 26 base tasks → 14 variant types across 6 categories → oracle verification → 208 task variants.
      </figcaption>
    </figure>

    <!-- Taxonomy 概览（简化版，不带展开详情） -->
    <div class="taxonomy-mini-grid">
      <div class="taxonomy-mini-card taxonomy-mini-card--a">
        <span class="taxonomy-mini-code">A</span>
        <span class="taxonomy-mini-name">Data Encoding</span>
        <span class="taxonomy-mini-count">49 variants</span>
      </div>
      <div class="taxonomy-mini-card taxonomy-mini-card--b">
        <span class="taxonomy-mini-code">B</span>
        <span class="taxonomy-mini-name">File System</span>
        <span class="taxonomy-mini-count">60 variants</span>
      </div>
      <div class="taxonomy-mini-card taxonomy-mini-card--c">
        <span class="taxonomy-mini-code">C</span>
        <span class="taxonomy-mini-name">Data Quality</span>
        <span class="taxonomy-mini-count">39 variants</span>
      </div>
      <div class="taxonomy-mini-card taxonomy-mini-card--d">
        <span class="taxonomy-mini-code">D</span>
        <span class="taxonomy-mini-name">Network</span>
        <span class="taxonomy-mini-count">35 variants</span>
      </div>
      <div class="taxonomy-mini-card taxonomy-mini-card--e">
        <span class="taxonomy-mini-code">E</span>
        <span class="taxonomy-mini-name">Dependency</span>
        <span class="taxonomy-mini-count">22 variants</span>
      </div>
      <div class="taxonomy-mini-card taxonomy-mini-card--g">
        <span class="taxonomy-mini-code">G</span>
        <span class="taxonomy-mini-name">Security</span>
        <span class="taxonomy-mini-count">3 variants</span>
      </div>
    </div>
    <a href="tasks.html" class="section-link">View all 208 tasks →</a>
  </div>
</section>
```

**CSS：**
```css
.pipeline-figure {
  max-width: 720px;
}

.taxonomy-mini-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  max-width: 640px;
  margin: 1.5rem auto 0;
}

@media (max-width: 700px) {
  .taxonomy-mini-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.taxonomy-mini-card {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.8rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 0.85rem;
}

.taxonomy-mini-code {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.6rem;
  height: 1.6rem;
  color: var(--bg-secondary);
  font-family: var(--font-code);
  font-weight: 700;
  font-size: 0.75rem;
  border-radius: 4px;
  flex-shrink: 0;
}

.taxonomy-mini-card--a .taxonomy-mini-code { background: var(--category-a); }
.taxonomy-mini-card--b .taxonomy-mini-code { background: var(--category-b); }
.taxonomy-mini-card--c .taxonomy-mini-code { background: var(--category-c); }
.taxonomy-mini-card--d .taxonomy-mini-code { background: var(--category-d); }
.taxonomy-mini-card--e .taxonomy-mini-code { background: var(--category-e); }
.taxonomy-mini-card--g .taxonomy-mini-code { background: var(--category-g); }

.taxonomy-mini-name {
  font-weight: 600;
}

.taxonomy-mini-count {
  margin-left: auto;
  color: var(--text-secondary);
  font-family: var(--font-code);
  font-size: 0.78rem;
}

.section-link {
  display: block;
  text-align: center;
  margin-top: 1.5rem;
  font-family: var(--font-code);
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--accent-highlight);
  text-decoration: none;
}

.section-link:hover {
  text-decoration: underline;
}
```

### 2.5 Section 5: Skill Autopsy（保留但改进）

**两个修改：**

1. **替换为真实 skill 示例**（当前是虚构的 energy-market-pricing 片段）：

从 `generated-tasks/` 中选一个有代表性的真实 task。使用 `energy-market-pricing--E1_missing_dep` 的实际 skill 文件内容。读取 `generated-tasks/energy-market-pricing--E1_missing_dep/environment/skills/s1/SKILL.md`，提取关键部分放入 HTML。

如果你读不到真实 skill 内容，**保持现有的虚构示例**，不要随便编造。

2. **移除渐变消失效果**（队长说渐变消失感觉不对）：
   - 保留 opacity 变化（从清晰到模糊）
   - 保留 strikethrough（删除线）
   - 保留 progress bar
   - 移除或减弱 blur 效果（blur 从 0→4.5px 改为 0→1.5px，更清晰可读）
   - 保留 intro overlay

### 2.6 删除的内容

- ❌ **删除整个 `#figure-gallery` section**（"At a glance" 三图并排）→ 被 Introduction + Benchmark 大图替代
- ❌ **删除 mini SVG chart**（"Core Findings" 下面的 inline chart）→ 不再需要，首页不放图表
- ❌ **删除 section indicator dots**（右侧固定圆点）→ 首页结构简化后不需要

---

## 3. Tasks 页重构（tasks.html）

### 3.1 移除错误的实验数据

**tasks.json 中的 S1-S4 results 全部是占位符**（S1 全 1.0, S2-S4 全 0.0），这是错误数据。

**绝对不能展示。** 修改 tasks.js：

```javascript
// renderTask 函数中：移除 result-strip（S1-S4 PASS/FAIL pills）
// 只显示 variant type tags + fragility level
```

修改后的 task card 渲染（tasks.js `renderTask` 函数）：

```javascript
function renderTask(task) {
  var variants = task.variants || [];
  var primaryCategory = variants[0] ? variants[0].category : "";
  var tags = variants.map(function (variant) {
    return '<span class="variant-tag ' + categoryClass(variant.category) + '">' +
      variant.type.replace(/_/g, " ") + '</span>';
  }).join("");

  var detail = variants.map(function (variant) {
    return '<div class="variant-detail">' +
      '<strong>' + variant.variant_name + '</strong>' +
      '<span class="variant-meta">' + variant.category_name +
      ' / ' + variant.fragility + ' fragility</span>' +
      '</div>';
  }).join("");

  return '<article class="task-card ' + categoryClass(primaryCategory) + '">' +
    '<button type="button" class="task-card__button" aria-expanded="false">' +
    '<span class="task-card__title">' + task.id + '</span>' +
    '<span class="variant-tags">' + tags + '</span>' +
    '<span class="task-card__meta"><span>Domain: ' + task.domain + '</span>' +
    '<span>' + variants.length + ' variant(s)</span></span>' +
    '</button>' +
    '<div class="task-detail" hidden>' + detail + '</div>' +
    '</article>';
}
```

### 3.2 Task card 扩展后显示任务详情（参照 SkillsBench）

当用户点击 task card 展开时，显示：
- Task name
- Domain
- 每个 variant 的类型 + fragility level
- **不显示** S1-S4 结果数据

### 3.3 修改 gallery count 文案

```javascript
galleryCount.textContent = "Showing " + visible.length + " of " + total + " tasks (" + totalVariants + " variants)";
```

其中 `total` = base task 数量，`totalVariants` = variant 总数。

---

## 4. Experiments 页（experiments.html）

### 4.1 验证图片位置

确保 experiments.html 中：
- **Introduction section**：`benchmark-pipeline.png` + `introduction-infographic.png` → ✅ 已经正确
- **Case Study section**：`case-study-comparison.jpg` → ✅ 已经正确
- **What Gets Erased section**：`distillation-example.png` → ✅ 已经正确

**如果位置正确，不要改 experiments.html。**

---

## 5. Git Commit 策略（4 步）

### Commit 1: 重构首页结构
```
refactor: redesign homepage following XSkill academic page style

- Add Abstract section (like XSkill)
- Add Introduction section with big introduction-infographic.png
- Add Benchmark Overview section with big benchmark-pipeline.png
- Remove "At a glance" figure gallery grid
- Remove mini SVG chart from Core Findings
- Remove section indicator dots
- Key stats integrated into Introduction section
```
Files: `index.html`, `static/css/styles.css`

### Commit 2: 修复 Skill Autopsy
```
fix: improve autopsy scroll with reduced blur and clearer visual

- Reduce blur range from 0-4.5px to 0-1.5px for readability
- Keep opacity change, strikethrough, progress bar, intro overlay
```
Files: `static/js/home.js`, `static/css/styles.css`

### Commit 3: 重构 Tasks 页面
```
refactor: remove incorrect experiment data from task gallery

- Remove S1-S4 PASS/FAIL result pills (data is placeholder, not verified)
- Task card shows: name, domain, variant tags, fragility
- Expanded detail shows variant info without results
- Update gallery count to show task + variant counts
```
Files: `static/js/tasks.js`, `static/css/styles.css`

### Commit 4: Final QA
```
fix: final QA - verify all image placements and cross-page links

- Verify introduction-infographic.png in Introduction section
- Verify benchmark-pipeline.png in Benchmark section
- Verify all homepage links to tasks.html and experiments.html work
- Verify dark mode on new components
- Verify mobile responsive
```

---

## 6. 不要做的事

- ❌ 不要展示未验证的 S1-S4 实验结果数据
- ❌ 不要把 distillation-example.png 放在首页大图位置（它是 experiments 详情图）
- ❌ 不要在首页使用 Chart.js
- ❌ 不要创建新的动画特效
- ❌ 不要用 emoji 做图标
- ❌ 不要改 experiments.html 的图片（已经正确）
- ❌ 不要改 experiments.html 的数据表格（已验证正确）
- ❌ 不要使用渐变模糊效果（blur 超过 2px 不可读）

---

## 7. 首页最终结构验证清单

首页应该像 XSkill 一样，是论文的网页化展示：

- [ ] Hero → 有压缩滑块交互，"but Fragile" 淡出
- [ ] Abstract → 论文摘要文本，tail 相关数据加粉色 bold
- [ ] Introduction → introduction-infographic.png **大图**（占满 800px 宽度）+ caption + 3 stat cards
- [ ] Benchmark → benchmark-pipeline.png **大图** + caption + 6 taxonomy mini cards + "View all 208 tasks →" 链接
- [ ] Skill Autopsy → 滚动交互（opacity + strikethrough + progress bar，**弱化 blur**）
- [ ] Explore → 3 张导航卡片
- [ ] BibTeX → 引用信息

---

## 8. 立即开始

1. **先阅读本文档** — `docs/iteration-4-requirements.md`
2. **阅读参考网站** — 用 webReader 或浏览器打开 https://xskill-agent.github.io/xskill_page 和 https://www.skillsbench.ai/tasks，理解它们的设计
3. **阅读当前代码** — `index.html`, `tasks.html`, `static/css/styles.css`, `static/js/home.js`, `static/js/tasks.js`
4. **理解图片内容** — 本文第 0 节列出了每张图片的正确含义和正确位置
5. **按 4 步 commit 策略执行**
6. **每次 push 后验证** https://tailskill-bench.github.io/tailskill/
