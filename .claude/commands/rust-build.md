---
description: Fix Rust build errors, cargo clippy warnings, and linker issues incrementally. Invokes the rust-build-resolver agent for minimal, surgical fixes.
---

# Rust Build and Fix

This command invokes the **rust-build-resolver** agent to incrementally fix Rust build errors with minimal changes.

## What This Command Does

1. **Run Diagnostics**: Execute `cargo check`, `cargo clippy`, `cargo build`
2. **Parse Errors**: Group by file and sort by severity
3. **Fix Incrementally**: One error at a time
4. **Verify Each Fix**: Re-run build after each change
5. **Report Summary**: Show what was fixed and what remains

## When to Use

Use `/rust-build` when:
- `cargo build` fails with errors
- `cargo check` reports issues
- `cargo clippy` shows warnings
- Dependency or feature flag problems occur
- After pulling changes that break the build

## Diagnostic Commands Run

```bash
# Primary build check
cargo check 2>&1

# Full build
cargo build 2>&1

# Lint analysis
cargo clippy -- -D warnings 2>&1

# Dependency issues
cargo tree
cargo update --dry-run

# Format check
cargo fmt -- --check
```

## Example Session

```text
User: /rust-build

Agent:
# Rust Build Resolution

## Initial Diagnostics

```bash
$ cargo check
error[E0382]: borrow of moved value: `data`
  --> src/service/processor.rs:25:15
error[E0308]: mismatched types
  --> src/handler/api.rs:42:9
error[E0599]: no method named `execute` found for struct `Query`
  --> src/repository/user.rs:18:10
```

Errors found: 3

## Fix 1: Borrow of Moved Value

File: src/service/processor.rs:25
Error: borrow of moved value: `data`
Cause: data moved into function, then used again

```rust
// Changed
fn process(data: Vec<u8>) {
    send(data);
    log(&data);  // Error: data was moved
}
// To
fn process(data: Vec<u8>) {
    log(&data);  // Borrow before move
    send(data);
}
```

```bash
$ cargo check
# 2 errors remaining
```

## Fix 2: Mismatched Types

File: src/handler/api.rs:42
Error: expected `String`, found `&str`

```rust
// Changed
let name: String = user.name_ref();
// To
let name: String = user.name_ref().to_string();
```

```bash
$ cargo check
# 1 error remaining
```

## Fix 3: Method Not Found

File: src/repository/user.rs:18
Error: no method named `execute` found for struct `Query`

```rust
// Changed - wrong method name
query.execute(&pool).await?
// To - correct sqlx method
query.fetch_all(&pool).await?
```

```bash
$ cargo check
# Build successful!
```

## Final Verification

```bash
$ cargo clippy -- -D warnings
# No warnings

$ cargo test
test result: ok. 12 passed; 0 failed
```

## Summary

| Metric | Count |
|--------|-------|
| Build errors fixed | 3 |
| Clippy warnings fixed | 0 |
| Files modified | 3 |
| Remaining issues | 0 |

Build Status: ✅ SUCCESS
```

## Common Errors Fixed

| Error | Typical Fix |
|-------|-------------|
| `borrowed value does not live long enough` | Return owned value or restructure lifetimes |
| `cannot move out of borrowed content` | Clone, use reference, or restructure |
| `type mismatch` | Type conversion with `.into()`, `as`, or `.to_string()` |
| `trait not satisfied` | Add derive, implement trait, or add trait bound |
| `unresolved import` | Add to Cargo.toml or fix module path |
| `missing fields` | Add fields or use `..Default::default()` |
| `cannot borrow as mutable` | Fix borrow ordering or use interior mutability |
| `unused variable/import` | Remove or prefix with `_` |

## Fix Strategy

1. **Build errors first** - Code must compile
2. **Clippy warnings second** - Fix common mistakes
3. **Format issues third** - Run `cargo fmt`
4. **One fix at a time** - Verify each change
5. **Minimal changes** - Don't refactor, just fix

## Stop Conditions

The agent will stop and report if:
- Same error persists after 3 attempts
- Fix introduces more errors
- Requires architectural changes
- Missing external dependencies

## Related Commands

- `/rust-test` - Run tests after build succeeds
- `/rust-review` - Review code quality
- `/verify` - Full verification loop

## Related

- Agent: `agents/rust-build-resolver.md`
- Skill: `skills/rust-patterns/`
