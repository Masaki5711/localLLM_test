---
description: Enforce TDD workflow for Rust. Write tests first, then implement. Verify 80%+ coverage with cargo-tarpaulin or cargo-llvm-cov.
---

# Rust TDD Command

This command enforces test-driven development methodology for Rust code using idiomatic Rust testing patterns.

## What This Command Does

1. **Define Types/Traits**: Scaffold function signatures and trait definitions first
2. **Write Tests**: Create comprehensive test cases with assert macros (RED)
3. **Run Tests**: Verify tests fail for the right reason
4. **Implement Code**: Write minimal code to pass (GREEN)
5. **Refactor**: Improve while keeping tests green
6. **Check Coverage**: Ensure 80%+ coverage

## When to Use

Use `/rust-test` when:
- Implementing new Rust functions
- Adding test coverage to existing code
- Fixing bugs (write failing test first)
- Building critical business logic
- Learning TDD workflow in Rust

## TDD Cycle

```
RED     → Write failing test with assert macros
GREEN   → Implement minimal code to pass
REFACTOR → Improve code, tests stay green
REPEAT  → Next test case
```

## Example Session

```text
User: /rust-test I need a function to validate email addresses

Agent:
# TDD Session: Email Validator

## Step 1: Define Interface

```rust
// src/validator.rs
use thiserror::Error;

#[derive(Error, Debug, PartialEq)]
pub enum ValidationError {
    #[error("email cannot be empty")]
    Empty,
    #[error("email format is invalid")]
    InvalidFormat,
}

pub fn validate_email(email: &str) -> Result<(), ValidationError> {
    todo!()
}
```

## Step 2: Write Tests (RED)

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn valid_simple_email() {
        assert!(validate_email("user@example.com").is_ok());
    }

    #[test]
    fn valid_email_with_subdomain() {
        assert!(validate_email("user@mail.example.com").is_ok());
    }

    #[test]
    fn valid_email_with_plus() {
        assert!(validate_email("user+tag@example.com").is_ok());
    }

    #[test]
    fn valid_email_with_dots() {
        assert!(validate_email("first.last@example.com").is_ok());
    }

    #[test]
    fn empty_email_returns_error() {
        assert_eq!(
            validate_email(""),
            Err(ValidationError::Empty)
        );
    }

    #[test]
    fn no_at_sign_returns_error() {
        assert_eq!(
            validate_email("userexample.com"),
            Err(ValidationError::InvalidFormat)
        );
    }

    #[test]
    fn no_domain_returns_error() {
        assert_eq!(
            validate_email("user@"),
            Err(ValidationError::InvalidFormat)
        );
    }

    #[test]
    fn no_local_part_returns_error() {
        assert_eq!(
            validate_email("@example.com"),
            Err(ValidationError::InvalidFormat)
        );
    }

    #[test]
    fn spaces_returns_error() {
        assert_eq!(
            validate_email("user @example.com"),
            Err(ValidationError::InvalidFormat)
        );
    }
}
```

## Step 3: Run Tests - Verify FAIL

```bash
$ cargo test

running 9 tests
test tests::valid_simple_email ... FAILED
thread 'tests::valid_simple_email' panicked at 'not yet implemented'

test result: FAILED. 0 passed; 9 failed
```

✓ Tests fail as expected (todo! panic).

## Step 4: Implement Minimal Code (GREEN)

```rust
use regex::Regex;
use std::sync::LazyLock;

static EMAIL_REGEX: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$").unwrap()
});

pub fn validate_email(email: &str) -> Result<(), ValidationError> {
    if email.is_empty() {
        return Err(ValidationError::Empty);
    }
    if !EMAIL_REGEX.is_match(email) {
        return Err(ValidationError::InvalidFormat);
    }
    Ok(())
}
```

## Step 5: Run Tests - Verify PASS

```bash
$ cargo test

running 9 tests
test tests::valid_simple_email ... ok
test tests::valid_email_with_subdomain ... ok
test tests::valid_email_with_plus ... ok
test tests::valid_email_with_dots ... ok
test tests::empty_email_returns_error ... ok
test tests::no_at_sign_returns_error ... ok
test tests::no_domain_returns_error ... ok
test tests::no_local_part_returns_error ... ok
test tests::spaces_returns_error ... ok

test result: ok. 9 passed; 0 failed
```

✓ All tests passing!

## Step 6: Check Coverage

```bash
$ cargo tarpaulin -p my_crate --lib

|| Tested/Total Lines:
|| src/validator.rs: 6/6 100.00%
||
100.00% coverage, 6/6 lines covered
```

✓ Coverage: 100%

## TDD Complete!
```

## Test Patterns

### Unit Tests (inline)
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_case() {
        assert_eq!(function(input), expected);
    }

    #[test]
    #[should_panic(expected = "out of bounds")]
    fn test_panic_case() {
        function(invalid_input);
    }
}
```

### Parameterized-Style Tests
```rust
#[test]
fn test_multiple_cases() {
    let cases = vec![
        ("input1", expected1),
        ("input2", expected2),
        ("input3", expected3),
    ];

    for (input, expected) in cases {
        assert_eq!(
            function(input), expected,
            "failed for input: {input}"
        );
    }
}
```

### Async Tests
```rust
#[tokio::test]
async fn test_async_operation() {
    let result = async_function().await;
    assert!(result.is_ok());
}
```

### Integration Tests
```rust
// tests/integration.rs
use my_crate::{Config, App};

#[test]
fn test_full_workflow() {
    let app = App::new(Config::test());
    let result = app.process("input");
    assert_eq!(result.status, Status::Complete);
}
```

### Property-Based Tests
```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_roundtrip(input in "[a-zA-Z0-9]{1,100}") {
        let encoded = encode(&input);
        let decoded = decode(&encoded).unwrap();
        prop_assert_eq!(input, decoded);
    }
}
```

## Coverage Commands

```bash
# Using cargo-tarpaulin
cargo tarpaulin
cargo tarpaulin --out html
cargo tarpaulin --fail-under 80

# Using cargo-llvm-cov
cargo llvm-cov
cargo llvm-cov --html
cargo llvm-cov --branch
```

## Coverage Targets

| Code Type | Target |
|-----------|--------|
| Critical business logic | 100% |
| Public APIs | 90%+ |
| General code | 80%+ |
| Generated code | Exclude |

## TDD Best Practices

**DO:**
- Write test FIRST, before any implementation
- Run tests after each change
- Use `assert_eq!` over `assert!` for better error messages
- Include edge cases (empty, None, max values, unicode)
- Test error paths, not just happy paths
- Use `#[should_panic]` for expected panics

**DON'T:**
- Write implementation before tests
- Skip the RED phase
- Test private functions directly (test through public API)
- Use `sleep()` in tests (use channels or async)
- Ignore flaky tests
- Use `unwrap()` only in tests, never in production code

## Related Commands

- `/rust-build` - Fix build errors
- `/rust-review` - Review code after implementation
- `/verify` - Run full verification loop

## Related

- Skill: `skills/rust-testing/`
- Skill: `skills/tdd-workflow/`
