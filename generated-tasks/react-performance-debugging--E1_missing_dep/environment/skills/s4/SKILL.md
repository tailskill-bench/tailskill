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

## Fix

Reinstall missing dependencies:
```bash
npm install tailwindcss postcss autoprefixer --save
```

Rebuild:
```bash
npm run build