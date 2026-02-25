---
name: rust-testing
description: Rust testing patterns including unit tests, integration tests, doc tests, property-based testing, benchmarks, and coverage. Follows TDD methodology with idiomatic Rust practices.
---

# Rust Testing Patterns

Comprehensive Rust testing patterns for writing reliable, maintainable tests following TDD methodology.

## When to Activate

- Writing new Rust functions or methods
- Adding test coverage to existing code
- Creating benchmarks for performance-critical code
- Implementing property-based tests for input validation
- Following TDD workflow in Rust projects

## TDD Workflow for Rust

### The RED-GREEN-REFACTOR Cycle

```
RED     → Write a failing test first
GREEN   → Write minimal code to pass the test
REFACTOR → Improve code while keeping tests green
REPEAT  → Continue with next requirement
```

### Step-by-Step TDD in Rust

```rust
// Step 1: Define the function signature
// src/calculator.rs
pub fn add(a: i32, b: i32) -> i32 {
    todo!() // Placeholder
}

// Step 2: Write failing test (RED)
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }
}

// Step 3: Run test - verify FAIL
// $ cargo test
// thread 'tests::test_add' panicked at 'not yet implemented'

// Step 4: Implement minimal code (GREEN)
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

// Step 5: Run test - verify PASS
// $ cargo test
// test tests::test_add ... ok

// Step 6: Refactor if needed, verify tests still pass
```

## Unit Tests

### Basic Unit Test Structure

```rust
// src/validator.rs
pub fn validate_email(email: &str) -> Result<(), ValidationError> {
    if email.is_empty() {
        return Err(ValidationError::Empty);
    }
    if !email.contains('@') {
        return Err(ValidationError::MissingAt);
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn valid_email() {
        assert!(validate_email("user@example.com").is_ok());
    }

    #[test]
    fn empty_email_returns_error() {
        assert!(matches!(
            validate_email(""),
            Err(ValidationError::Empty)
        ));
    }

    #[test]
    fn email_without_at_returns_error() {
        assert!(matches!(
            validate_email("userexample.com"),
            Err(ValidationError::MissingAt)
        ));
    }
}
```

### Testing with Multiple Cases (Parameterized-Style)

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_valid_inputs() {
        let cases = vec![
            ("42", 42),
            ("0", 0),
            ("-1", -1),
            ("1000000", 1_000_000),
        ];

        for (input, expected) in cases {
            assert_eq!(
                parse_number(input).unwrap(),
                expected,
                "failed for input: {input}"
            );
        }
    }

    #[test]
    fn test_parse_invalid_inputs() {
        let cases = vec!["", "abc", "12.34", "99999999999999999999"];

        for input in cases {
            assert!(
                parse_number(input).is_err(),
                "expected error for input: {input}"
            );
        }
    }
}
```

### Testing Panics

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic(expected = "index out of bounds")]
    fn test_out_of_bounds_panics() {
        let v = vec![1, 2, 3];
        let _ = v[10];
    }

    #[test]
    #[should_panic(expected = "division by zero")]
    fn test_divide_by_zero_panics() {
        divide(10, 0);
    }
}
```

### Ignoring Tests

```rust
#[test]
#[ignore] // Skip by default, run with: cargo test -- --ignored
fn expensive_integration_test() {
    // Long-running test
}
```

## Integration Tests

### tests/ Directory Structure

```text
my_project/
├── src/
│   └── lib.rs
├── tests/
│   ├── common/
│   │   └── mod.rs      # Shared test utilities
│   ├── api_tests.rs     # API integration tests
│   └── db_tests.rs      # Database integration tests
```

### Integration Test Example

```rust
// tests/common/mod.rs
pub fn setup_test_db() -> TestDb {
    let db = TestDb::new("test.db");
    db.migrate();
    db
}

// tests/api_tests.rs
mod common;

use my_project::{create_app, Config};

#[tokio::test]
async fn test_health_endpoint() {
    let app = create_app(Config::test()).await;
    let response = app.get("/health").await;
    assert_eq!(response.status(), 200);
    assert_eq!(response.text(), "OK");
}

#[tokio::test]
async fn test_create_user() {
    let db = common::setup_test_db();
    let app = create_app(Config::test_with_db(db)).await;

    let response = app
        .post("/users")
        .json(&serde_json::json!({"name": "Alice", "email": "alice@example.com"}))
        .await;

    assert_eq!(response.status(), 201);

    let user: User = response.json().await;
    assert_eq!(user.name, "Alice");
    assert!(!user.id.is_empty());
}
```

## Doc Tests

### Testable Documentation Examples

