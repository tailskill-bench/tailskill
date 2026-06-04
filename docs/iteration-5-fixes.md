# TailSkills 网站修复任务 — v5

> 本文档是一个新 Claude Code 会话的完整任务描述。
> 分支: gh-pages | 项目: D:\codes\tailskill
> 线上: https://tailskill-bench.github.io/tailskill/

---

## 你的任务

修复上一轮开发中引入的错误。主要问题是**图片放错了位置**和一些数据/代码问题。
按优先级执行 P0 → P1，每完成一组 commit + push。

**先完整阅读本文档，再开始改代码。不要跳过任何步骤。**

---

## P0: 图片语义修复（必须修）

### 问题说明

上一轮开发把图片的含义搞混了。5 张图中有 3 张放错了位置。

**每张图片的真实内容（不要搞混）：**

| 文件 | 真实内容 | 尺寸 |
|------|----------|------|
| `introduction-infographic.png` | Skill Distillation 传送带图：S1→S2→S3→S4 压缩过程，绿色 common 保留，粉色 tail 消失 | 1000×1284 (竖图) |
| `benchmark-pipeline.png` | TailSkills Benchmark 构建流程：base task → variant injection → oracle verification → 208 tasks | 1960×1142 (横图) |
| `distillation-example.png` | S1-S4 Skill Cards 并排对比：4 列，每列是一个 generation 的 skill 文本，粉色部分逐步消失 | 7648×3419 (超宽图) |
| `case-study-comparison.jpg` | Regular vs Tail-Aware 蒸馏策略对比：同一个 C4 task 两种策略不同结果 | 2085×1280 |
| `category-collapse-curves.jpg` | 6 个分类的坍塌曲线图 | 1950×1280 |

### P0-1: 修复 experiments.html 图片位置

**当前错误 → 正确映射：**

```
Introduction section (line 48-53):
  当前: distillation-example.png ← 错！
  改为: benchmark-pipeline.png

Introduction section (line 54-61):
  当前: introduction-infographic.png ← 对 ✅，保留不动

Main Results section (line 102-115):
  当前: case-study-comparison.jpg ← 错！这图是 case study 对比不是 collapse curve
  改为: 移除 case-study-comparison.jpg，只保留 category-collapse-curves.jpg

Case Study section (line 298):
  当前: benchmark-pipeline.png ← 错！这图是 pipeline 不是 case study
  改为: case-study-comparison.jpg

What Gets Erased section (line 352-357):
  当前: 只有文字面板，没有图片
  改为: 添加 distillation-example.png 图片展示
```

**具体操作：**

1. experiments.html line 50：把 `distillation-example.png` 改为 `benchmark-pipeline.png`，同时更新 alt text：
   ```html
   <img src="static/images/benchmark-pipeline.png" alt="TailSkills benchmark construction pipeline: 26 base tasks, 14 variant types across 6 categories, oracle verification, producing 208 task variants." width="1960" height="1142" loading="lazy" decoding="async">
   ```
   figcaption 改为: `Benchmark construction pipeline: base tasks → variant injection → oracle verification → 208 task variants.`

2. experiments.html line 105-108：把 `case-study-comparison.jpg` 的 figure 移到 Case Study section，Main Results 只保留 `category-collapse-curves.jpg`

3. experiments.html Case Study section（大约 line 298）：把 `benchmark-pipeline.png` 替换为 `case-study-comparison.jpg`，更新 alt text：
   ```html
   <img src="static/images/case-study-comparison.jpg" alt="Comparison of regular distillation (drops C4 extreme value handling) vs tail-aware distillation (preserves exception clause), showing why case-specific retention matters." width="2085" height="1280" loading="lazy" decoding="async">
   ```

