---
name: s1
description: Next.js version compatibility guide for handling version drift in React performance debugging.
---

# Next.js Version Compatibility

## Version Drift Issues

Downgrading Next.js (e.g., 14.0.0 from 14.2.0) breaks features:

- **App Router**: `force-dynamic` config unreliable; Server Component streaming and `next/dynamic` imports behave differently.
- **API Routes**: `route.ts` handlers have different request/response handling; `NextRequest`/`NextResponse` APIs differ.
- **Build System**: PostCSS config and CSS module handling vary across versions.

## Detect & Fix Drift

Check installed version:
```bash
npm list next
```

Compare with `package.json`:
```bash
cat package.json | grep next
```

If mismatched, reinstall the correct version:
```bash
npm install next@14.2.0 --save
```

## Rebuild After Version Change

Always rebuild after changing Next.js version:
```bash
npm run build