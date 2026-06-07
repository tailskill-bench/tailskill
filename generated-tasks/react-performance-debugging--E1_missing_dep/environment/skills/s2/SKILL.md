---
name: s1
description: Guide for diagnosing and recovering missing CSS build dependencies in Next.js projects.
---

# Missing CSS Build Dependencies

## Symptoms

Build errors:
```
Error: Cannot find module 'tailwindcss'
Error: Cannot find module 'postcss'
Error: Cannot find module 'autoprefixer'
```

PostCSS plugin errors during `npm run build`:
```
Error: It looks like your PostCSS configuration is not correct
```

Visual symptoms: unstyled HTML, missing responsive layouts, no hover/focus effects.

## Diagnosis

Check installed dependencies:
```bash
npm list tailwindcss postcss autoprefixer
```

Verify `postcss.config.js`:
```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

If the config references uninstalled packages, the build will fail.

## Fix

Reinstall missing dependencies:
```bash
npm install tailwindcss postcss autoprefixer --save
```

With specific versions:
```bash
npm install tailwindcss@3.4.1 postcss@8.4.32 autoprefixer@10.4.16 --save
```

Rebuild:
```bash
npm run build
```

> **Note:** When encountering `Cannot find module` errors during build, check `package.json` to see what should be installed, then use `npm install <package>` to recover. Always verify the build succeeds after reinstalling.