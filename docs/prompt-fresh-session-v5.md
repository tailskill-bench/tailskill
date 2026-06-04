# TailSkills 网站修复 — 给新 Claude Code 会话的完整任务说明

---

## 第一步：了解这个项目

### 项目是什么

TailSkills 是一篇被 EMNLP 2026 接收的学术论文，标题是 "Focused but Fragile: Tail Knowledge Collapse in Recursive Agent Skill Distillation"。我们为这篇论文建了一个宣传网页（project page），用来展示论文的核心发现。

**论文核心发现：** 当 AI agent 的技能文档（skill）被递归压缩（S1→S2→S3→S4）时，常见的工作流程知识保持不变，但罕见的异常处理知识（"tail knowledge"）会逐渐消失。

**网站地址：** https://tailskill-bench.github.io/tailskill/
**代码仓库：** D:\codes\tailskill，分支 gh-pages
**技术栈：** 纯 HTML + CSS + JavaScript，无框架无 npm

### 网站有 4 个页面

1. **index.html** — 首页（Hero + Abstract + Introduction + Benchmark + Skill Autopsy + Explore + BibTeX）
2. **tasks.html** — 任务列表页（54 个 base task 卡片，可搜索/过滤）
3. **task.html** — 任务详情页（点击卡片跳转，显示 instruction、verifier 等）
4. **experiments.html** — 实验结果页（Chart.js 图表 + 数据表格 + ablation + case study）

---

## 第二步：了解网站是怎么建到现在的

### 第 1 轮（v1）：基础搭建
- Codex 搭建了单页应用，9 个 section，所有数据与论文一致

### 第 2 轮（v2）：多页架构
- 拆成 3 页，JS 拆分，添加 Skill Autopsy 滚动交互，缩小字体
- 填充了 208 个真实任务数据（tasks.json）

### 第 3 轮（v3）：首页增强
- 添加论文图预览、Autopsy 滚动增强、stat card 动画

### 第 4 轮（v4）：重大重构 ← 当前版本
- 首页参照 XSkill 学术页面重新设计（Abstract + Introduction 大图 + Benchmark）
- Tasks 页改为 SkillsBench 风格的 Task Registry，新增 task.html 详情页
- 移除了不可信的 S1-S4 实验结果展示

### v4 引入的问题（你的修复目标）

上一轮开发犯了一个严重错误：**把图片的含义搞混了，导致 5 张图中有 3 张放错了位置。**

具体来说：
- `distillation-example.png` 实际是"S1-S4 skill cards 对比图"，但被当成了"benchmark construction pipeline"
- `benchmark-pipeline.png` 实际是"benchmark 构建流程图"，但被当成了"case study comparison"
- `case-study-comparison.jpg` 实际是"Regular vs Tail-Aware 蒸馏对比"，但被当成了"collapse curve"

此外还有：2 个任务的 instruction 被误标为 missing、Autopsy 用了虚构文本、JS 里有死代码。

---

## 第三步：理解每张图片的真实内容

在改代码之前，你必须理解每张图片到底是什么。我逐张解释：

### 1. introduction-infographic.png（894KB，1000×1284，竖图）
**内容：** 一个像传送带一样的流程图。左侧是 S1（完整的 skill），向右经过 S2、S3、S4 逐步压缩。绿色部分（common workflow）在所有阶段都保留，粉色部分（tail exception handling）从 S3 开始消失。
**应该放在哪：** 首页 Introduction section ✅（当前正确）、experiments 页 Introduction section ✅（当前正确）

### 2. benchmark-pipeline.png（758KB，1960×1142，横图）
**内容：** TailSkills benchmark 的构建流程。从 26 个 base task 开始，经过 14 种 variant injection（6 个 category），到 oracle verification，最终产出 208 个 task variants。是一个从左到右的流程图。
**应该放在哪：** 首页 Benchmark section ❌（当前放的是 distillation-example.png）、experiments 页 Introduction section ❌（当前放的是 distillation-example.png）

