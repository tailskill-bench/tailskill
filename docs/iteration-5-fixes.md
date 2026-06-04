# TailSkills 网站修复 — 补充修复规格

> ⚠️ **主文档是 `prompt-fresh-session-v5.md`**，那份文档包含完整的项目介绍、图片语义说明、修复步骤和验证清单。
> 本文件是补充参考，提供了一些额外的代码片段模板。如果两份文档有冲突，以 `prompt-fresh-session-v5.md` 为准。

---

## 项目背景

**TailSkills** 是一篇 EMNLP 2026 的学术论文，研究 AI agent 的"技能蒸馏"问题。
当人类写的 agent 技能（S1, ~8000 字符）被递归压缩成更短版本（S2 ~5600, S3 ~3900, S4 ~2700 字符）时，
常见的操作流程知识被保留，但罕见的异常处理知识（"tail knowledge"）会逐渐丢失。
论文提出了 TailSkills 基准测试，包含 208 个经过 oracle 验证的任务变体，14 种变体类型，6 个分类。

**论文标题：** "Focused but Fragile: Tail Knowledge Collapse in Recursive Agent Skill Distillation"
**组织：** tailskill-bench | **仓库：** tailskill | **分支：** gh-pages

## 网站简介

我们为这篇论文建了一个学术项目展示网页，类似 XSkill (https://xskill-agent.github.io/xskill_page) 那种论文配套网页。

**技术栈：** 纯 HTML5 + CSS3 + vanilla JavaScript。无框架、无 npm、无构建工具。
**字体：** Instrument Serif（标题）+ DM Sans（正文）+ JetBrains Mono（代码）
**Chart.js 4.x CDN** 仅在 experiments 页面使用。
**部署：** GitHub Pages，从 gh-pages 分支自动部署。
**线上地址：** https://tailskill-bench.github.io/tailskill/

**网站有 4 个页面：**
1. **index.html** — 首页，有 Hero（压缩滑块交互）、Abstract、Introduction、Benchmark、Skill Autopsy（滚动动画）、Explore 卡片、BibTeX
2. **tasks.html** — Task Registry，54 个 base task 卡片，搜索/过滤，类似 SkillsBench
3. **task.html** — Task 详情页，显示 instruction、verifier、results（不可用）、trajectory（不可用）
4. **experiments.html** — 实验结果页，Chart.js 图表、数据表格、Ablation、Case Study

## 前四轮开发历史

**Round 1：** Codex 搭建了初始单页网站，9 个 section，所有数据与论文一致。

**Round 2：** 单页 → 三页架构（index + tasks + experiments），JS 拆分为 4 个文件，缩小标题字体。

**Round 3：** 修复 tasks.js bug，增强 Autopsy 滚动效果，添加图片预览 gallery。

**Round 4（最近一轮）：** 重大重构——
- 首页改为学术 paper page 风格（参照 XSkill），新增 Abstract、Introduction 大图、Benchmark 大图
- Tasks 页改为 Task Registry 风格（参照 SkillsBench），新增 task.html 详情页
- 移除了错误的 S1-S4 PASS/FAIL 实验结果数据
- 添加 task-details.json，52 个 task 有 source-backed instructions

**但是！Round 4 引入了严重问题：**

1. **图片放错位置** — 开发者不理解每张图片的实际内容，把 3 张图放到了错误的 section
2. **2 个 task 被误标为 missing** — 实际本地有 instruction
3. **Skill Autopsy 用了虚构文本** — 应该用真实 skill 文件内容
4. **home.js 有死代码** — 引用已删除的 DOM 元素

---

## 你的任务：修复 Round 4 的问题

读取详细任务文档 `docs/iteration-5-fixes.md`，按 P0 → P1 顺序执行。
每个 P0/P1 完成后 commit + push。

### 图片内容说明（最重要——理解每张图是什么）

项目目录 `static/images/` 有 5 张图片。你无法看到图片内容，所以必须通过下面的描述理解：

| 文件名 | 图片实际内容 | 图片特征 |
|--------|-------------|----------|
| `introduction-infographic.png` | **Skill Distillation 流程图**。展示 S1→S2→S3→S4 的压缩过程，像一个传送带。绿色部分（common workflow）保持不变，粉色部分（tail exception handling）逐渐消失。 | 竖图 1000×1284 |
| `benchmark-pipeline.png` | **TailSkills Benchmark 构建流程**。展示完整的 pipeline：26 个 base task → 14 种 variant injection → oracle verification → 最终 208 个任务。有多个步骤节点和箭头。 | 横图 1960×1142 |
| `distillation-example.png` | **S1-S4 Skill Cards 并排对比**。4 列并排，每列是一个 generation 的 skill 文本。绿色高亮 common 部分，粉色高亮 tail 部分。可以看到粉色部分从 S3 开始消失。这是"What Gets Erased"的视觉证据。 | 超宽图 7648×3419，3.2MB |
| `case-study-comparison.jpg` | **Regular vs Tail-Aware 蒸馏对比**。左右两栏，展示同一个 C4 极值任务在两种蒸馏策略下的不同表现。Regular 策略丢失了极值处理，Tail-Aware 保留了。 | 横图 2085×1280 |
| `category-collapse-curves.jpg` | **6 个分类的坍塌曲线**。6 条折线，每条代表一个 variant category（A-G）在不同压缩深度下的 pass rate 变化。 | 横图 1950×1280 |

### 当前图片位置（有错）

**experiments.html 当前图片位置：**
```
Introduction section → distillation-example.png ❌（应该是 benchmark-pipeline.png）
                  → introduction-infographic.png ✅
Main Results section → case-study-comparison.jpg ❌（应该是 category-collapse-curves.jpg only）
                    → category-collapse-curves.jpg ✅
Case Study section → benchmark-pipeline.png ❌（应该是 case-study-comparison.jpg）
What Gets Erased → 只有文字，没有图片 ❌（应该是 distillation-example.png）
```

**index.html 当前图片位置：**
```
Introduction section → introduction-infographic.png ✅
Benchmark section → distillation-example.png ❌（应该是 benchmark-pipeline.png）
```

### 正确的图片位置（修复目标）

**experiments.html：**
```
Introduction section → benchmark-pipeline.png + introduction-infographic.png
Main Results section → category-collapse-curves.jpg（移除 case-study-comparison.jpg）
Case Study section → case-study-comparison.jpg
What Gets Erased → distillation-example.png
```

**index.html：**
```
Introduction section → introduction-infographic.png ✅ 不改
Benchmark section → benchmark-pipeline.png（替换 distillation-example.png）
```

---

## 具体修复步骤

### Step 1: 修复 experiments.html 图片（P0）

逐个替换图片 src 和 alt text：

1. **Line ~50**：`distillation-example.png` → `benchmark-pipeline.png`
   - alt: `"TailSkills benchmark construction pipeline: 26 base tasks, 14 variant types across 6 categories, oracle verification, producing 208 task variants."`
   - width/height: 1960/1142
   - figcaption: `"Benchmark construction pipeline: base tasks → variant injection → oracle verification → 208 task variants."`

2. **Line ~105**：移除 `case-study-comparison.jpg` 的整个 `<figure>` 块。Main Results 只保留 `category-collapse-curves.jpg`。

3. **Line ~298** Case Study section：`benchmark-pipeline.png` → `case-study-comparison.jpg`
   - alt: `"Comparison of regular distillation (drops C4 extreme value handling) vs tail-aware distillation (preserves exception clause), showing why case-specific retention matters."`
   - width/height: 2085/1280

4. **"What Gets Erased" section**：添加 `distillation-example.png` 图片（当前只有文字面板）
   - alt: `"S1 to S4 skill cards comparison: common-case workflow instructions (green) persist across all depths while tail-case exception handling (pink) progressively disappears at S3 and S4."`
   - width/height: 7648/3419
   - loading: lazy
   - figcaption: `"Skill text at each distillation depth. Tail-handling knowledge (pink) disappears at S3 while common workflow (green) persists."`

### Step 2: 修复 index.html Benchmark 图片（P0）

index.html 约 line 149-150：`distillation-example.png` → `benchmark-pipeline.png`

```html
<a class="image-frame pipeline-figure" href="static/images/benchmark-pipeline.png" aria-label="Open benchmark pipeline at full size">
  <img src="static/images/benchmark-pipeline.png" alt="TailSkills benchmark construction pipeline: 26 base tasks, 14 variant types, oracle verification, 208 task variants." width="1960" height="1142" loading="lazy" decoding="async">
</a>
```

figcaption: `"Benchmark construction pipeline: base tasks → variant injection → oracle verification → 208 task variants."`

### Step 3: 补全 missing task instructions（P0）

运行 python 脚本从本地 generated-tasks 提取 instruction：

```bash
cd D:\codes\tailskill
python -c "
import json, os
DETAILS_FILE = 'data/task-details.json'
GEN_DIR = 'D:/temp/Tailskill_base/tailskills/generated-tasks'
with open(DETAILS_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)
missing_ids = ['gh-repo-analytics', 'trend-anomaly-causal-inference']
for task in data['tasks']:
    if task['id'] in missing_ids:
        dirs = [d for d in os.listdir(GEN_DIR) if d.startswith(task['id'] + '--')]
        if dirs:
            inst_path = os.path.join(GEN_DIR, dirs[0], 'instruction.md')
            if os.path.exists(inst_path):
                with open(inst_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                task['instruction'] = content
                task['instruction_available'] = True
                print(f'Updated {task[\"id\"]}: {len(content)} chars')
with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print('Done')
"
```

### Step 4: 替换 Autopsy 虚构文本（P1）

从真实 SKILL.md 提取内容：

```bash
head -30 "D:/temp/Tailskill_base/tailskills/generated-tasks/energy-market-pricing--E1_missing_dep/environment/skills/s1/SKILL.md"
```

把输出的真实 skill 文本替换 index.html 中 `<pre><code>` 内的虚构文本（约 line 226-240）。

将真实文本中涉及 fallback/recovery/error-handling 的行用 `<span class="tail-text">...</span>` 包裹，其他保持不变。

### Step 5: 删除 home.js 死代码（P1）

`static/js/home.js` 中：
- Line 12: 删除 `var sectionIndicatorDots = ...`
- Lines 143-188: 删除 `setActiveSectionIndicator()` 和 `setupSectionIndicator()` 两个函数
- Line 296: 删除 `setupSectionIndicator();` 调用

### Step 6: 改 loading=eager 为 lazy（P1）

index.html 中所有 `<img>` 标签的 `loading="eager"` 改为 `loading="lazy"`。

---

## Git Commit 策略

```bash
cd D:\codes\tailskill

# Commit 1: 图片修复
git add -A
git commit -m "fix: correct image placement across homepage and experiments page"
git push origin gh-pages

# Commit 2: 数据修复
git add -A
git commit -m "fix: add missing task instructions from local generated-tasks"
git push origin gh-pages

# Commit 3: 代码质量
git add -A
git commit -m "fix: real autopsy text, remove dead code, lazy loading"
git push origin gh-pages
```

---

## 验证清单

每次 push 后等 1-2 分钟，浏览器验证：
- [ ] 首页 Benchmark 显示 pipeline 流程图（不是 skill cards）
- [ ] Experiments Introduction 显示 pipeline + infographic
- [ ] Experiments Case Study 显示 Regular vs Tail-Aware 对比
- [ ] Experiments "What Gets Erased" 显示 S1-S4 skill cards
- [ ] 所有图片 alt text 与内容一致
- [ ] Tasks 页 54 张卡片，点击进详情有 instruction
- [ ] Skill Autopsy 显示真实 skill 文本
- [ ] 暗色模式 + 移动端正常

## 不要做的事

- ❌ 不要改 Chart.js 数据或表格数据
- ❌ 不要创建新动画/特效
- ❌ 不要编造数据
- ❌ 不要切换分支
- ❌ 不要引入 npm/框架
