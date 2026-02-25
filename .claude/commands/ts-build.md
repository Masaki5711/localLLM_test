---
description: Fix TypeScript build errors, tsc type errors, and bundler failures incrementally. Invokes the ts-build-resolver agent for minimal, surgical fixes.
---

# TypeScript Build and Fix

This command invokes the **ts-build-resolver** agent to incrementally fix TypeScript build errors with minimal changes.

## What This Command Does

1. **Run Diagnostics**: Execute `tsc --noEmit`, `eslint`, `npm run build`
2. **Parse Errors**: Group by file and sort by error code
3. **Fix Incrementally**: One error at a time
4. **Verify Each Fix**: Re-run `tsc --noEmit` after each change
5. **Report Summary**: Show what was fixed and what remains

## When to Use

- `tsc --noEmit` reports type errors
- `npm run build` / `vite build` fails
- ESLint parsing errors
- After pulling changes that break types

## Common Errors Fixed

| Error | Typical Fix |
|-------|-------------|
| `TS2322: Type 'X' not assignable to 'Y'` | Fix type annotation or value |
| `TS2531: Object is possibly 'null'` | Add null check or `?.` |
| `TS2339: Property does not exist` | Add to interface or fix access |
| `TS2307: Cannot find module` | Fix path or install @types |
| `TS7006: Implicit 'any'` | Add type annotation |
| `TS2786: Cannot use as JSX component` | Fix return type |

## Diagnostic Commands Run

```bash
npx tsc --noEmit 2>&1
npx eslint . --ext .ts,.tsx 2>&1
npm run build 2>&1
```

## Fix Strategy

1. **Type errors first** — tsc must pass
2. **Module errors second** — All imports must resolve
3. **ESLint errors third** — Fix parsing/rule violations
4. **One fix at a time** — Verify each change
5. **Minimal changes** — Don't refactor, just fix

## Related

- Agent: `agents/ts-build-resolver.md`
- Skill: `skills/typescript-patterns/`
