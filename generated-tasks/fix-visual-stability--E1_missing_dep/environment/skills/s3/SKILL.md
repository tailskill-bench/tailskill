---
name: s1
description: "Browser testing, React best practices, and web interface guidelines for visual stability."
---

# Performance Measurement with Playwright CDP

**Install:**
```bash
pip3 install --break-system-packages playwright==1.49.1
playwright install chromium
```

## Quick Start

```bash
npx ts-node <path-to-this-skill>/measure.ts http://localhost:3000
npx ts-node <path-to-this-skill>/measure.ts http://localhost:3000/api/products
```

## Output

```json
{
  "url": "http://localhost:3000",
  "totalMs": 1523,
  "requests": [
    { "url": "http://localhost:3000/", "ms": 45.2 },
    { "url": "http://localhost:3000/api/products", "ms": 512.3 }
  ],
  "metrics": {
    "JSHeapUsedSize": 4521984,
    "LayoutCount": 12,
    "ScriptDuration": 0.234
  }
}
```

### Key Metrics

| Metric | Meaning | Red flag |
|--------|---------|----------|
| `totalMs` | Total page load time | > 1000ms |
| `JSHeapUsedSize` | JS memory used | Growing over time |
| `LayoutCount` | Layout recalculations | > 50 per page |
| `ScriptDuration` | JS execution time | > 0.5s |

### Diagnosing Issues

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Sequential requests | Sequential `await` | Use `Promise.all()` |
| Same URL twice | Fetch before cache check | Check cache first |
| High LayoutCount | Re-rendering components | Add `React.memo`, `useMemo` |

## Measuring API Endpoints

```typescript
async function measureAPI(url: string) {
  const start = Date.now();
  const response = await fetch(url);
  const elapsed = Date.now() - start;
  return { url, time_ms: elapsed, status: response.status };
}
```

# Visual Stability Measurement

## CLS (Cumulative Layout Shift)

```bash
npx ts-node <path-to-this-skill>/measure-cls.ts http://localhost:3000
```

Output:
```json
{
  "url": "http://localhost:3000",
  "cls": 0.42,
  "rating": "poor",
  "shifts": [
    {
      "value": 0.15,
      "hadRecentInput": false,
      "sources": [{"nodeId": 42, "previousRect": {...}, "currentRect": {...}}]
    }
  ]
}
```

### CLS Thresholds

| CLS Score | Rating | Action |
|-----------|--------|--------|
| < 0.1 | Good | No action needed |
| 0.1 - 0.25 | Needs Improvement | Review shift sources |
| > 0.25 | Poor | Fix immediately |

### Accurate CLS Measurement

CLS measures shifts **within the viewport**. For full-page measurement:

1. Load page → Wait 3s → Scroll to bottom → Wait 2s
2. Trigger UI actions → Wait 2s → Read final CLS

```bash
npx ts-node <path-to-this-skill>/measure-cls.ts http://localhost:3000 --scroll
```

### Common CLS Causes

| Shift Source | Likely Cause | Fix |
|--------------|--------------|-----|
| `<img>` elements | Missing width/height | Add dimensions or use `next/image` |
| Theme wrapper | Hydration flicker | Use inline script before React |
| Skeleton loaders | Size mismatch | Match skeleton to final content size |
| Dynamic banners | No reserved space | Add `min-height` to container |
| Font loading | Custom fonts cause text reflow | Use `font-display: swap` or preload fonts |

## Theme Flicker Detection

```bash
npx ts-node <path-to-this-skill>/detect-flicker.ts http://localhost:3000
```

Detects if dark theme flashes white before loading.

# React Best Practices

45 rules across 8 categories, prioritized by impact.

## When to Apply

- Refactoring React/Next.js code
- Fixing CLS or visual instability
- Preventing localStorage/cookie flickering
- Optimizing font loading (FOIT/FOUT)