```rust
/// Adds two numbers together.
///
/// # Examples
///
/// ```
/// use my_crate::add;
///
/// assert_eq!(add(2, 3), 5);
/// assert_eq!(add(-1, 1), 0);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

/// Parses a string into a configuration.
///
/// # Errors
///
/// Returns `ParseError` if the input is not valid TOML.
///
/// # Examples
///
/// ```
/// use my_crate::parse_config;
///
/// let config = parse_config("[server]\nport = 8080").unwrap();
/// assert_eq!(config.server.port, 8080);
/// ```
///
/// ```should_panic
/// use my_crate::parse_config;
///
/// // Invalid TOML will cause an error
/// parse_config("{{invalid}}").unwrap();
/// ```
pub fn parse_config(input: &str) -> Result<Config, ParseError> {
    // ...
}
```

## Property-Based Testing with proptest

### Basic Property Tests

```rust
#[cfg(test)]
mod tests {
    use proptest::prelude::*;

    proptest! {
        #[test]
        fn test_add_commutative(a in any::<i32>(), b in any::<i32>()) {
            // Addition is commutative
            prop_assert_eq!(add(a, b), add(b, a));
        }

        #[test]
        fn test_add_identity(a in any::<i32>()) {
            // Zero is the identity element
            prop_assert_eq!(add(a, 0), a);
        }

        #[test]
        fn test_serialize_roundtrip(s in "[a-zA-Z0-9]{1,100}") {
            let serialized = serialize(&s);
            let deserialized = deserialize(&serialized).unwrap();
            prop_assert_eq!(s, deserialized);
        }
    }
}
```

### Custom Strategies

```rust
use proptest::prelude::*;

fn valid_email_strategy() -> impl Strategy<Value = String> {
    (
        "[a-zA-Z][a-zA-Z0-9._%+-]{0,20}",
        "[a-zA-Z][a-zA-Z0-9.-]{0,10}",
        "(com|org|net|io)",
    )
        .prop_map(|(local, domain, tld)| format!("{}@{}.{}", local, domain, tld))
}

proptest! {
    #[test]
    fn test_valid_emails_pass_validation(email in valid_email_strategy()) {
        prop_assert!(validate_email(&email).is_ok());
    }

    #[test]
    fn test_parse_never_panics(input in ".*") {
        // Should never panic, may return error
        let _ = parse_input(&input);
    }
}
```

## Mocking with mockall

### Trait-Based Mocking

```rust
use mockall::automock;

#[automock]
trait UserRepository {
    fn find_by_id(&self, id: &str) -> Result<User, Error>;
    fn save(&self, user: &User) -> Result<(), Error>;
}

#[cfg(test)]
mod tests {
    use super::*;
    use mockall::predicate::*;

    #[test]
    fn test_get_user_profile() {
        let mut mock = MockUserRepository::new();

        mock.expect_find_by_id()
            .with(eq("123"))
            .times(1)
            .returning(|_| Ok(User {
                id: "123".to_string(),
                name: "Alice".to_string(),
            }));

        let service = UserService::new(Box::new(mock));
        let profile = service.get_profile("123").unwrap();

        assert_eq!(profile.name, "Alice");
    }

    #[test]
    fn test_user_not_found() {
        let mut mock = MockUserRepository::new();

        mock.expect_find_by_id()
            .with(eq("999"))
            .times(1)
            .returning(|id| Err(Error::NotFound(id.to_string())));

        let service = UserService::new(Box::new(mock));
        let result = service.get_profile("999");

        assert!(matches!(result, Err(Error::NotFound(_))));
    }
}
```

## Async Test Patterns

### Testing with tokio

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_async_fetch() {
        let client = TestClient::new();
        let result = client.fetch("https://example.com").await;
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_concurrent_operations() {
        let (tx, mut rx) = tokio::sync::mpsc::channel(10);

        tokio::spawn(async move {
            tx.send("hello").await.unwrap();
        });

        let received = rx.recv().await.unwrap();
        assert_eq!(received, "hello");
    }

    #[tokio::test(flavor = "multi_thread", worker_threads = 2)]
    async fn test_multithreaded() {
        // Test that requires actual multi-threading
    }
}
```

## Benchmarks with criterion

### Basic Benchmarks