### 3. distillation-example.png（3.2MB，7648×3419，超宽图）
**内容：** 四列并排的 skill cards。每列是一个 distillation depth（S1/S2/S3/S4），每列的 skill 文本用绿色标记 common 部分、粉色标记 tail 部分。可以看到粉色的 tail 部分从 S3 开始消失。
**应该放在哪：** experiments 页 "What Gets Erased" section ❌（当前只有文字面板，没有这张图）

### 4. case-study-comparison.jpg（132KB，2085×1280）
**内容：** 左右对比图。左边是 Regular distillation（丢掉了 C4 extreme value handling），右边是 Tail-Aware distillation（保留了 exception clause 并通过了验证）。
**应该放在哪：** experiments 页 Case Study section ❌（当前放的是 benchmark-pipeline.png）

### 5. category-collapse-curves.jpg（140KB，1950×1280）
**内容：** 6 条分类坍塌曲线（A/B/C/D/E/G），每条线显示该分类从 S1 到 S4 的 pass rate 变化。
**应该放在哪：** experiments 页 Main Results section ✅（当前正确）

---

## 第四步：执行修复

下面是详细的修复指令。请严格按照以下步骤执行。

### P0-1: 修复 experiments.html 图片位置

experiments.html 当前有 4 处图片位置需要修改。

#### 修改 1：Introduction section（约 line 48-53）

**当前代码（错误）：**
```html
<figure class="image-figure figure-showcase__item figure-showcase__item--wide">
  <div class="image-frame">
    <img src="static/images/distillation-example.png" alt="TailSkills benchmark construction pipeline from base task pool through tail variant taxonomy, task construction, oracle generation, and sandbox verification." width="7648" height="3419" loading="eager" decoding="async">
  </div>
  <figcaption>Benchmark construction pipeline: task-variant planning, tail injection, oracle and S1 generation, and sandbox verification.</figcaption>
</figure>
```

**替换为：**
```html
<figure class="image-figure figure-showcase__item figure-showcase__item--wide">
  <div class="image-frame">
    <img src="static/images/benchmark-pipeline.png" alt="TailSkills benchmark construction pipeline: 26 base tasks, 14 variant types across 6 categories, oracle verification, producing 208 task variants." width="1960" height="1142" loading="eager" decoding="async">
  </div>
  <figcaption>Benchmark construction pipeline: base tasks → variant injection → oracle verification → 208 task variants.</figcaption>
</figure>
```

注意：只替换这一处 figure。下面紧跟的 introduction-infographic.png figure 保持不动。

#### 修改 2：Main Results section（约 line 102-115）

**当前代码（错误）有两个 figure，第一个是 case-study-comparison.jpg：**
```html
<div class="figure-showcase figure-showcase--curves">
  <figure class="image-figure figure-showcase__item figure-showcase__item--wide">
    <div class="image-frame">
      <img src="static/images/case-study-comparison.jpg" ...>
    </div>
    <figcaption>Overall tail-collapse curve with confidence intervals.</figcaption>
  </figure>
  <figure class="image-figure figure-showcase__item figure-showcase__item--wide">
    <div class="image-frame">
      <img src="static/images/category-collapse-curves.jpg" ...>
    </div>
    <figcaption>Category-specific collapse patterns across distillation depth.</figcaption>
  </figure>
</div>
```

**替换为——删除第一个 figure，只保留 category-collapse-curves.jpg：**
```html
<div class="figure-showcase figure-showcase--curves">
  <figure class="image-figure figure-showcase__item figure-showcase__item--wide">
    <div class="image-frame">
      <img src="static/images/category-collapse-curves.jpg" alt="Category-specific tail collapse curves for encoding, file system, data quality, network, and dependency variants across distillation depth." width="1950" height="1280" loading="lazy" decoding="async">
    </div>
    <figcaption>Category-specific collapse patterns across distillation depth.</figcaption>
  </figure>
</div>
```

#### 修改 3：Case Study section（约 line 296-303）