## Rule Categories

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Eliminating Waterfalls | CRITICAL | `async-` |
| 2 | Bundle Size Optimization | CRITICAL | `bundle-` |
| 3 | Server-Side Performance | HIGH | `server-` |
| 4 | Client-Side Data Fetching | MEDIUM-HIGH | `client-` |
| 5 | Re-render Optimization | MEDIUM | `rerender-` |
| 6 | Rendering Performance | MEDIUM | `rendering-` |
| 7 | JavaScript Performance | LOW-MEDIUM | `js-` |
| 8 | Advanced Patterns | LOW | `advanced-` |

## Rules by Category

**1. Eliminating Waterfalls (CRITICAL):** `async-parallel` (Promise.all), `async-dependencies`, `async-api-routes` (start promises early, await late), `async-suspense-boundaries`

**2. Bundle Size (CRITICAL):** `bundle-barrel-imports` (direct imports), `bundle-dynamic-imports` (next/dynamic), `bundle-defer-third-party` (analytics after hydration), `bundle-preload` (hover/focus)

**3. Server-Side (HIGH):** `server-cache-react` (React.cache), `server-cache-lru`, `server-serialization` (minimize client data), `server-parallel-fetching`

**4. Client-Side (MEDIUM-HIGH):** `client-swr-dedup` (SWR for deduplication), `client-event-listeners` (deduplicate listeners)

**5. Re-render (MEDIUM):** `rerender-defer-reads`, `rerender-memo`, `rerender-dependencies` (primitives), `rerender-derived-state`, `rerender-transitions` (startTransition)

**6. Rendering (MEDIUM):** `rendering-hydration-no-flicker` (inline script), `rendering-activity`, `rendering-conditional-render` (ternary not &&), `rendering-content-visibility`

**7. JavaScript (LOW-MEDIUM):** `js-batch-dom-css`, `js-cache-storage`, `js-combine-iterations`, `js-early-exit`, `js-set-map-lookups` (O(1))

**8. Advanced (LOW):** `advanced-event-handler-refs`, `advanced-use-latest`

Read individual rule files: `rules/async-parallel.md`, `rules/bundle-barrel-imports.md`, etc.

# Web Interface Guidelines

## Visual Stability Quick Reference

| Issue | Rule |
|-------|------|
| Images without dimensions | `<img>` needs `width` and `height` (prevents CLS) |
| Font loading flash | `<link rel="preload" as="font">` with `font-display: swap` |
| Large lists | Virtualize >50 items (`content-visibility: auto`) |
| Layout reads in render | No `getBoundingClientRect`/`offsetHeight` in render |

## Full Rules

**Images:** Explicit `width`/`height`; below-fold: `loading="lazy"`; above-fold: `priority` or `fetchpriority="high"`

**Performance:** Virtualize large lists; no layout reads in render; batch DOM reads/writes; preload critical fonts

**Accessibility:** Icon-only buttons need `aria-label`; form controls need `<label>` or `aria-label`; `<button>` for actions, `<a>`/`<Link>` for navigation; images need `alt` (or `alt=""` decorative)

**Focus States:** Visible focus via `focus-visible:ring-*`; never `outline-none` without replacement; use `:focus-visible` over `:focus`

**Animation:** Honor `prefers-reduced-motion`; animate `transform`/`opacity` only; never `transition: all`

**Forms:** Inputs need `autocomplete` and `name`; correct `type` (`email`, `tel`, `url`, `number`) and `inputmode`; never block paste; labels clickable via `htmlFor` or wrapping

**Content:** Text containers handle overflow (`truncate`, `line-clamp-*`, `break-words`); flex children need `min-w-0`; handle empty states

### Anti-patterns

- `user-scalable=no` or `maximum-scale=1`
- `transition: all`
- `outline-none` without `focus-visible` replacement
- Images without dimensions
- Large arrays `.map()` without virtualization
- Form inputs without labels
- Icon buttons without `aria-label`