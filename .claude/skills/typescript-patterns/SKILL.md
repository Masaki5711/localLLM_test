---
description: Idiomatic TypeScript patterns, best practices, and conventions for building type-safe, maintainable applications with React and Node.js.
user_invocable: true
---

# TypeScript Patterns

## Core Principles

1. **Strict mode always** — `"strict": true` in tsconfig.json
2. **No `any`** — use `unknown`, generics, or specific types
3. **Immutability** — `readonly`, `as const`, spread over mutation
4. **Type narrowing** — type guards over type assertions

## Type System

```typescript
// Discriminated unions (prefer over enums)
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: string }

// Branded types for domain safety
type UserId = number & { readonly __brand: "UserId" }
type OrderId = number & { readonly __brand: "OrderId" }

function createUserId(id: number): UserId {
  return id as UserId
}

// Template literal types
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE"
type ApiEndpoint = `/api/v1/${string}`

// Mapped types
type Readonly<T> = { readonly [K in keyof T]: T[K] }
type Partial<T> = { [K in keyof T]?: T[K] }
type Pick<T, K extends keyof T> = { [P in K]: T[P] }
```

## Data Models

```typescript
// Use interfaces for object shapes
interface User {
  readonly id: number
  readonly name: string
  readonly email: string
  readonly createdAt: Date
}

// Use type for unions, intersections, utilities
type CreateUserInput = Omit<User, "id" | "createdAt">
type UpdateUserInput = Partial<Pick<User, "name" | "email">>

// Zod for runtime validation
import { z } from "zod"

const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().min(0).max(150),
})

type CreateUserInput = z.infer<typeof CreateUserSchema>
```

## Error Handling

```typescript
// Custom error classes
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500
  ) {
    super(message)
    this.name = this.constructor.name
  }
}

class NotFoundError extends AppError {
  constructor(entity: string, id: string | number) {
    super(`${entity} with id=${id} not found`, "NOT_FOUND", 404)
  }
}

// Result pattern (no exceptions)
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E }

function ok<T>(value: T): Result<T, never> {
  return { ok: true, value }
}

function err<E>(error: E): Result<never, E> {
  return { ok: false, error }
}
```

## React Patterns

```tsx
// Component with typed props
interface UserCardProps {
  readonly user: User
  readonly onEdit: (id: number) => void
}

function UserCard({ user, onEdit }: UserCardProps) {
  return (
    <div>
      <h2>{user.name}</h2>
      <button onClick={() => onEdit(user.id)}>Edit</button>
    </div>
  )
}

// Custom hooks
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debouncedValue
}

// Generic fetch hook
function useQuery<T>(url: string): {
  data: T | null
  loading: boolean
  error: Error | null
} {
  const [state, setState] = useState<{
    data: T | null
    loading: boolean
    error: Error | null
  }>({ data: null, loading: true, error: null })

  useEffect(() => {
    const controller = new AbortController()
    fetch(url, { signal: controller.signal })
      .then(res => res.json())
      .then(data => setState({ data, loading: false, error: null }))
      .catch(error => {
        if (!controller.signal.aborted) {
          setState({ data: null, loading: false, error })
        }
      })
    return () => controller.abort()
  }, [url])

  return state
}
```

## Async Patterns

```typescript
// Parallel execution
const [users, orders] = await Promise.all([
  fetchUsers(),
  fetchOrders(),
])

// Error-safe parallel
const results = await Promise.allSettled([
  fetchUsers(),
  fetchOrders(),
])

for (const result of results) {
  if (result.status === "fulfilled") {
    process(result.value)
  } else {
    logger.error("Failed:", result.reason)
  }
}

// Retry with exponential backoff
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      await new Promise(r => setTimeout(r, baseDelay * 2 ** i))
    }
  }
  throw new Error("Unreachable")
}
```

## API Layer

```typescript
// Type-safe API client
interface ApiClient {
  get<T>(path: string): Promise<T>
  post<T>(path: string, body: unknown): Promise<T>
  put<T>(path: string, body: unknown): Promise<T>
  delete(path: string): Promise<void>
}

// API response format
interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  meta?: { total: number; page: number; limit: number }
}

// Repository pattern
interface Repository<T> {
  findAll(filters?: Record<string, unknown>): Promise<T[]>
  findById(id: string): Promise<T | null>
  create(data: Omit<T, "id">): Promise<T>
  update(id: string, data: Partial<T>): Promise<T>
  delete(id: string): Promise<void>
}
```

## State Management

```typescript
// Zustand (lightweight, recommended)
import { create } from "zustand"

interface UserStore {
  users: User[]
  loading: boolean
  fetchUsers: () => Promise<void>
  addUser: (user: User) => void
}

const useUserStore = create<UserStore>((set) => ({
  users: [],
  loading: false,
  fetchUsers: async () => {
    set({ loading: true })
    const users = await api.get<User[]>("/api/users")
    set({ users, loading: false })
  },
  addUser: (user) => set((state) => ({
    users: [...state.users, user],
  })),
}))
```

## Anti-Patterns to Avoid

| Anti-Pattern | Fix |
|-------------|-----|
| `any` type | `unknown`, generics, or specific types |
| `as` assertions | Type guards with `is` |
| `!` non-null assertion | Proper null checks |
| `enum` | `as const` objects or union types |
| Index access `obj["key"]` | Typed property access |
| `Function` type | Specific `(args) => return` |
| Mutation | Spread, `structuredClone()` |
| `namespace` | ES modules |
| String-based events | Typed event emitters |
| `== null` | `=== null \|\| === undefined` |

## Tooling

```bash
# Type checking
npx tsc --noEmit

# Linting
npx eslint . --ext .ts,.tsx

# Formatting
npx prettier --write "src/**/*.{ts,tsx}"

# Testing
npx vitest run
# or
npx jest --passWithNoTests

# Bundle analysis
npx vite-bundle-visualizer
```

## tsconfig.json (Strict)

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "exactOptionalPropertyTypes": true,
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "declaration": true,
    "sourceMap": true
  }
}
```
