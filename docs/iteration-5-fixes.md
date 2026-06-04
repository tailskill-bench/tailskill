# TailSkills 网页 v5 修复需求

> **先完整阅读本文档，再阅读当前代码，再开始修改。**
> 分支: gh-pages | 项目: D:\codes\tailskill
> 线上: https://tailskill-bench.github.io/tailskill/

---

## 0. 图片真实含义（最重要，逐字看）

你有 5 张图片。之前 Codex 把图片的含义搞反了，导致图片全放错了位置。
**不要猜，不要 reinterpret，严格按下面来：**

| 文件名 | 尺寸 | 图片真实内容 | 必须放在哪里 |
|--------|------|-------------|-------------|
| `introduction-infographic.png` | 874KB, 1000×1284 (竖图) | Skill Distillation 传送带：S1→S2→S3→S4 压缩过程，绿色(common)保留，粉色(tail)逐渐消失 | 首页 "Introduction" section ✅ 已正确 |
| `benchmark-pipeline.png` | 741KB, 1960×1142 (宽图) | TailSkills Benchmark 构建流程：26 base task → 14 variant types → oracle verification → 208 tasks | **首页 "Benchmark" section** ❌ 当前放了 distillation-example.png；**experiments "Introduction" section** ❌ 当前也放错了 |
| `distillation-example.png` | 3115KB, 7648×3419 (超宽图) | S1-S4 Skill Cards 并排对比：4 列，每列是一个 generation 的 skill 文本，绿色高亮 common，粉色高亮 tail，tail 从 S3 开始消失 | **experiments "What Gets Erased" section** ❌ 当前是文字面板 |
| `case-study-comparison.jpg` | 129KB, 2085×1280 | Regular vs Tail-Aware 蒸馏对比：左右两列，同一个 C4 task 在两种策略下的不同结果 | **experiments "Case Study" section** ❌ 当前放了 benchmark-pipeline.png |
| `category-collapse-curves.jpg` | 136KB, 1950×1280 | 分类坍塌曲线：每个 category 的 pass rate 随 S1→S4 变化的折线图 | experiments "Main Results" section ✅ 已正确 |

**记忆口诀：**
- `introduction-infographic` = 传送带图 → Introduction
- `benchmark-pipeline` = 构建流水线 → Benchmark
- `distillation-example` = S1-S4 skill cards 对比 → What Gets Erased
- `case-study-comparison` = Regular vs Tail-Aware 对比 → Case Study

---

## 1. P0-1: 修复 experiments.html 图片位置

### 当前错误（experiments.html）：

1. **Introduction section** (约 line 48-61): 放了 `distillation-example.png` + `introduction-infographic.png`
   - ❌ `distillation-example.png` 不是 introduction 图，是 S1-S4 skill cards
   - ✅ `introduction-infographic.png` 正确

2. **Main Results section** (约 line 102-115): 放了 `case-study-comparison.jpg` + `category-collapse-curves.jpg`
   - ❌ `case-study-comparison.jpg` 不是 collapse curve，是 Regular vs Tail-Aware 对比
   - ✅ `category-collapse-curves.jpg` 正确

3. **Case Study section** (约 line 277-334): 放了 `benchmark-pipeline.png`
   - ❌ `benchmark-pipeline.png` 不是 case study 图，是构建流水线
   - 正确应该放 `case-study-comparison.jpg`

4. **What Gets Erased section** (约 line 337+): 当前是纯文字面板，没有图片
   - 应该放 `distillation-example.png`（这就是 "what gets erased" 的可视化）

### 修复方案：

**Introduction section** — 换图 + 修正 alt/caption：
```html
<figure class="image-figure figure-showcase__item figure-showcase__item--wide">
  <div class="image-frame">
    <img src="static/images/benchmark-pipeline.png"
         alt="TailSkills benchmark construction pipeline: 26 base tasks across diverse domains, 14 variant injection types, oracle verification, producing 208 task variants."
         width="1960" height="1142" loading="lazy" decoding="async">
  </div>
  <figcaption>Benchmark construction pipeline: 26 base tasks → 14 variant types → oracle verification → 208 variants.</figcaption>
</figure>
```
保留 `introduction-infographic.png`（这个是对的），只替换第一张图。

**Main Results section** — 移走 `case-study-comparison.jpg`，只保留 `category-collapse-curves.jpg`（如果需要两张图，保留 collapse curves 的那张）。

