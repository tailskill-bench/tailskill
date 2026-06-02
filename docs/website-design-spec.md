# TailSkills Project Webpage — Design Specification

> **Status**: Ready for Development | **Target**: tailskill-bench.github.io/tailskill
> **Paper**: "Focused but Fragile: Tail Knowledge Collapse in Recursive Agent Skill Distillation" (EMNLP 2026)
> **Project Root**: `D:\codes\tailskill\`

---

## 0. Codex Development Workflow

### Git Commit Strategy

This project is developed via Codex (or similar AI coding agent). Follow incremental commit discipline:

| Commit Point | When | Message Pattern |
|-------------|------|-----------------|
| Commit 1 | HTML skeleton with all 9 sections (empty content) | `feat: scaffold index.html with 9 sections` |
| Commit 2 | CSS variables, base layout, typography, theme toggle | `feat: add base CSS with light/dark theming` |
| Commit 3 | Hero section complete (title + compression slider JS) | `feat: implement hero compression slider interaction` |
| Commit 4 | Abstract + Introduction sections with images | `feat: add abstract and introduction sections` |
| Commit 5 | Benchmark taxonomy cards (interactive expand) | `feat: add benchmark overview with taxonomy cards` |
| Commit 6 | Main Results (Chart.js charts + data table) | `feat: add interactive main results charts and table` |
| Commit 7 | Ablation section (retention chart + findings) | `feat: add ablation studies with retention analysis` |
| Commit 8 | Case Study section | `feat: add case study comparison section` |
| Commit 9 | Task Gallery (filter/search + cards) | `feat: add task gallery with filters and search` |
| Commit 10 | BibTeX + Footer + responsive polish | `feat: add bibtex footer and responsive polish` |
| Commit 11 | Final QA, Lighthouse audit, image optimization | `fix: performance and accessibility final pass` |

### Development Rules for Codex

1. **One section per commit** — never bundle multiple sections
2. **Always test locally** — open `index.html` in browser after each section
3. **Use relative paths** — all image/script references from project root
4. **No npm/node_modules** — pure static site, CDN only for Chart.js and Google Fonts
5. **Mobile-first CSS** — write mobile styles first, then add media queries for desktop
6. **CSS variables for ALL colors** — enables theme toggle in one place
7. **Images are in `static/images/`** — use these exact filenames:
   - `introduction-infographic.png` (conveyor belt)
   - `benchmark-pipeline.png` (construction workflow)
   - `category-collapse-curves.jpg` (category chart)
   - `case-study-comparison.jpg` (regular vs tail-aware)
   - `distillation-example.png` (S1-S4 skill cards)
8. **Do NOT push to GitHub** — only local commits, remote push happens later
9. **Chart.js data is hardcoded** — all numbers come from the tables in this document
10. **tasks.json is placeholder** — use 5-10 sample tasks, full data generated later

### Codex System Prompt (copy-paste ready)

```
You are building a static academic project webpage for the TailSkills paper (EMNLP 2026).
The paper studies "Tail Knowledge Collapse" — how recursive skill distillation preserves
common-case knowledge but progressively erodes rare exception-handling knowledge.

Project directory: D:\codes\tailskill\
Tech stack: Pure HTML5 + CSS3 + vanilla JavaScript. No frameworks, no build tools.
External CDN: Chart.js 4.x, Google Fonts (Instrument Serif, DM Sans, JetBrains Mono)

Read the design specification at docs/website-design-spec.md for all details.
Follow the commit strategy in Section 0. One section per commit, test after each.