```rust
// benches/benchmark.rs
use criterion::{criterion_group, criterion_main, Criterion, black_box};

fn bench_process(c: &mut Criterion) {
    let data = generate_test_data(1000);

    c.bench_function("process_1000", |b| {
        b.iter(|| process(black_box(&data)))
    });
}

fn bench_with_sizes(c: &mut Criterion) {
    let mut group = c.benchmark_group("sort");

    for size in [100, 1000, 10000] {
        let data = generate_random_vec(size);
        group.bench_with_input(
            criterion::BenchmarkId::new("quicksort", size),
            &data,
            |b, data| {
                b.iter(|| {
                    let mut copy = data.clone();
                    quicksort(&mut copy);
                })
            },
        );
    }

    group.finish();
}

criterion_group!(benches, bench_process, bench_with_sizes);
criterion_main!(benches);
```

```toml
# Cargo.toml
[[bench]]
name = "benchmark"
harness = false

[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }
```

## Test Coverage

### Using cargo-tarpaulin

```bash
# Install
cargo install cargo-tarpaulin

# Basic coverage
cargo tarpaulin

# With HTML report
cargo tarpaulin --out html

# Specific package in workspace
cargo tarpaulin -p my_crate

# Exclude test files from coverage
cargo tarpaulin --ignore-tests

# With minimum threshold
cargo tarpaulin --fail-under 80
```

### Using cargo-llvm-cov

```bash
# Install
cargo install cargo-llvm-cov

# Basic coverage
cargo llvm-cov

# HTML report
cargo llvm-cov --html

# With branch coverage
cargo llvm-cov --branch

# JSON output for CI
cargo llvm-cov --json --output-path coverage.json
```

### Coverage Targets

| Code Type | Target |
|-----------|--------|
| Critical business logic | 100% |
| Public APIs | 90%+ |
| General code | 80%+ |
| Generated code | Exclude |

## Test Fixtures and Helpers

### Test Utilities Module

```rust
// src/test_utils.rs (or tests/common/mod.rs)
#[cfg(test)]
pub mod test_utils {
    use super::*;

    pub fn create_test_user(name: &str) -> User {
        User {
            id: uuid::Uuid::new_v4().to_string(),
            name: name.to_string(),
            email: format!("{}@test.com", name.to_lowercase()),
            created_at: chrono::Utc::now(),
        }
    }

    pub struct TestDb {
        pool: sqlx::SqlitePool,
    }

    impl TestDb {
        pub async fn new() -> Self {
            let pool = sqlx::SqlitePool::connect(":memory:").await.unwrap();
            sqlx::migrate!().run(&pool).await.unwrap();
            Self { pool }
        }

        pub fn pool(&self) -> &sqlx::SqlitePool {
            &self.pool
        }
    }
}
```

### Temporary Files in Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_file_processing() {
        let tmp_dir = TempDir::new().unwrap();
        let file_path = tmp_dir.path().join("test.txt");

        std::fs::write(&file_path, "test content").unwrap();

        let result = process_file(&file_path).unwrap();
        assert_eq!(result.line_count, 1);
        // tmp_dir dropped here, files cleaned up automatically
    }
}
```

## Testing Commands

```bash
# Run all tests
cargo test

# Run tests with output shown
cargo test -- --nocapture

# Run specific test
cargo test test_add

# Run tests matching pattern
cargo test validate_

# Run tests in specific module
cargo test validator::tests

# Run only integration tests
cargo test --test integration

# Run only doc tests
cargo test --doc

# Run ignored tests
cargo test -- --ignored

# Run all tests including ignored
cargo test -- --include-ignored

# Run benchmarks
cargo bench

# Run tests with release optimizations
cargo test --release

# Run specific number of test threads
cargo test -- --test-threads=1
```

## CI/CD Integration

```yaml
# GitHub Actions example
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: dtolnay/rust-toolchain@stable

    - name: Run tests
      run: cargo test --all-features

    - name: Run clippy
      run: cargo clippy -- -D warnings

    - name: Check formatting
      run: cargo fmt -- --check

    - name: Check coverage
      run: |
        cargo install cargo-tarpaulin
        cargo tarpaulin --fail-under 80
```

## Best Practices

**DO:**
- Write tests FIRST (TDD)
- Use `#[cfg(test)]` for test-only code
- Test behavior, not implementation
- Use meaningful assertion messages
- Include edge cases (empty, max values, unicode)
- Use `assert_eq!` over `assert!` for better error messages
- Test error paths, not just happy paths
- Use proptest for input validation code

**DON'T:**
- Use `unwrap()` in production code (OK in tests)
- Skip testing error variants
- Use `sleep()` in tests (use channels, barriers, or async)
- Mock everything (prefer integration tests when possible)
- Ignore flaky tests (fix or remove them)
- Test private functions directly (test through public API)

**Remember**: Tests are documentation. They show how your code is meant to be used. Write them clearly and keep them up to date.