**Case Study section** — 换图：
```html
<figure class="image-figure case-figure">
  <div class="image-frame">
    <img src="static/images/case-study-comparison.jpg"
         alt="Regular distillation drops C4 extreme-value handling while tail-aware distillation preserves the recovery branch and passes verification."
         width="2085" height="1280" loading="lazy" decoding="async">
  </div>
  <figcaption>Regular vs Tail-Aware distillation on a C4 extreme-value variant. Regular loses the exception clause; Tail-Aware preserves it.</figcaption>
</figure>
```

**What Gets Erased section** — 添加图片（替代纯文字面板）：
```html
<figure class="image-figure wide-paper-figure">
  <div class="image-frame">
    <img src="static/images/distillation-example.png"
         alt="S1 to S4 skill text cards showing tail-handling knowledge (pink) progressively disappearing while common workflow (green) persists."
         width="7648" height="3419" loading="lazy" decoding="async">
  </div>
  <figcaption>Skill text at each distillation depth. Tail-handling knowledge (pink) disappears at S3 while common workflow (green) persists.</figcaption>
</figure>
```

---

## 2. P0-2: 修复首页 Benchmark section 图片

**index.html line 149-150** 当前用了 `distillation-example.png`，应该用 `benchmark-pipeline.png`。

替换：
```html
<a class="image-frame pipeline-figure" href="static/images/benchmark-pipeline.png" aria-label="Open benchmark pipeline figure at full size">
  <img src="static/images/benchmark-pipeline.png"
       alt="TailSkills benchmark construction pipeline: 26 base tasks, 14 variant types across 6 categories, oracle verification, 208 task variants."
       width="1960" height="1142" loading="lazy" decoding="async">
</a>
```
同时修正 figcaption。

---

## 3. P0-3: 补全 2 个 missing task 的 instruction

**当前状态：** `gh-repo-analytics` 和 `trend-anomaly-causal-inference` 在 `data/task-details.json` 中标记为 `instruction_available: false`。

**本地数据确认：** 这两个 task 在 `D:\temp\Tailskill_base\tailskills\generated-tasks\` 目录中确实存在：
```
gh-repo-analytics--B1_readonly_output/instruction.md
trend-anomaly-causal-inference--A1_bom/instruction.md
trend-anomaly-causal-inference--C4_extremes/instruction.md
...等
```

**修复方案：**
1. 读取 `D:\temp\Tailskill_base\tailskills\generated-tasks\gh-repo-analytics--B1_readonly_output\instruction.md`
2. 读取 `D:\temp\Tailskill_base\tailskills\generated-tasks\trend-anomaly-causal-inference--A1_bom\instruction.md`
3. 将 instruction 文本写入 `data/task-details.json` 对应 task 的 `instruction` 字段
4. 设置 `instruction_available: true`
5. 更新 `source_repository` 为 "TailSkills"，`source_path` 为 `generated-tasks/<task-name>/instruction.md`

---

## 4. P1-1: 修复 Skill Autopsy 使用真实 skill 文本

**当前：** `index.html` line 226-240 使用了虚构的 skill 文本片段。

**真实数据：** `D:\temp\Tailskill_base\tailskills\generated-tasks\energy-market-pricing--E1_missing_dep\environment\skills\s1\SKILL.md` 有完整的 S1 skill 文本（约 200 行，很长）。

**修复方案：** 提取 skill 中最关键的 15-20 行作为 Autopsy 示例，必须包含：
- 依赖安装部分（包含 tail 处理的 `[TAIL]` 行）
- 核心工作流步骤
- solver 配置

从 SKILL.md 中提取的关键段落（用这些替换现有的虚构文本）：

```
Dependencies:
	pip install numpy scipy cvxpy

[TAIL] If cvxpy is unavailable, reinstall with:
	pip install --no-cache-dir cvxpy==1.4.2
[TAIL] Prefer CLARABEL solver; if missing, fall back to SCIPY.

Analysis Workflow:
	1. Load network.json and validate buses, generators, demand
	2. Formulate market-clearing objective with power-flow constraints
	3. Solve dispatch and compute locational marginal prices
	4. Save report.json with prices, generation, and feasibility checks

Solver Configuration:
	Use prob.solve(solver=cp.CLARABEL)
