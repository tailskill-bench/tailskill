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

详细的修复步骤写在 `docs/iteration-5-fixes.md` 里。请先读那个文件，然后按 P0 → P1 顺序执行。

### P0 修复（最高优先级，影响展示正确性）

**P0-1: 修复 experiments.html 图片位置**

需要做以下交换：
1. Introduction section：`distillation-example.png` → `benchmark-pipeline.png`（行 50）
2. Main Results section：移除 `case-study-comparison.jpg`，只保留 `category-collapse-curves.jpg`（行 102-115）
3. Case Study section：`benchmark-pipeline.png` → `case-study-comparison.jpg`（行 298）
4. What Gets Erased section：添加 `distillation-example.png` 图片（行 352 后面）

每次交换图片时，必须同时更新 alt text 和 figcaption，使其描述图片的真实内容。

**P0-2: 修复 index.html Benchmark section**

index.html 行 149-150：`distillation-example.png` → `benchmark-pipeline.png`，更新 alt text 和 figcaption。

**P0-3: 补全 2 个 missing task 的 instruction**

运行以下命令（在 D:\codes\tailskill 目录下）：

```
python -c "
import json, os
DETAILS = 'data/task-details.json'
GEN = 'D:/temp/Tailskill_base/tailskills/generated-tasks'
with open(DETAILS, 'r', encoding='utf-8') as f:
    data = json.load(f)
for task in data['tasks']:
    if task['id'] in ['gh-repo-analytics', 'trend-anomaly-causal-inference']:
        dirs = [d for d in os.listdir(GEN) if d.startswith(task['id'] + '--')]
        if dirs:
            path = os.path.join(GEN, dirs[0], 'instruction.md')
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    task['instruction'] = f.read().strip()
                task['instruction_available'] = True
                print(f'Updated {task[\"id\"]}')
with open(DETAILS, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
"
```

### P1 修复（提升质量）

**P1-1: 用真实 skill 文本替换 Autopsy 虚构内容**

index.html 行 226-240 的 skill 文本是编造的。真实 skill 在：
`D:\temp\Tailskill_base\tailskills\generated-tasks\energy-market-pricing--E1_missing_dep\environment\skills\s1\SKILL.md`

读取这个文件的前 30 行，替换 index.html 中的虚构文本。用 `<span class="tail-text">` 标记以下类型的行：
- 关于 fallback/备用方案的说明
- 关于错误处理的说明
- 关于诊断/调试的说明

**P1-2: 删除 home.js 中的死代码**

`static/js/home.js` 引用了已从 HTML 中移除的 section indicator dots：
- 行 12: `var sectionIndicatorDots = ...` — 删除
- 行 143-188: `setActiveSectionIndicator()` 和 `setupSectionIndicator()` 函数 — 整段删除
- 行 296: `setupSectionIndicator();` — 删除调用

**P1-3: 大图改为 lazy loading**

index.html 行 117 和 150 的 `loading="eager"` 改为 `loading="lazy"`。

---

## 第五步：Git Commit 策略

```bash
cd D:\codes\tailskill
```

3 个 commit：

```
# Commit 1: 图片修复
git add -A
git commit -m "fix: correct image placement — swap 3 misplaced figures across homepage and experiments"
git push origin gh-pages

# Commit 2: 数据修复
git add -A
git commit -m "fix: add missing task instructions for gh-repo-analytics and trend-anomaly-causal-inference"
git push origin gh-pages

# Commit 3: 代码质量
git add -A
git commit -m "fix: use real skill text in autopsy, remove dead code, lazy-load large images"
git push origin gh-pages
```

---

## 第六步：验证

每次 push 后等 1-2 分钟，然后检查：

- [ ] 首页 Benchmark section：应该看到横版的 pipeline 流程图（有 26 base tasks → variants → oracle 的流程）
- [ ] 首页 Introduction section：应该看到竖版的传送带图（S1→S4 压缩过程）✅ 不改
- [ ] Experiments Introduction：pipeline 流程图 + 传送带图
- [ ] Experiments Case Study：Regular vs Tail-Aware 对比图
- [ ] Experiments What Gets Erased：S1-S4 四列 skill cards 对比图
- [ ] Experiments Main Results：分类坍塌曲线图
- [ ] 所有图片的 alt text 与图片真实内容一致
- [ ] Tasks 页 54 张卡片，点击 `gh-repo-analytics` 和 `trend-anomaly-causal-inference` 能看到 instruction
- [ ] Skill Autopsy 显示真实 skill 文本
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

1. 读 `docs/iteration-5-fixes.md` — 详细的修复规格
2. 读 `index.html` — 理解首页结构
3. 读 `experiments.html` — 理解实验页结构和当前图片位置
4. 读 `static/js/home.js` — 找到要删除的死代码
5. 按 P0 → P1 顺序执行修复
6. 每个 commit 后 push 并验证
