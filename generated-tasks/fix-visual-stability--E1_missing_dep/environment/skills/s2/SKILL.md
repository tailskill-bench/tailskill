---
name: s1
description: "Browser testing, React best practices, and web interface guidelines for visual stability fixes."
---

# Browser Testing

# Performance Measurement with Playwright CDP

Diagnose performance issues by measuring actual load times and network activity.

**Playwright may need to be installed first:**
```bash
pip3 install --break-system-packages playwright==1.49.1
playwright install chromium
```

## Quick Start

A `measure.ts` script is included in this skill's directory:

```bash
npx ts-node <path-to-this-skill>/measure.ts http://localhost:3000
npx ts-node <path-to-this-skill>/measure.ts http://localhost:3000/api/products
```

## Understanding the Output

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

### Reading the Waterfall

Look for **sequential patterns** in the `requests` array:

```
BAD (sequential):
  /api/products    |████████|                        512ms
  /api/featured             |██████|                 301ms  (starts AFTER products)
  Total: 1014ms

GOOD (parallel):
  /api/products    |████████|                        512ms
  /api/featured    |██████|                          301ms  (starts SAME TIME)
  Total: 512ms
```

### Key Metrics

| Metric | What it means | Red flag |
|--------|---------------|----------|
| `totalMs` | Total page load time | > 1000ms |
| `JSHeapUsedSize` | Memory used by JS | Growing over time |
| `LayoutCount` | Layout recalculations | > 50 per page |
| `ScriptDuration` | Time in JS execution | > 0.5s |

## What to Look For

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Requests in sequence | Sequential `await` statements | Use `Promise.all()` |
| Same URL requested twice | Fetch before cache check | Check cache first |
| High LayoutCount | Components re-rendering | Add `React.memo`, `useMemo` |

## Measuring API Endpoints Directly

```typescript
async function measureAPI(url: string) {
  const start = Date.now();
  const response = await fetch(url);
  const elapsed = Date.now() - start;
  return { url, time_ms: elapsed, status: response.status };
}
```

## Visual Stability Measurement

### Measure CLS (Cumulative Layout Shift)

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

### Detect Theme Flicker

```bash
npx ts-node <path-to-this-skill>/detect-flicker.ts http://localhost:3000
```

Detects if dark theme flashes white before loading.

### Accurate CLS Measurement

CLS only measures shifts **within the viewport**. For accurate measurement:

1. Load page → Wait 3 seconds → Scroll to bottom → Wait 2 seconds
2. Trigger UI actions → Wait 2 seconds → Read final CLS

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

# React Best Practices

# Vercel React Best Practices

Performance optimization guide for React/Next.js applications. 45 rules across 8 categories, prioritized by impact.

## When to Apply

- Refactoring existing React/Next.js code
- Fixing visual instability or layout shift (CLS) issues
- Preventing flickering when reading from localStorage or cookies
- Optimizing font loading (FOIT/FOUT prevention)

## Rule Categories by Priority

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

## Quick Reference

### 1. Eliminating Waterfalls (CRITICAL)

- `async-parallel` - Use Promise.all() for independent operations
- `async-dependencies` - Use better-all for partial dependencies
- `async-api-routes` - Start promises early, await late in API routes
- `async-suspense-boundaries` - Use Suspense to stream content

### 2. Bundle Size Optimization (CRITICAL)

- `bundle-barrel-imports` - Import directly, avoid barrel files
- `bundle-dynamic-imports` - Use next/dynamic for heavy components
- `bundle-defer-third-party` - Load analytics/logging after hydration
- `bundle-preload` - Preload on hover/focus for perceived speed

### 3. Server-Side Performance (HIGH)

- `server-cache-react` - Use React.cache() for per-request deduplication
- `server-cache-lru` - Use LRU cache for cross-request caching
- `server-serialization` - Minimize data passed to client components
- `server-parallel-fetching` - Restructure components to parallelize fetches

### 4. Client-Side Data Fetching (MEDIUM-HIGH)