**当前代码（错误）：**
```html
<figure class="image-figure case-figure">
  <div class="image-frame">
    <img src="static/images/benchmark-pipeline.png" alt="Regular distillation drops C4 extreme-value handling while tail-aware distillation preserves the recovery branch and passes verification." width="1960" height="1142" loading="eager" decoding="async">
  </div>
  <figcaption>
    A C4 tail variant exposes the difference between preserving the workflow and preserving the exception clause.
  </figcaption>
</figure>
```

**替换为：**
```html
<figure class="image-figure case-figure">
  <div class="image-frame">
    <img src="static/images/case-study-comparison.jpg" alt="Comparison of regular distillation (drops C4 extreme-value handling) versus tail-aware distillation (preserves exception clause), demonstrating why case-specific retention matters." width="2085" height="1280" loading="lazy" decoding="async">
  </div>
  <figcaption>
    Regular distillation drops C4 extreme-value handling while tail-aware distillation preserves the recovery branch and passes verification.
  </figcaption>
</figure>
```

#### 修改 4：What Gets Erased section（约 line 352-376）

**当前代码** 是一个纯文字面板 `<div class="erasure-panel">`，包含一段说明文字和列表。

**在 `<div class="erasure-panel">` 之前**，添加图片 figure：

```html
<figure class="image-figure" style="margin-bottom: 2rem;">
  <div class="image-frame">
    <img src="static/images/distillation-example.png" alt="S1 to S4 skill cards comparison: common-case workflow instructions in green persist across all depths while tail-case exception handling in pink progressively disappears at S3 and S4." width="7648" height="3419" loading="lazy" decoding="async">
  </div>
  <figcaption>Skill text at each distillation depth. Tail-handling knowledge (pink) disappears at S3 while common workflow (green) persists.</figcaption>
</figure>
```

保留原有的 `<div class="erasure-panel">` 文字面板不动，图片加在前面即可。

---

### P0-2: 修复 index.html Benchmark section 图片

index.html 约 line 148-155：

**当前代码（错误）：**
```html
<figure class="paper-figure paper-figure--wide">
  <a class="image-frame pipeline-figure" href="static/images/distillation-example.png" aria-label="Open benchmark construction figure at full size">
    <img src="static/images/distillation-example.png" alt="TailSkills benchmark construction pipeline: base tasks, variant taxonomy, task-variant planning, oracle generation, and sandbox verification." width="7648" height="3419" loading="eager" decoding="async">
  </a>
  <figcaption>
    Benchmark construction pipeline: 54 base tasks are transformed with 14 variant types across 6 tail categories, then admitted only after deterministic oracle verification.
  </figcaption>
</figure>
```

**替换为：**
```html
<figure class="paper-figure paper-figure--wide">
  <a class="image-frame pipeline-figure" href="static/images/benchmark-pipeline.png" aria-label="Open benchmark pipeline at full size">
    <img src="static/images/benchmark-pipeline.png" alt="TailSkills benchmark construction pipeline: 54 base tasks, 14 variant types across 6 categories, oracle verification, 208 task variants." width="1960" height="1142" loading="lazy" decoding="async">
  </a>
  <figcaption>
    Benchmark construction pipeline: 54 base tasks are transformed with 14 variant types across 6 tail categories, then admitted only after deterministic oracle verification.
  </figcaption>
</figure>
```

注意变化：
- 图片从 distillation-example.png（3.2MB, 7648×3419）换成 benchmark-pipeline.png（758KB, 1960×1142）
- loading 从 eager 改为 lazy
- href 链接也换成 benchmark-pipeline.png

---

### P0-3: 补全 2 个 missing task 的 instruction

在 D:\codes\tailskill 目录下运行：

