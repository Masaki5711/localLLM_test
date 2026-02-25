---
description: Comprehensive Rust code review for ownership, safety, concurrency, error handling, and security. Invokes the rust-reviewer agent.
---

# Rust Code Review

This command invokes the **rust-reviewer** agent for comprehensive Rust-specific code review.

## What This Command Does

1. **Identify Rust Changes**: Find modified `.rs` files via `git diff`
2. **Run Static Analysis**: Execute `cargo clippy`, `cargo check`, `cargo audit`
3. **Security Scan**: Check for unsafe usage, SQL injection, command injection
4. **Concurrency Review**: Analyze Send/Sync safety, Arc/Mutex usage, async patterns
5. **Ownership Check**: Verify borrowing, lifetimes, unnecessary clones
6. **Generate Report**: Categorize issues by severity

## When to Use

Use `/rust-review` when:
- After writing or modifying Rust code
- Before committing Rust changes
- Reviewing pull requests with Rust code
- Onboarding to a new Rust codebase
- Learning idiomatic Rust patterns

## Review Categories

### CRITICAL (Must Fix)
- Unjustified `unsafe` blocks
- SQL/Command injection vulnerabilities
- Data races or Send/Sync violations
- Hardcoded credentials
- unwrap() in production error paths
- Use-after-free potential (raw pointers)

### HIGH (Should Fix)
- Missing error context (bare `?` without `.context()`)
- Unnecessary `.clone()` to appease borrow checker
- Blocking operations in async contexts
- Deadlock-prone lock ordering
- Ignoring Result with `let _ =` on important operations
- Missing trait bounds

### MEDIUM (Consider)
- Non-idiomatic patterns (manual loops vs iterators)
- Missing derive macros (Debug, Clone)
- String instead of &str in parameters
- Vec not pre-allocated
- Missing doc comments on public items
- Not using Cow where applicable

## Automated Checks Run

```bash
# Lint analysis
cargo clippy -- -D warnings

# Build check
cargo check

# Security audit
cargo audit

# Format check
cargo fmt -- --check

# Test
cargo test
```

## Example Usage

```text
User: /rust-review

Agent:
# Rust Code Review Report

## Files Reviewed
- src/handler/api.rs (modified)
- src/service/auth.rs (modified)

## Static Analysis Results
✓ cargo check: No issues
⚠ cargo clippy: 2 warnings

## Issues Found

[CRITICAL] Unsafe Block Without Justification
File: src/service/auth.rs:38
Issue: Raw pointer dereference without safety comment
```rust
unsafe {
    let token = &*(ptr as *const Token);  // No safety invariant documented
}
```
Fix: Add SAFETY comment or use safe alternative
```rust
// SAFETY: ptr is guaranteed valid and aligned by the token pool allocator,
// and the pool outlives all references returned by this function.
unsafe {
    let token = &*(ptr as *const Token);
}
```

[HIGH] Unnecessary Clone
File: src/handler/api.rs:25
Issue: Cloning String when borrow would suffice
```rust
fn process(data: &Request) -> Response {
    let name = data.name.clone();  // Unnecessary clone
    validate(&name)
}
```
Fix: Use reference directly
```rust
fn process(data: &Request) -> Response {
    validate(&data.name)
}
```

## Summary
- CRITICAL: 1
- HIGH: 1
- MEDIUM: 0

Recommendation: ❌ Block merge until CRITICAL issue is fixed
```

## Approval Criteria

| Status | Condition |
|--------|-----------|
| ✅ Approve | No CRITICAL or HIGH issues |
| ⚠️ Warning | Only MEDIUM issues (merge with caution) |
| ❌ Block | CRITICAL or HIGH issues found |

## Integration with Other Commands

- Use `/rust-test` first to ensure tests pass
- Use `/rust-build` if build errors occur
- Use `/rust-review` before committing
- Use `/code-review` for non-Rust specific concerns

## Related

- Agent: `agents/rust-reviewer.md`
- Skills: `skills/rust-patterns/`, `skills/rust-testing/`
