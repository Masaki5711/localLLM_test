---
description: TypeScript testing patterns including Vitest/Jest, React Testing Library, Playwright E2E, mocking, and coverage. Follows TDD methodology.
user_invocable: true
---

# TypeScript Testing

## TDD Workflow

```
RED     → Write failing test with expect assertions
GREEN   → Implement minimal code to pass
REFACTOR → Improve code, tests stay green
REPEAT  → Next test case
```

## Unit Tests (Vitest/Jest)

```typescript
// tests/validator.test.ts
import { describe, it, expect } from "vitest"
import { validateEmail } from "../src/validator"

describe("validateEmail", () => {
  it("accepts valid email", () => {
    expect(validateEmail("user@example.com")).toBe(true)
  })

  it("rejects empty string", () => {
    expect(() => validateEmail("")).toThrow("cannot be empty")
  })

  it("rejects invalid format", () => {
    expect(() => validateEmail("not-an-email")).toThrow("invalid format")
  })
})
```

## Parametrized Tests

```typescript
describe("validateEmail", () => {
  const validCases = [
    "user@example.com",
    "user+tag@example.com",
    "first.last@example.com",
    "user@sub.domain.com",
  ]

  it.each(validCases)("accepts %s", (email) => {
    expect(validateEmail(email)).toBe(true)
  })

  const invalidCases = [
    { input: "", error: "cannot be empty" },
    { input: "no-at-sign", error: "invalid format" },
    { input: "@no-local", error: "invalid format" },
    { input: "no-domain@", error: "invalid format" },
  ]

  it.each(invalidCases)("rejects $input", ({ input, error }) => {
    expect(() => validateEmail(input)).toThrow(error)
  })
})
```

## React Component Testing

```tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { UserForm } from "../src/components/UserForm"

describe("UserForm", () => {
  it("submits form with valid data", async () => {
    const onSubmit = vi.fn()
    render(<UserForm onSubmit={onSubmit} />)

    await userEvent.type(screen.getByLabelText("Name"), "John Doe")
    await userEvent.type(screen.getByLabelText("Email"), "john@example.com")
    await userEvent.click(screen.getByRole("button", { name: "Submit" }))

    expect(onSubmit).toHaveBeenCalledWith({
      name: "John Doe",
      email: "john@example.com",
    })
  })

  it("shows validation error for empty name", async () => {
    render(<UserForm onSubmit={vi.fn()} />)

    await userEvent.click(screen.getByRole("button", { name: "Submit" }))

    expect(screen.getByText("Name is required")).toBeInTheDocument()
  })

  it("disables submit while loading", () => {
    render(<UserForm onSubmit={vi.fn()} loading />)

    expect(screen.getByRole("button", { name: "Submit" })).toBeDisabled()
  })
})
```

## Mocking

```typescript
import { vi, describe, it, expect, beforeEach } from "vitest"

// Mock module
vi.mock("../src/api", () => ({
  fetchUsers: vi.fn(),
}))

import { fetchUsers } from "../src/api"
import { UserService } from "../src/services/UserService"

describe("UserService", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("returns users from API", async () => {
    const mockUsers = [{ id: 1, name: "Alice" }]
    vi.mocked(fetchUsers).mockResolvedValue(mockUsers)

    const service = new UserService()
    const result = await service.getUsers()

    expect(result).toEqual(mockUsers)
    expect(fetchUsers).toHaveBeenCalledOnce()
  })

  it("throws on API failure", async () => {
    vi.mocked(fetchUsers).mockRejectedValue(new Error("Network error"))

    const service = new UserService()
    await expect(service.getUsers()).rejects.toThrow("Network error")
  })
})
```

## Async Testing

```typescript
describe("async operations", () => {
  it("resolves after delay", async () => {
    const result = await fetchWithRetry("/api/data")
    expect(result.status).toBe("ok")
  })

  it("handles concurrent requests", async () => {
    const results = await Promise.all([
      fetchData("a"),
      fetchData("b"),
      fetchData("c"),
    ])
    expect(results).toHaveLength(3)
    results.forEach(r => expect(r.ok).toBe(true))
  })

  it("times out after threshold", async () => {
    vi.useFakeTimers()
    const promise = waitForEvent(5000)
    vi.advanceTimersByTime(5001)
    await expect(promise).rejects.toThrow("Timeout")
    vi.useRealTimers()
  })
})
```

## API Integration Tests

```typescript
import { describe, it, expect, beforeAll, afterAll } from "vitest"
import { createApp } from "../src/app"
import supertest from "supertest"

describe("POST /api/users", () => {
  let app: Express
  let request: supertest.SuperTest<supertest.Test>

  beforeAll(() => {
    app = createApp({ testing: true })
    request = supertest(app)
  })

  it("creates user with valid data", async () => {
    const response = await request
      .post("/api/users")
      .send({ name: "John", email: "john@example.com" })
      .expect(201)

    expect(response.body).toMatchObject({
      success: true,
      data: { name: "John", email: "john@example.com" },
    })
  })

  it("returns 400 for invalid email", async () => {
    const response = await request
      .post("/api/users")
      .send({ name: "John", email: "not-valid" })
      .expect(400)

    expect(response.body.success).toBe(false)
  })
})
```

## E2E Tests (Playwright)

```typescript
import { test, expect } from "@playwright/test"

test.describe("User Management", () => {
  test("creates a new user", async ({ page }) => {
    await page.goto("/users")

    await page.getByRole("button", { name: "Add User" }).click()
    await page.getByLabel("Name").fill("Test User")
    await page.getByLabel("Email").fill("test@example.com")
    await page.getByRole("button", { name: "Save" }).click()

    await expect(page.getByText("User created successfully")).toBeVisible()
    await expect(page.getByText("Test User")).toBeVisible()
  })

  test("validates required fields", async ({ page }) => {
    await page.goto("/users/new")
    await page.getByRole("button", { name: "Save" }).click()

    await expect(page.getByText("Name is required")).toBeVisible()
    await expect(page.getByText("Email is required")).toBeVisible()
  })
})
```

## Coverage

```bash
# Vitest
npx vitest run --coverage
npx vitest run --coverage --coverage.thresholds.lines=80

# Jest
npx jest --coverage --coverageThreshold='{"global":{"lines":80}}'

# Playwright
npx playwright test
```

| Code Type | Target |
|-----------|--------|
| Critical business logic | 100% |
| Public APIs | 90%+ |
| General code | 80%+ |
| Generated/config code | Exclude |

## Test Organization

```
tests/
├── setup.ts                 # Global test setup
├── unit/
│   ├── validators.test.ts
│   ├── services.test.ts
│   └── utils.test.ts
├── integration/
│   ├── api.test.ts
│   └── database.test.ts
├── components/
│   ├── UserForm.test.tsx
│   └── UserList.test.tsx
└── e2e/
    ├── auth.spec.ts
    └── users.spec.ts
```

## Best Practices

**DO:**
- Write test FIRST before implementation
- Use `describe` blocks for grouping
- Use `it.each` for parameterized tests
- Mock at module boundaries, not internals
- Use `screen.getByRole` over `getByTestId`
- Assert on user-visible behavior

**DON'T:**
- Test implementation details
- Mock everything (test real behavior)
- Use `sleep()` or fixed timeouts
- Snapshot test frequently-changing UI
- Skip the RED phase in TDD
- Use `any` in test types
