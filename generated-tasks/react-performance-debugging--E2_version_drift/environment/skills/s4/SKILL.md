---
name: s1
description: Guide for handling Next.js version drift in React performance debugging.
---

# Next.js Version Compatibility

Downgrading Next.js (e.g., 14.0.0→14.2.0) breaks features:
- **App Router**: `force-dynamic` unreliable; Server Component streaming and `next/dynamic` differ.
- **API Routes**: `route.ts` handlers differ; `NextRequest`/`NextResponse` APIs vary.
- **Build System**: PostCSS config and CSS module handling vary.

## Detect & Fix Drift

```bash
npm list next
```

```bash
cat package.json | grep next
```

If mismatched:
```bash
npm install next@14.2.0 --save
```

Always rebuild after version change:
```bash
npm run build