Key constraints:
- Light theme is DEFAULT (#fafaf8 bg), dark mode is toggleable
- All colors via CSS custom properties for theme switching
- Tail accent color: #E2ABB8, Common accent: #B2D9B3 (from the paper's LaTeX)
- Hero interaction: compression slider S1→S4, tail keywords fade out
- Chart.js for all data visualizations (collapse curves, retention bars)
- 208 task gallery with category filters and search (data in data/tasks.json)
- Mobile responsive, WCAG AA accessible, Lighthouse > 90

Do NOT:
- Use React, Next.js, or any framework
- Install npm packages or create node_modules
- Push to any remote repository
- Use AI-generated generic aesthetics (Inter font, purple gradients, etc.)
```

---

## 1. Core Concept: "Compression & Erosion"

The page's central interactive metaphor mirrors the paper's thesis: **as you "compress" a skill, tail knowledge erodes while common knowledge persists**. Every animation serves this narrative — nothing is decorative.

### Key Design Philosophy

- **Narrative-first**: All interactions explain the paper, not decorate the page
- **Restrained Vitality**: Academic rigor + measured interactive surprise
- **Explorable Data**: Users can interactively explore 208 tasks, 14 variants, 4 compression depths
- **Deploy Zero-Friction**: Static site, GitHub Pages direct deploy

---

## 2. Aesthetic Direction

### 2.1 Color System (Light Default + Dark Toggle)

| Token | Light Mode | Dark Mode | Usage |
|-------|-----------|-----------|-------|
| `--bg-primary` | `#fafaf8` (warm white) | `#0f0f14` | Page background |
| `--bg-secondary` | `#ffffff` | `#1a1a24` | Cards, sections |
| `--bg-tertiary` | `#f0f0ec` | `#14141e` | Alternating sections |
| `--text-primary` | `#1a1a2e` (deep navy) | `#f0ede6` | Headlines, body |
| `--text-secondary` | `#5a5a6e` | `#a0a0b0` | Captions, labels |
| `--accent-tail` | `#E2ABB8` (tailpink) | `#E2ABB8` | Tail knowledge, danger |
| `--accent-common` | `#B2D9B3` (commongreen) | `#B2D9B3` | Common knowledge, safety |
| `--accent-highlight` | `#4A6FA5` | `#6B8FC5` | Links, interactive |
| `--border` | `#e0e0dc` | `#2a2a3a` | Dividers, cards |

### 2.2 Typography

| Role | Font | Weight | Source |
|------|------|--------|--------|
| Display / H1 | **Instrument Serif** | 400 | Google Fonts |
| Headings / H2-H4 | **DM Sans** | 600-700 | Google Fonts |
| Body / Captions | **DM Sans** | 400 | Google Fonts |
| Code / Data | **JetBrains Mono** | 400 | Google Fonts |

### 2.3 Background Treatment

- Light mode: Subtle warm noise texture (SVG pattern, ~2% opacity) over `#fafaf8`
- Dark mode: Same noise texture over `#0f0f14` at slightly higher opacity (~4%)
- Section transitions: Soft gradient fades, no hard lines

### 2.4 Light/Dark Toggle

- Fixed top-right button: ☀️ / 🌙 icon
- Smooth CSS transition (0.3s) on all color tokens via CSS variables
- Preference saved to `localStorage`
- Respects `prefers-color-scheme` on first visit

---

## 3. Page Structure (9 Sections, Single-Page Scroll)

```
┌─────────────────────────────────────────────────────────────┐
│  NAV (fixed) — Logo | Sections | Light/Dark Toggle          │
├─────────────────────────────────────────────────────────────┤
│  S1. HERO — Title + Compression Slider                      │
├─────────────────────────────────────────────────────────────┤
│  S2. ABSTRACT — Paper abstract                              │
├─────────────────────────────────────────────────────────────┤
│  S3. INTRODUCTION — Skill Distillation infographic           │
├─────────────────────────────────────────────────────────────┤
│  S4. BENCHMARK — TailSkills construction + taxonomy          │
├─────────────────────────────────────────────────────────────┤
│  S5. MAIN RESULTS — Interactive charts + data table          │
├─────────────────────────────────────────────────────────────┤
│  S6. ABLATION — Retention analysis + forgetting rates        │
├─────────────────────────────────────────────────────────────┤
│  S7. CASE STUDY — Regular vs Tail-Aware comparison           │
├─────────────────────────────────────────────────────────────┤
│  S8. TASK GALLERY — 208 tasks with filters                  │
├─────────────────────────────────────────────────────────────┤
│  S9. BIBTEX + FOOTER                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Section-by-Section Design

### S1. Hero — "Focused but Fragile"

**Layout**: Full viewport height, centered content

**Content**:
- Title: "Focused but Fragile" (Instrument Serif, large)
- Subtitle: "Tail Knowledge Collapse in Recursive Agent Skill Distillation"
- Badge: "EMNLP 2026"
- Author list (anonymous for now, placeholder)
- Two buttons: [📄 Paper (arXiv)] [💻 GitHub]

**🎯 Compression Slider (Key Interaction)**:
- Below the title, a horizontal range slider: `S1 (8K) ← → S4 (2.7K)`
- As user drags right (deeper compression):
  - Title words "Fragile", "Tail", "Collapse", "Exception" fade/blur (opacity → 0.2, filter: blur(3px))
  - Title words "Focused", "Recursive", "Agent Skill" remain sharp
  - A small animated counter shows: "Tail knowledge retained: 100% → 15.7%"
  - A progress bar shrinks from full (green+pink) to mostly-green with pink disappearing
- **Mobile**: Tap buttons instead of slider

**Background**: Soft gradient, no image. Clean and focused on the interaction.

---

### S2. Abstract

**Layout**: Centered, max-width 800px, generous padding

**Content**: Full paper abstract in English

**Design**:
- Left border accent (3px, tailpink gradient)
- Clean paragraph typography
- Subtle entrance animation: fade-in-up on scroll

**Abstract text** (copy directly):
> Agent skills package procedural knowledge into reusable artifacts that can improve LLM agents at inference time. Existing work shows that curated skills can materially raise average pass rates and that transferable skills can be distilled from execution traces. However, current evaluations emphasize average-case performance and systematically under-measure rare exceptions. This paper studies tail-knowledge collapse: under recursive rewriting of a robust skill artifact into shorter or more standardized variants, common-case utility may remain stable while rare exception handling degrades. To investigate this, we introduce the TailSkills benchmark, a tail-focused evaluation suite featuring 14 variant types across six categories, 208 oracle-verified exception-heavy task variants with deterministic verifiers, and an expert-guided agentic construction pipeline. We show that recursive distillation can preserve common-case utility while degrading tail-case performance, and that this degradation is accompanied by the preferential removal of short, local tail-handling instructions relative to regular workflow content.

---

### S3. Introduction — Skill Distillation Visual

**Layout**: Full-width image with caption

**Content**: `static/images/introduction-infographic.png` (conveyor belt infographic)
- Shows S1→S4 distillation pipeline
- Contrasts "Ideal Sandbox" (success) vs "Real-World" (failure due to lost tail knowledge)

**Interaction**:
- Image scales slightly on hover (1.02x)
- Below image: three stat cards

| Stat | Value | Color |
|------|-------|-------|
| Common-case retention | ~100% across S1→S4 | commongreen |
| Tail-logic retention | 100% → 15.7% | tailpink |
| Total skill size | 8K → 2.7K chars | neutral |

---

### S4. Benchmark Overview

**Layout**: Two-part section

**Part A — Construction Pipeline**:
- `static/images/benchmark-pipeline.png` (4-step workflow)
- Four steps: Planning → Construction → Oracle Generation → Sandbox Verification
- Below: brief text explaining the process

**Part B — Interactive Taxonomy Grid**:

6 clickable category cards in a 3×2 grid:

```
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│  A: Data Encoding     │  │  B: File System       │  │  C: Data Quality      │
│  49 variants          │  │  60 variants          │  │  39 variants          │
│  Med Fragility        │  │  Med Fragility        │  │  High Fragility       │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│  D: Network/Service   │  │  E: Dependency        │  │  G: Security          │
│  35 variants          │  │  22 variants          │  │  3 variants           │
│  Med-High Fragility   │  │  Med Fragility        │  │  High Fragility       │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

- Click a card → expands to show sub-variants with counts
- Color-coded by fragility: Low (green) → Med (yellow) → High (red/tailpink)
- Animation: smooth height transition on expand

**Sub-variant detail on expand**:
```
A: Data Encoding
├── A1: BOM Injection ............ 23 tasks  [Med]
└── A2: Zero-width Characters .... 26 tasks  [Med-High]
```

**Variant taxonomy data**:
```
A: Data Encoding
  A1: BOM injection — 23 tasks — Med fragility
  A2: Zero-width characters — 26 tasks — Med-High fragility

B: File System
  B1: Read-only output dir — 50 tasks — Med fragility
  B2: Output contamination — 10 tasks — Med fragility

C: Data Boundary
  C1: NaN/Inf poisoning — 13 tasks — High fragility
  C2: Duplicate primary keys — 3 tasks — Low fragility
  C3: Extreme values — 13 tasks — High fragility
  C4: Type confusion — 10 tasks — High fragility

D: Network / Service
  D1: DNS jitter (50% loss) — 19 tasks — Med-High fragility
  D2: HTTPS connection throttling — 16 tasks — Med-High fragility

E: Dependency
  E1: Missing optional dep — 20 tasks — Med fragility
  E2: Library version drift — 2 tasks — High fragility

G: Security
  G1: Multi-vector attack — 2 tasks — High fragility
  G2: Security fallback — 1 task — High fragility
```

---

### S5. Main Results — Core Interactive Section

**Layout**: Three-part vertical stack

**Part A — Interactive Collapse Curves** (Chart.js):

Two side-by-side charts:

**Left Chart: Overall Tail-Collapse Curve**
- X-axis: Skill Generation (S1 → S4), labels: ["S₁ (8K)", "S₂ (5.6K)", "S₃ (3.9K)", "S₄ (2.7K)"]
- Y-axis: Pass Rate (%), range 0-100
- Two lines:
  - Common-case: #B2D9B3, nearly flat, data: [50.8, 52.5, 49.2, 49.2]
  - Tail-case: #E2ABB8, steep decline, data: [50.5, 35.4, 23.4, 23.1]
- Shaded confidence bands (lighter versions of each color)
- Hover: tooltip with exact values
- **Animation**: Lines draw from left to right on scroll-into-view

**Right Chart: Category-Specific Collapse** (reference: `static/images/category-collapse-curves.jpg`)
- 5 lines (A-E), each with distinct color:
  - A: Encoding — data: [43.5, 26.0, 17.4, 14.3]
  - B: File System — data: [51.7, 38.3, 30.9, 28.3]
  - C: Data Quality — data: [39.5, 28.2, 17.6, 5.1]
  - D: Network — data: [48.4, 34.3, 14.3, 34.3]
  - E: Dependency — data: [81.8, 59.1, 40.0, 45.5]
- Interactive legend: click to show/hide categories

**Part B — Data Table**:

| Distribution / Category | S₁ | S₂ | S₃ | S₄ |
|---|:---:|:---:|:---:|:---:|
| **Common-case** | 50.8% | 52.5% | 49.2% | 49.2% |
| **Tail-case** | 50.5% | 35.4% | 23.4% | 23.1% |
| *Gap* | 0.3% | **17.1%** | **25.8%** | **26.1%** |
| *Collapse Index* | 0.00 | **0.49** | **0.64** | **0.65** |
| | | | | |
| A: Encoding | 43.5% | 26.0% | 17.4% | 14.3% |
| B: File System | 51.7% | 38.3% | 30.9% | 28.3% |
| C: Data Quality | 39.5% | 28.2% | 17.6% | 5.1% |
| D: Network | 48.4% | 34.3% | 14.3% | 34.3% |
| E: Dependency | 81.8% | 59.1% | 40.0% | 45.5% |
| G: Multi-vector | 66.7% | 33.3% | 50.0% | 0.0% |

- Key values (Gap, CI) in tailpink (#E2ABB8)
- Hover: row highlight
- Category rows: subtle background tint matching category color

**Part C — Key Takeaway Cards** (3 cards in a row):

| Card | Value | Context |
|------|-------|---------|
| 27.4pp Drop | Tail-case: 50.5% → 23.1% | "54% relative degradation" |
| CI = 0.65 | at S₄ | "Tail degrades 2× faster than common-case" |
| 0.3% Gap at S₁ | baseline parity | "Oracle-verified: all variants are solvable" |

---

### S6. Ablation Studies

**Layout**: Two-column

**Left Column — Retention Analysis Chart** (Chart.js):

Grouped bar chart with 4 groups (S1→S4), 3 bars each:
- Total Words Retention (neutral gray #9CA3AF)
- Regular Content Retention (commongreen #B2D9B3)
- Tail-Logic Retention (tailpink #E2ABB8)

| Depth | Total | Regular | Tail | Tail Absent |
|-------|-------|---------|------|-------------|
| S₁ | 100% | 100% | 100% | — |
| S₂ | 70.9% | 73.5% | 43.5% | 34.6% |
| S₃ | 52.9% | 56.1% | 22.7% | 53.7% |
| S₄ | 45.6% | 48.7% | **15.7%** | **67.3%** |

**Animation**: Bars grow from 0 on scroll-into-view, staggered

**Right Column — Key Findings**:

4 insight cards with large numbers:

| Finding | Value | Description |
|---------|-------|-------------|
| Tail Retention at S₄ | **15.7%** | vs 48.7% regular content |
| Complete Tail Loss at S₄ | **67.3%** | 2/3 variants lose ALL tail knowledge |
| Tail Forgetting Rate | **48.0%** | Tasks that succeed at S₁ but fail at S₂ |
| Common Forgetting Rate | **3.3%** | Same depth, nearly zero degradation |

**Deletion Ablation Highlight**:
- Callout box: "Removing the defensive fragment from S₁ → **0/48** tasks pass (down from **48/48**)"
- Red accent border, strong visual weight

**Forgetting Rate Data**:

| Distribution | F(2) | F(3) | F(4) |
|---|:---:|:---:|:---:|
| Common (Dc) | -3.3% | 3.3% | 3.3% |
| Tail (Dt) | 48.0% | 63.4% | 44.6% |

---

### S7. Case Study — Regular vs Tail-Aware

**Layout**: Side-by-side comparison

**Content**: `static/images/case-study-comparison.jpg` (C4 Tail Variant comparison)

```
┌─── Regular Distillation ───┐  ┌─── Tail-Aware Distillation ───┐
│                             │  │                                │
│  Keeps: Core workflow       │  │  Keeps: Core workflow          │
│  Drops: Extreme value       │  │  Keeps: Extreme value          │
│         handling            │  │         handling               │
│                             │  │                                │
│  Result:                    │  │  Result:                       │
│  Heat = 85.94% ❌           │  │  Heat = 49.66% ✅              │
│  (outside 40-60% range)     │  │  (within expected range)       │
│                             │  │                                │
│  Verifier: FAIL             │  │  Verifier: PASS                │
└─────────────────────────────┘  └────────────────────────────────┘
```

**Interaction**: Hover over each side to highlight what's kept vs dropped
**Design**: Left panel has tailpink border, right has commongreen border

---

### S8. Task Gallery (SkillsBench-Inspired)

**Layout**: Filter bar + responsive grid

**Filter Bar**:
```
[🔍 Search...]  [A: Encode] [B: FileSys] [C: DataQl] [D: Network] [E: Depend] [G: Secure] [All]
```
- Active filter: filled pill with category color
- Search: fuzzy match on task name

**Task Card Design** (per task):
```
┌──────────────────────────────────────────┐
│ earthquake-phase-association              │
│ ┌──────┐ ┌──────┐ ┌──────┐              │
│ │A1 BOM│ │A2 ZW │ │D1 DNS│  ← variant   │
│ └──────┘ └──────┘ └──────┘    tags       │
│ Domain: Seismology                       │
│ Base task: ✅  Variants: 3/5 pass (S₁)   │
└──────────────────────────────────────────┘
```

- Click card → expand to show S1-S4 pass rates per variant
- Variant tags: color-coded by category (same as taxonomy colors)
- **No AI icons**, clean text-based design like SkillsBench

**Data**: 208 tasks from `data/tasks.json`

**Grid**: Responsive, 3 columns on desktop, 2 on tablet, 1 on mobile

---

### S9. BibTeX + Footer

**BibTeX Section**:
- Code block with monospace font
- "Copy" button (copies to clipboard)
- Citation placeholder:

```bibtex
@inproceedings{tailskills2026,
  title     = {Focused but Fragile: Tail Knowledge Collapse in Recursive Agent Skill Distillation},
  author    = {Anonymous},
  booktitle = {Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  year      = {2026}
}
```

**Footer**:
- GitHub repo link
- EMNLP 2026 badge

---

## 5. Technical Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Structure | HTML5 semantic | Zero build step |
| Styling | CSS3 + CSS Variables | Light/dark theme via variable swap |
| Charts | Chart.js 4.x (CDN) | Lightweight, interactive, academic-standard |
| Fonts | Google Fonts CDN | Instrument Serif + DM Sans + JetBrains Mono |
| Animations | CSS @keyframes + IntersectionObserver | Scroll-triggered, performant |
| Theme | CSS Variables + localStorage | Light/dark toggle with persistence |
| Deploy | GitHub Pages (direct push, later) | No CI/CD needed |

---

## 6. File Structure (current state)

```
D:\codes\tailskill\
├── docs/
│   └── website-design-spec.md    ← THIS FILE
├── static/
│   ├── css/                      ← (empty, to be created)
│   ├── js/                       ← (empty, to be created)
│   └── images/
│       ├── introduction-infographic.png   (1.7MB, conveyor belt)
│       ├── benchmark-pipeline.png         (1.3MB, construction workflow)
│       ├── category-collapse-curves.jpg   (140KB, category chart)
│       ├── case-study-comparison.jpg      (132KB, regular vs tail-aware)
│       └── distillation-example.png       (3.2MB, S1-S4 skill cards)
├── data/                         ← (empty, tasks.json to be created)
└── index.html                    ← (to be created)
```

---

## 7. Responsive Breakpoints

| Breakpoint | Layout Adjustments |
|-----------|-------------------|
| > 1200px | Full layout, 3-col gallery |
| 768–1200px | 2-col gallery, charts stack vertically |
| < 768px | Single column, hero slider becomes tap buttons, gallery 1-col |

---

## 8. Performance Budget

| Metric | Target |
|--------|--------|
| First Contentful Paint | < 1.5s |
| Total JS bundle (excl. Chart.js CDN) | < 15KB |
| Total CSS | < 20KB |
| Images | < 2MB total (optimize PNGs) |
| Lighthouse Performance | > 90 |

---

## 9. Accessibility

- All charts have `aria-label` descriptions
- Color is never the sole indicator (patterns + labels accompany)
- Keyboard-navigable: slider, filter buttons, gallery
- `prefers-reduced-motion`: disable scroll animations, keep static layout
- Contrast ratios meet WCAG AA in both themes

---

## 10. Animation Specification

| Element | Trigger | Animation | Duration |
|---------|---------|-----------|----------|
| Hero title | Page load | Fade-in-up, staggered words | 0.6s |
| Hero slider | User drag | Tail words blur/fade, counter updates | Real-time |
| Section headings | Scroll into view | Fade-in-up | 0.5s |
| Chart.js charts | Scroll into view | Data points animate from 0 | 1.0s |
| Category cards | Click | Smooth height expand | 0.3s |
| Gallery cards | Hover | Subtle lift (translateY -2px + shadow) | 0.2s |
| Theme toggle | Click | All colors transition | 0.3s |

---

## 11. Data Schema (tasks.json)

```json
{
  "tasks": [
    {
      "id": "earthquake-phase-association",
      "domain": "Seismology",
      "variants": [
        {
          "type": "A1_bom",
          "category": "A",
          "category_name": "Data Encoding",
          "variant_name": "BOM Injection",
          "fragility": "Med",
          "results": {
            "s1": 1.0,
            "s2": 0.0,
            "s3": 0.0,
            "s4": 0.0
          }
        }
      ]
    }
  ]
}
```

*(Full 208-task JSON to be generated from experiment data during implementation. Use 5-10 sample tasks for development.)*

---

*Document: D:\codes\tailskill\docs\website-design-spec.md*
*Generated: 2026-06-02 | Updated with Codex workflow | Ready for development*