- `client-swr-dedup` - Use SWR for automatic request deduplication
- `client-event-listeners` - Deduplicate global event listeners

### 5. Re-render Optimization (MEDIUM)

- `rerender-defer-reads` - Don't subscribe to state only used in callbacks
- `rerender-memo` - Extract expensive work into memoized components
- `rerender-dependencies` - Use primitive dependencies in effects
- `rerender-derived-state` - Subscribe to derived booleans, not raw values
- `rerender-transitions` - Use startTransition for non-urgent updates

### 6. Rendering Performance (MEDIUM)

- `rendering-hydration-no-flicker` - Use inline script for client-only data
- `rendering-activity` - Use Activity component for show/hide
- `rendering-conditional-render` - Use ternary, not && for conditionals
- `rendering-content-visibility` - Use content-visibility for long lists

### 7. JavaScript Performance (LOW-MEDIUM)

- `js-batch-dom-css` - Group CSS changes via classes or cssText
- `js-cache-storage` - Cache localStorage/sessionStorage reads
- `js-combine-iterations` - Combine multiple filter/map into one loop
- `js-early-exit` - Return early from functions
- `js-set-map-lookups` - Use Set/Map for O(1) lookups

### 8. Advanced Patterns (LOW)

- `advanced-event-handler-refs` - Store event handlers in refs
- `advanced-use-latest` - useLatest for stable callback refs

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/async-parallel.md
rules/bundle-barrel-imports.md
```

# Web Interface Guidelines

Review UI code for compliance with Vercel's web interface standards.

## Quick Reference - Visual Stability

| Issue | Rule |
|-------|------|
| Images without dimensions | `<img>` needs explicit `width` and `height` (prevents CLS) |
| Font loading flash | Critical fonts: `<link rel="preload" as="font">` with `font-display: swap` |
| Large lists | Virtualize lists >50 items (`content-visibility: auto`) |
| Layout reads in render | No `getBoundingClientRect`, `offsetHeight` in render path |

## Full Rules

### Images

- `<img>` needs explicit `width` and `height` (prevents CLS)
- Below-fold images: `loading="lazy"`
- Above-fold critical images: `priority` or `fetchpriority="high"`

### Performance

- Large lists (>50 items): virtualize (`virtua`, `content-visibility: auto`)
- No layout reads in render (`getBoundingClientRect`, `offsetHeight`, `offsetWidth`, `scrollTop`)
- Batch DOM reads/writes; avoid interleaving
- Critical fonts: `<link rel="preload" as="font">` with `font-display: swap`

### Accessibility

- Icon-only buttons need `aria-label`
- Form controls need `<label>` or `aria-label`
- `<button>` for actions, `<a>`/`<Link>` for navigation (not `<div onClick>`)
- Images need `alt` (or `alt=""` if decorative)

### Focus States

- Interactive elements need visible focus: `focus-visible:ring-*` or equivalent
- Never `outline-none` / `outline: none` without focus replacement
- Use `:focus-visible` over `:focus` (avoid focus ring on click)

### Animation

- Honor `prefers-reduced-motion` (provide reduced variant or disable)
- Animate `transform`/`opacity` only (compositor-friendly)
- Never `transition: all`—list properties explicitly

### Forms

- Inputs need `autocomplete` and meaningful `name`
- Use correct `type` (`email`, `tel`, `url`, `number`) and `inputmode`
- Never block paste (`onPaste` + `preventDefault`)
- Labels clickable (`htmlFor` or wrapping control)

### Content Handling

- Text containers handle long content: `truncate`, `line-clamp-*`, or `break-words`
- Flex children need `min-w-0` to allow text truncation
- Handle empty states—don't render broken UI for empty strings/arrays

### Anti-patterns (flag these)

- `user-scalable=no` or `maximum-scale=1` disabling zoom
- `transition: all`
- `outline-none` without focus-visible replacement
- Images without dimensions
- Large arrays `.map()` without virtualization
- Form inputs without labels
- Icon buttons without `aria-label`