```powershell
python -c "
import json, os
DETAILS = 'data/task-details.json'
GEN = r'D:\temp\Tailskill_base\tailskills\generated-tasks'
with open(DETAILS, 'r', encoding='utf-8') as f:
    data = json.load(f)
for task in data['tasks']:
    if task['id'] in ['gh-repo-analytics', 'trend-anomaly-causal-inference']:
        # Each base task has multiple variant directories, but they share the same instruction.md
        # We pick the first variant directory to get the base instruction
        dirs = sorted([d for d in os.listdir(GEN) if d.startswith(task['id'] + '--')])
        if dirs:
            path = os.path.join(GEN, dirs[0], 'instruction.md')
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                task['instruction'] = content
                task['instruction_available'] = True
                print(f'Updated {task[\"id\"]}: {len(content)} chars from {dirs[0]}')
with open(DETAILS, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print('Done. Verify: all 54 tasks now have instruction_available=True')
"
```

运行后，用以下命令验证：
```powershell
python -c "import json; d=json.load(open('data/task-details.json','r',encoding='utf-8')); print(f'Tasks: {len(d[\"tasks\"])}'); avail=sum(1 for t in d['tasks'] if t.get('instruction_available')); print(f'With instruction: {avail}')"
```

预期输出：`Tasks: 54` `With instruction: 54`

---

### P1-1: 用真实 skill 文本替换 Autopsy 虚构内容

index.html 约 line 221-241 是 Skill Autopsy 的 skill 文档区域。当前 `<pre><code>` 内的文本是编造的。

**真实 skill 文件位置：**
`D:\temp\Tailskill_base\tailskills\generated-tasks\energy-market-pricing--E1_missing_dep\environment\skills\s1\SKILL.md`

这个文件有 586 行。你需要从中选取有代表性的段落来展示"common workflow vs tail exception handling"的对比。

**具体做法：**

1. 读取 SKILL.md 全文
2. 从中选取约 15-20 行有代表性的内容，包含：
   - **Common workflow 部分**（不加标记）：如主流程步骤、数据处理、公式说明
   - **Tail exception handling 部分**（用 `<span class="tail-text">` 包裹）：如依赖安装失败的处理、错误恢复指令、防御性检查

**Tail 知识的判断标准**——以下模式属于 tail knowledge，需要用 `<span class="tail-text">` 包裹：
- `If you encounter ...` / `If ... is unavailable` — 条件性错误处理
- `Reinstall ...` / `fallback` / `fall back` — 恢复/回退指令
- `when ... is missing` / `check ... if needed` — 防御性检查
- `ModuleNotFoundError` — 具体错误类型的处理

**Common 知识的判断标准**——以下属于 common workflow，不加标记：
- `pip install ...` — 正常安装步骤
- `Load ... and validate ...` — 标准数据处理
- `Solve ... and calculate ...` — 核心算法步骤
- `Save ... with ...` — 标准输出步骤

**示例替换内容（你可以直接使用）：**

```html
<pre><code>## Dependencies
pip3 install numpy==1.26.4 scipy==1.11.4 cvxpy==1.4.2
<span class="tail-text">If you encounter a ModuleNotFoundError: No module named 'cvxpy',
the package may have been removed from the environment.
Reinstall it with:
pip3 install --no-cache-dir cvxpy==1.4.2</span>

## Market Clearing
1. Load network.json and validate buses, generators, and demand
2. Formulate DC-OPF objective with quadratic generator costs
3. Solve dispatch and extract locational marginal prices
4. Save report.json with prices, generation, and reserve margins

## Solver Selection
Use prob.solve(solver=cp.CLARABEL) for quadratic costs
<span class="tail-text">Quick file size check (if needed):
wc -l network.json   # Line count
du -h network.json   # File size</span></code></pre>
```

**关键约束：**
- 保持 `energy-market-pricing / E1 missing dependency` 的标题不变
- `<span class="tail-text">` 标记的行在 Autopsy 滚动时会逐渐模糊/消失（这是已有的 CSS 动画）
- 内容必须来自真实 SKILL.md，不能编造

---

### P1-2: 删除 home.js 中的死代码

`static/js/home.js` 引用了已从 HTML 中移除的 section indicator dots。需要删除：