```

同时更新 `home.js` 中 compressionStates 的 retention 值保持不变（这些来自论文数据）。

---

## 5. P1-2: 清理 home.js 死代码

`home.js` line 12 引用了 `sectionIndicatorDots`，但 index.html 中已经没有 `.section-indicator__dot` 元素（已在上轮删除）。

**清理方案：**
- 删除 `var sectionIndicatorDots = ...` (line 12)
- 删除 `setActiveSectionIndicator` 函数 (约 line 143-153)
- 删除 `setupSectionIndicator` 函数 (约 line 155-188)
- 删除 `setupSectionIndicator()` 调用 (line 297)

---

## 6. P1-3: 更新 Tasks 页面来源标注

**当前问题：**
- `tasks.html` subtitle 说 "54 SkillsBench base tasks"
- `tasks.html` 有链接到 SkillsBench GitHub
- 实际 instruction 来自本地 TailSkills generated-tasks，不是 SkillsBench

**修复：** 更新 `tasks.html` line 41-42 的文案：
```html
<p class="page-subtitle">
  Explore 54 base tasks and 208 TailSkills exception-heavy variants. Each task links to its verified instruction from the TailSkills benchmark.
</p>
```

更新 `tasks.html` line 46 的按钮：
```html
<a class="button-link button-link--secondary" href="https://github.com/tailskill-bench/tailskill">TailSkills Source</a>
```

更新 `data/task-details.json` 中每个 task 的 `source_repository` 为 `"TailSkills"`。

---

## 7. P1-4: distillation-example.png 性能优化

**index.html line 150**: `distillation-example.png` (3115KB) 使用 `loading="eager"`

→ 改为 `loading="lazy"`

注意：首页 Benchmark section 修复后用的是 `benchmark-pipeline.png` (741KB)，这个可以用 `loading="eager"` 因为在 viewport 下方不远。

---

## 8. Git Commit 策略（3 步）

### Commit 1: 修复所有图片位置
```
fix: correct image placement across all pages

- index.html Benchmark: replace distillation-example.png with benchmark-pipeline.png
- experiments Introduction: replace distillation-example.png with benchmark-pipeline.png
- experiments Case Study: replace benchmark-pipeline.png with case-study-comparison.jpg
- experiments What Gets Erased: add distillation-example.png image
- experiments Main Results: remove misplaced case-study-comparison.jpg
- Fix all alt texts and captions to match actual image content
```

### Commit 2: 修复数据 + 清理代码
```
fix: complete missing task instructions and clean dead code

- Add instruction for gh-repo-analytics from local generated-tasks
- Add instruction for trend-anomaly-causal-inference from local generated-tasks
- Set instruction_available=true for both tasks
- Update source_repository to "TailSkills"
- Update tasks.html source attribution
- Remove dead section-indicator code from home.js
- Fix Skill Autopsy to use real skill text excerpt
```

### Commit 3: QA
```
fix: final QA - verify all images, links, and data

- Verify every image alt text matches image content
- Verify cross-page links work
- Verify dark mode on changed components
- Verify mobile layout
- git push origin gh-pages
```

---

## 9. 验证清单

完成后逐项检查：

- [ ] 首页 Introduction: `introduction-infographic.png` (竖图，传送带)
- [ ] 首页 Benchmark: `benchmark-pipeline.png` (宽图，构建流水线)
- [ ] experiments Introduction: `benchmark-pipeline.png` + `introduction-infographic.png`
- [ ] experiments Case Study: `case-study-comparison.jpg` (左右对比)
- [ ] experiments What Gets Erased: `distillation-example.png` (4 列 skill cards)
- [ ] experiments Main Results: `category-collapse-curves.jpg` (折线图)
- [ ] 每张图的 alt text 和 caption 都与图片真实内容匹配
- [ ] Tasks 页显示 54/54 tasks，全部有 instruction（不是 52）
- [ ] Skill Autopsy 使用真实 skill 文本
- [ ] home.js 没有 section-indicator 相关代码
- [ ] 所有修改在暗色模式下正常

---

## 10. 不要做的事

- ❌ 不要重新解释图片含义 — 本文档第 0 节是最终答案
- ❌ 不要编造任何数据
- ❌ 不要改 Chart.js 数据（已验证正确）
- ❌ 不要改 experiments.html 的表格数据
- ❌ 不要引入框架或 npm
- ❌ 不要切换分支

---

## 11. 立即开始

1. **完整阅读本文档** — `docs/iteration-5-fixes.md`
2. **阅读当前代码** — `index.html`, `experiments.html`, `static/js/home.js`, `data/task-details.json`
3. **用浏览器打开线上页面** — https://tailskill-bench.github.io/tailskill/ 对比当前图片和 caption，确认哪张图放错了
4. **读取本地 instruction** — `D:\temp\Tailskill_base\tailskills\generated-tasks\gh-repo-analytics--B1_readonly_output\instruction.md` 和 `trend-anomaly-causal-inference--A1_bom\instruction.md`
5. **按 3 步 commit 策略执行**