4. experiments.html "What Gets Erased" section：添加 `distillation-example.png` 图片：
   ```html
   <figure class="image-figure wide-paper-figure">
     <div class="image-frame">
       <img src="static/images/distillation-example.png" alt="S1 to S4 skill cards comparison: common-case workflow instructions (green) persist across all depths while tail-case exception handling (pink) progressively disappears at S3 and S4." width="7648" height="3419" loading="lazy" decoding="async">
     </div>
     <figcaption>
       Skill text at each distillation depth. Tail-handling knowledge (pink) disappears at S3 while common workflow (green) persists.
     </figcaption>
   </figure>
   ```

### P0-2: 修复 index.html Benchmark section 图片

index.html line 149-150：把 `distillation-example.png` 改为 `benchmark-pipeline.png`：

```html
<a class="image-frame pipeline-figure" href="static/images/benchmark-pipeline.png" aria-label="Open benchmark pipeline at full size">
  <img src="static/images/benchmark-pipeline.png" alt="TailSkills benchmark construction pipeline: 26 base tasks, 14 variant types across 6 categories, oracle verification, producing 208 task variants." width="1960" height="1142" loading="lazy" decoding="async">
</a>
```

figcaption 更新为：`Benchmark construction pipeline: base tasks → variant injection → oracle verification → 208 task variants.`

### P0-3: 补全 2 个 missing task 的 instruction

`data/task-details.json` 中 `gh-repo-analytics` 和 `trend-anomaly-causal-inference` 被标记为 instruction 不可用，但它们在本地 generated-tasks 中存在。

运行以下命令提取真实 instruction 并更新 task-details.json：

```bash
cd D:\codes\tailskill
python -c "
import json, os, re

DETAILS_FILE = 'data/task-details.json'
GEN_DIR = 'D:/temp/Tailskill_base/tailskills/generated-tasks'

with open(DETAILS_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

missing_ids = ['gh-repo-analytics', 'trend-anomaly-causal-inference']

for task in data['tasks']:
    if task['id'] in missing_ids:
        # Find any variant directory for this task
        dirs = [d for d in os.listdir(GEN_DIR) if d.startswith(task['id'] + '--')]
        if dirs:
            inst_path = os.path.join(GEN_DIR, dirs[0], 'instruction.md')
            if os.path.exists(inst_path):
                with open(inst_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                task['instruction'] = content
                task['instruction_available'] = True
                print(f'Updated {task[\"id\"]}: {len(content)} chars from {dirs[0]}')
            else:
                print(f'No instruction.md in {dirs[0]}')
        else:
            print(f'No directory for {task[\"id\"]}')

with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print('Done')
"
```

---

## P1: 代码质量修复

### P1-1: 用真实 skill 文本替换 Autopsy 虚构内容

index.html line 226-240 的 skill 文本是编造的。替换为真实 SKILL.md 内容。

本地真实 skill 文件位置：
`D:\temp\Tailskill_base\tailskills\generated-tasks\energy-market-pricing--E1_missing_dep\environment\skills\s1\SKILL.md`

把这个文件的前 30 行提取出来，放入 index.html 的 `<pre><code>` 中作为 autopsy 展示文本。

用以下命令提取：
```bash
head -30 "D:/temp/Tailskill_base/tailskills/generated-tasks/energy-market-pricing--E1_missing_dep/environment/skills/s1/SKILL.md"
```

然后用提取到的真实文本替换 index.html 中的虚构文本。

**注意：** 真实 skill 中需要手动标记哪些行是 "tail" 内容。在 skill 文本中，以下类型的行应该用 `<span class="tail-text">` 包裹：
- 关于 fallback 的说明（如 "if unavailable", "fallback", "recover"）
- 关于错误处理的说明（如 "If ModuleNotFoundError", "catch"）
- 关于诊断/调试的说明（如 "diagnostic note", "debug"）

其他内容（主要工作流程、依赖安装、求解器配置）保持不变。

### P1-2: 删除 home.js 中的死代码

`static/js/home.js` 中以下代码引用了不存在的 DOM 元素（section indicator dots 已从 HTML 中移除）：