1. **约 line 12**：`var sectionIndicatorDots = document.querySelectorAll('.section-indicator__dot');` — 删除这一行
2. **约 line 143-188**：`setActiveSectionIndicator()` 和 `setupSectionIndicator()` 两个函数 — 整段删除（约 46 行）
3. **约 line 296**：`setupSectionIndicator();` — 删除这个调用

判断方法：搜索 `sectionIndicatorDots` 和 `setupSectionIndicator`，删除所有包含这两个名称的行。

---

### P1-3: 改大图为 lazy loading

在 index.html 中：
- 约 line 117 的 `loading="eager"` → `loading="lazy"`（Introduction infographic）
- 注意：P0-2 已经把 Benchmark 图片改为 lazy 了

在 experiments.html 中：
- 修改 3 已经把 Case Study 图片改为 lazy
- 修改 2 已经把 Main Results 图片改为 lazy
- 修改 4 已经把 What Gets Erased 图片改为 lazy
- Introduction section 的两张图保持 `loading="eager"`（首屏可见，需要快速加载）

---

## 第五步：Git Commit 策略

```powershell
cd D:\codes\tailskill
```

3 个 commit：

```powershell
# Commit 1: 图片修复（P0-1 + P0-2 + P1-3）
git add -A
git commit -m "fix: correct image placement — swap 3 misplaced figures across homepage and experiments"
git push origin gh-pages

# Commit 2: 数据修复（P0-3）
git add -A
git commit -m "fix: add missing task instructions for gh-repo-analytics and trend-anomaly-causal-inference"
git push origin gh-pages

# Commit 3: 代码质量（P1-1 + P1-2）
git add -A
git commit -m "fix: use real skill text in autopsy, remove dead code in home.js"
git push origin gh-pages
```

---

## 第六步：验证

每次 push 后等 1-2 分钟，然后检查：

- [ ] 首页 Benchmark section：应该看到横版的 pipeline 流程图（有 base tasks → variants → oracle 的流程）
- [ ] 首页 Introduction section：应该看到竖版的传送带图（S1→S4 压缩过程）✅ 不改
- [ ] Experiments Introduction：pipeline 流程图 + 传送带图
- [ ] Experiments Main Results：只有分类坍塌曲线图（case-study-comparison 已移走）
- [ ] Experiments Case Study：Regular vs Tail-Aware 对比图
- [ ] Experiments What Gets Erased：S1-S4 四列 skill cards 对比图
- [ ] 所有图片的 alt text 与图片真实内容一致
- [ ] Tasks 页 54 张卡片，点击 `gh-repo-analytics` 和 `trend-anomaly-causal-inference` 能看到 instruction
- [ ] Skill Autopsy 显示真实 skill 文本（包含 `<span class="tail-text">` 标记）
- [ ] 浏览器控制台无 JS 错误（home.js 死代码已删除）
- [ ] 暗色模式、移动端正常

---

## 关键约束

- **不要改** experiments.html 中的 Chart.js 图表数据（已验证正确）
- **不要改** experiments.html 中的表格数据（已验证正确）
- **不要编造**任何数据
- **不要创建**新的动画或交互
- **不要引入** npm/框架
- **当前分支**是 gh-pages，不要切换
- **字体**: Instrument Serif + DM Sans + JetBrains Mono
- **亮色默认** #fafaf8
- **颜色**: tail accent #E2ABB8, common accent #B2D9B3

---

## 立即开始

1. 读 `index.html` — 理解首页结构，定位 line 148-155（Benchmark 图片）和 line 221-241（Autopsy 文本）
2. 读 `experiments.html` — 理解实验页结构，定位 4 处需要修改的图片
3. 读 `static/js/home.js` — 找到 `sectionIndicatorDots` 和 `setupSectionIndicator` 相关的死代码
4. 按 P0-1 → P0-2 → P0-3 → P1-1 → P1-2 → P1-3 顺序执行修复
5. 每个 commit 后 push 并验证
