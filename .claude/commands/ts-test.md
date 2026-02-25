---
description: Enforce TDD workflow for TypeScript. Write Vitest/Jest tests first, then implement. Verify 80%+ coverage.
---

# TypeScript TDD Command

This command enforces test-driven development methodology for TypeScript code using Vitest or Jest.

## What This Command Does

1. **Define Interfaces**: Scaffold type definitions and function signatures first
2. **Write Tests**: Create comprehensive test cases (RED)
3. **Run Tests**: Verify tests fail for the right reason
4. **Implement Code**: Write minimal code to pass (GREEN)
5. **Refactor**: Improve while keeping tests green
6. **Check Coverage**: Ensure 80%+ coverage

## When to Use

- Implementing new TypeScript functions or React components
- Adding test coverage to existing code
- Fixing bugs (write failing test first)
- Building critical business logic

## TDD Cycle

```
RED     → Write failing test with expect assertions
GREEN   → Implement minimal code to pass
REFACTOR → Improve code, tests stay green
REPEAT  → Next test case
```

## Test Patterns

### Unit Tests (Vitest)
```typescript
it("returns expected result", () => {
  expect(function(input)).toBe(expected)
})
```

### Parametrized Tests
```typescript
it.each([
  { input: "a", expected: 1 },
  { input: "b", expected: 2 },
])("processes $input", ({ input, expected }) => {
  expect(function(input)).toBe(expected)
})
```

### React Component Tests
```tsx
it("renders user name", () => {
  render(<UserCard user={mockUser} />)
  expect(screen.getByText("John")).toBeInTheDocument()
})
```

### Async Tests
```typescript
it("fetches data", async () => {
  const result = await fetchData()
  expect(result.status).toBe("ok")
})
```

## Coverage Commands

```bash
npx vitest run --coverage --coverage.thresholds.lines=80
# or
npx jest --coverage --coverageThreshold='{"global":{"lines":80}}'
```

| Code Type | Target |
|-----------|--------|
| Critical business logic | 100% |
| Public APIs | 90%+ |
| General code | 80%+ |

## Related

- Skill: `skills/typescript-testing/`
- Skill: `skills/tdd-workflow/`