- Line 12: `var sectionIndicatorDots = document.querySelectorAll(".section-indicator__dot");`
- Lines 143-188: 整个 `setActiveSectionIndicator()` 和 `setupSectionIndicator()` 函数
- Line 296: `setupSectionIndicator();` 调用

删除这 3 处代码。

### P1-3: 大图改为 lazy loading

index.html line 117 和 line 150 的图片用了 `loading="eager"`。改为 `loading="lazy"`：

```html
<!-- line 117 -->
<img src="static/images/introduction-infographic.png" ... loading="lazy" ...>

<!-- line 150 (修改后是 benchmark-pipeline.png) -->
<img src="static/images/benchmark-pipeline.png" ... loading="lazy" ...>
```

---

## Git Commit 策略（3 步）

### Commit 1: P0 图片修复
```bash
cd D:\codes\tailskill
git add -A
git commit -m "fix: correct image placement across homepage and experiments page

- index.html: Benchmark section now uses benchmark-pipeline.png instead of distillation-example.png
- experiments.html: Introduction uses benchmark-pipeline.png, Case Study uses case-study-comparison.jpg
- experiments.html: What Gets Erased now shows distillation-example.png
- experiments.html: Main Results shows category-collapse-curves.jpg only
- All alt texts updated to match actual image content
- Large images changed to loading=lazy"
git push origin gh-pages
```

### Commit 2: P0 数据修复
```bash
git add -A
git commit -m "fix: add missing task instructions for gh-repo-analytics and trend-anomaly-causal-inference

- Instructions sourced from local generated-tasks directory
- task-details.json updated: 54/54 tasks now have instructions"
git push origin gh-pages
```

### Commit 3: P1 代码质量
```bash
git add -A
git commit -m "fix: replace fabricated autopsy text with real SKILL.md content and remove dead code

- index.html: Skill Autopsy now uses real skill text from energy-market-pricing E1 variant
- home.js: Remove dead section-indicator code (46 lines)
- index.html: Change large images from loading=eager to loading=lazy"
git push origin gh-pages
```

---

## 验证清单

每次 push 后等 1-2 分钟，然后在浏览器中验证：

- [ ] 首页 Benchmark section 显示的是 pipeline 流程图（不是 skill cards）
- [ ] 首页 Introduction section 显示的是 distillation 传送带图 ✅（已正确）
- [ ] Experiments Introduction section 显示 benchmark-pipeline + introduction-infographic
- [ ] Experiments Case Study section 显示 Regular vs Tail-Aware 对比图
- [ ] Experiments "What Gets Erased" section 显示 S1-S4 skill cards 对比图
- [ ] Experiments Main Results section 显示分类坍塌曲线图
- [ ] 所有图片的 alt text 与图片真实内容一致
- [ ] Tasks 页面 54 张卡片都能显示，点击能进入详情
- [ ] `gh-repo-analytics` 和 `trend-anomaly-causal-inference` 详情页能显示 instruction
- [ ] Skill Autopsy 显示真实 skill 文本（不是虚构的）
- [ ] 暗色模式下所有组件正确显示
- [ ] 移动端（375px）布局正常，无横向溢出

---

## 不要做的事

- ❌ 不要改 experiments.html 中的 Chart.js 数据（已验证正确）
- ❌ 不要改 experiments.html 中的表格数据（已验证正确）
- ❌ 不要创建新的动画或交互特效
- ❌ 不要编造任何数据
- ❌ 不要切换分支
- ❌ 不要引入 npm/框架

---

## 关键约束

- 纯 HTML/CSS/JS
- 字体: Instrument Serif + DM Sans + JetBrains Mono
- 亮色默认 #fafaf8
- Tail accent: #E2ABB8, Common accent: #B2D9B3
- 本地 generated-tasks 路径: `D:\temp\Tailskill_base\tailskills\generated-tasks\`
