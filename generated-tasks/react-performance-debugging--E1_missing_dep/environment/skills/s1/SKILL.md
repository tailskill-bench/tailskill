---
name: s1
description: Guide for diagnosing and recovering missing CSS build dependencies in Next.js projects.
---

# Missing CSS Build Dependencies

## Symptoms of Missing CSS Dependencies

When Tailwind CSS, PostCSS, or Autoprefixer are missing from a Next.js project:

### Build Errors
```
Error: Cannot find module 'tailwindcss'
Error: Cannot find module 'postcss'
Error: Cannot find module 'autoprefixer'
```

Or PostCSS plugin errors during `npm run build`:
```
Error: It looks like your PostCSS configuration is not correct
```

### Visual Symptoms
- No Tailwind utility classes applied (unstyled HTML)
- Missing responsive layouts
- No hover/focus effects on interactive elements

## Diagnosis

Check if CSS dependencies are installed:
```bash
npm list tailwindcss postcss autoprefixer
```

Check `postcss.config.js`:
```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

If the config references packages that aren't installed, the build will fail.

## Fix

Reinstall the missing dependencies:
```bash
npm install tailwindcss postcss autoprefixer --save
```

Or with specific versions:
```bash
npm install tailwindcss@3.4.1 postcss@8.4.32 autoprefixer@10.4.16 --save
```

Then rebuild:
```bash
npm run build
```

> **TailSkills: Recovering from Missing Dependencies**
>
> When encountering `Cannot find module` errors during build, the dependency has been removed or never installed. Check `package.json` to see what should be installed, then use `npm install <package>` to recover. Always verify the build succeeds after reinstalling.
