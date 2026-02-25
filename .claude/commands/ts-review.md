---
description: Comprehensive TypeScript code review for type safety, React patterns, async handling, security, and performance. Invokes the ts-reviewer agent.
---

# TypeScript Code Review

This command invokes the **ts-reviewer** agent for comprehensive TypeScript-specific code review.

## What This Command Does

1. **Identify TS Changes**: Find modified `.ts`/`.tsx` files via `git diff`
2. **Run Static Analysis**: Execute `tsc --noEmit`, `eslint`
3. **Security Scan**: Check for XSS, injection, prototype pollution
4. **Type Safety Review**: Check for `any`, non-null assertions, type guards
5. **React Review**: Key props, hook dependencies, derived state
6. **Generate Report**: Categorize issues by severity

## When to Use

- After writing or modifying TypeScript/React code
- Before committing TypeScript changes
- Reviewing pull requests with TypeScript code

## Review Categories

### CRITICAL (Must Fix)
- XSS via `innerHTML` / `dangerouslySetInnerHTML`
- SQL/NoSQL injection
- Hardcoded credentials
- `any` in public API types
- Unhandled Promise rejections

### HIGH (Should Fix)
- Non-null assertion `!` without guarantee
- `as` type assertion instead of type guard
- Missing hook dependencies (stale closure)
- Sequential awaits when parallel possible

### MEDIUM (Consider)
- Missing `React.memo` for expensive renders
- Large bundle imports
- `enum` instead of `as const` union
- Missing error boundaries

## Automated Checks Run

```bash
npx tsc --noEmit
npx eslint . --ext .ts,.tsx
npx prettier --check "src/**/*.{ts,tsx}"
npx vitest run
```

## Approval Criteria

| Status | Condition |
|--------|-----------|
| APPROVE | No CRITICAL or HIGH issues |
| WARNING | Only MEDIUM issues |
| BLOCK | CRITICAL or HIGH issues found |

## Related

- Agent: `agents/ts-reviewer.md`
- Skills: `skills/typescript-patterns/`, `skills/typescript-testing/`
