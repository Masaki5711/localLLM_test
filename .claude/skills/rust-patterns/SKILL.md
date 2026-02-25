---
name: rust-patterns
description: Idiomatic Rust patterns, best practices, and conventions for building safe, performant, and maintainable Rust applications.
---

# Rust Development Patterns

Idiomatic Rust patterns and best practices for building safe, performant, and maintainable applications.

## When to Activate

- Writing new Rust code
- Reviewing Rust code
- Refactoring existing Rust code
- Designing Rust crates/modules

## Core Principles

### 1. Ownership and Borrowing

Rust's ownership system is the foundation. Understand move semantics, borrowing, and lifetimes.

```rust
// Good: Clear ownership transfer
fn process_data(data: Vec<u8>) -> Result<Output, Error> {
    // data is owned here, will be dropped when function ends
    let parsed = parse(&data)?;
    Ok(transform(parsed))
}

// Good: Borrowing when ownership isn't needed
fn validate(data: &[u8]) -> bool {
    !data.is_empty() && data.len() < MAX_SIZE
}

// Bad: Unnecessary clone
fn bad_process(data: &Vec<u8>) -> Result<Output, Error> {
    let owned = data.clone(); // Unnecessary allocation!
    process_data(owned)
}
```

### 2. Use &str Over String for Parameters

Accept `&str` for read-only string parameters, return `String` when ownership is needed.

```rust
// Good: Accept &str, return String
fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

// Good: Accept Into<String> for flexible API
fn set_name(&mut self, name: impl Into<String>) {
    self.name = name.into();
}

// Bad: Forcing caller to allocate
fn greet_bad(name: String) -> String {
    format!("Hello, {}!", name)
}
```

### 3. Make Invalid States Unrepresentable

Use the type system to prevent invalid states at compile time.

```rust
// Good: Type-safe state machine
struct Draft;
struct Published;
struct Archived;

struct Article<State> {
    title: String,
    content: String,
    _state: std::marker::PhantomData<State>,
}

impl Article<Draft> {
    fn publish(self) -> Article<Published> {
        Article {
            title: self.title,
            content: self.content,
            _state: std::marker::PhantomData,
        }
    }
}

impl Article<Published> {
    fn archive(self) -> Article<Archived> {
        Article {
            title: self.title,
            content: self.content,
            _state: std::marker::PhantomData,
        }
    }
}

// Bad: Runtime state checks
struct BadArticle {
    state: String, // "draft", "published", "archived"
    // Easy to have invalid state like "publshed"
}
```

## Error Handling Patterns

### Result and the ? Operator

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("configuration error: {0}")]
    Config(String),

    #[error("database error")]
    Database(#[from] sqlx::Error),

    #[error("I/O error")]
    Io(#[from] std::io::Error),

    #[error("not found: {0}")]
    NotFound(String),
}

// Good: Use ? for propagation with context
fn load_config(path: &str) -> Result<Config, AppError> {
    let content = std::fs::read_to_string(path)?; // io::Error -> AppError::Io
    let config: Config = toml::from_str(&content)
        .map_err(|e| AppError::Config(format!("parse {}: {}", path, e)))?;
    Ok(config)
}
```

### Using anyhow for Application Code

```rust
use anyhow::{Context, Result};

// Good: anyhow for application-level error handling
fn setup() -> Result<()> {
    let config = load_config("config.toml")
        .context("failed to load configuration")?;

    let db = connect_database(&config.database_url)
        .context("failed to connect to database")?;

    Ok(())
}
```

### Using thiserror for Library Code

```rust
use thiserror::Error;

// Good: thiserror for library error types
#[derive(Error, Debug)]
pub enum ParseError {
    #[error("invalid header at byte {position}")]
    InvalidHeader { position: usize },

    #[error("unexpected EOF, expected {expected} bytes")]
    UnexpectedEof { expected: usize },

    #[error("checksum mismatch: expected {expected:#x}, got {actual:#x}")]
    ChecksumMismatch { expected: u32, actual: u32 },
}
```

### Avoiding unwrap()

```rust
// Bad: Panics on None/Err
let value = map.get("key").unwrap();
let data = file.read_to_string().unwrap();

// Good: Handle with ? or explicit matching
let value = map.get("key").ok_or(AppError::NotFound("key".into()))?;
let data = file.read_to_string()?;

// Good: unwrap_or / unwrap_or_default for safe defaults
let value = map.get("key").unwrap_or(&default_value);
let count = parse_count(input).unwrap_or_default();

// Acceptable: unwrap with expect for guaranteed invariants
let regex = Regex::new(r"^\d+$").expect("hardcoded regex must compile");
```

## Trait Design

### Small, Focused Traits

```rust
// Good: Single-responsibility traits
trait Validate {
    fn validate(&self) -> Result<(), ValidationError>;
}

trait Serialize {
    fn serialize(&self) -> Vec<u8>;
}

trait Deserialize: Sized {
    fn deserialize(data: &[u8]) -> Result<Self, ParseError>;
}

// Compose when needed
trait Message: Validate + Serialize {}
```

### Default Implementations

```rust
trait Logger {
    fn log(&self, message: &str);

    // Default implementation using the required method
    fn log_error(&self, error: &dyn std::error::Error) {
        self.log(&format!("ERROR: {}", error));
    }

    fn log_info(&self, message: &str) {
        self.log(&format!("INFO: {}", message));
    }
}
```

### Generics with Trait Bounds

```rust
// Good: Trait bounds for generic functions
fn process<T: Serialize + Validate>(item: T) -> Result<Vec<u8>, Error> {
    item.validate()?;
    Ok(item.serialize())
}

// Good: where clause for complex bounds
fn merge<T, U>(left: T, right: U) -> T
where
    T: Merge<U> + Clone,
    U: Into<T>,
{
    left.merge(right)
}
```

## Struct Design Patterns

### Builder Pattern

```rust
#[derive(Debug)]
pub struct Server {
    addr: String,
    port: u16,
    max_connections: usize,
    timeout: std::time::Duration,
}

#[derive(Default)]
pub struct ServerBuilder {
    addr: Option<String>,
    port: Option<u16>,
    max_connections: Option<usize>,
    timeout: Option<std::time::Duration>,
}

impl ServerBuilder {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn addr(mut self, addr: impl Into<String>) -> Self {
        self.addr = Some(addr.into());
        self
    }

    pub fn port(mut self, port: u16) -> Self {
        self.port = Some(port);
        self
    }

    pub fn max_connections(mut self, max: usize) -> Self {
        self.max_connections = Some(max);
        self
    }

    pub fn timeout(mut self, timeout: std::time::Duration) -> Self {
        self.timeout = Some(timeout);
        self
    }

    pub fn build(self) -> Result<Server, &'static str> {
        Ok(Server {
            addr: self.addr.unwrap_or_else(|| "127.0.0.1".to_string()),
            port: self.port.unwrap_or(8080),
            max_connections: self.max_connections.unwrap_or(100),
            timeout: self.timeout.unwrap_or(std::time::Duration::from_secs(30)),
        })
    }
}

// Usage
let server = ServerBuilder::new()
    .addr("0.0.0.0")
    .port(3000)
    .max_connections(500)
    .build()?;
```

### Newtype Pattern

```rust
// Good: Type safety through newtypes
struct UserId(u64);
struct OrderId(u64);

// Cannot accidentally pass OrderId where UserId is expected
fn get_user(id: UserId) -> Result<User, Error> {
    // ...
}

// Implement Display, From, etc. as needed
impl std::fmt::Display for UserId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "user:{}", self.0)
    }
}
```

## Concurrency Patterns

### Arc and Mutex for Shared State

```rust
use std::sync::{Arc, Mutex, RwLock};

// Good: Arc<Mutex<T>> for shared mutable state
struct AppState {
    cache: Arc<RwLock<HashMap<String, String>>>,
    counter: Arc<Mutex<u64>>,
}

impl AppState {
    fn increment(&self) -> u64 {
        let mut counter = self.counter.lock().unwrap();
        *counter += 1;
        *counter
    }

    fn get_cached(&self, key: &str) -> Option<String> {
        let cache = self.cache.read().unwrap();
        cache.get(key).cloned()
    }

    fn set_cached(&self, key: String, value: String) {
        let mut cache = self.cache.write().unwrap();
        cache.insert(key, value);
    }
}
```

### Channels for Message Passing

```rust
use std::sync::mpsc;
use std::thread;

// Good: Channel-based communication
fn worker_pool(jobs: Vec<Job>) -> Vec<Result<Output, Error>> {
    let (tx, rx) = mpsc::channel();
    let num_workers = num_cpus::get();

    let jobs = Arc::new(Mutex::new(jobs.into_iter()));

    for _ in 0..num_workers {
        let tx = tx.clone();
        let jobs = Arc::clone(&jobs);

        thread::spawn(move || {
            loop {
                let job = {
                    let mut jobs = jobs.lock().unwrap();
                    jobs.next()
                };
                match job {
                    Some(job) => tx.send(process(job)).unwrap(),
                    None => break,
                }
            }
        });
    }

    drop(tx); // Close sender so rx.iter() terminates
    rx.iter().collect()
}
```

### Async with Tokio

```rust
use tokio::sync::Semaphore;
use std::sync::Arc;

// Good: Async with bounded concurrency
async fn fetch_all(urls: Vec<String>, max_concurrent: usize) -> Vec<Result<Response, Error>> {
    let semaphore = Arc::new(Semaphore::new(max_concurrent));
    let mut handles = Vec::new();

    for url in urls {
        let permit = semaphore.clone().acquire_owned().await.unwrap();
        handles.push(tokio::spawn(async move {
            let result = reqwest::get(&url).await;
            drop(permit);
            result.map_err(Error::from)
        }));
    }

    let mut results = Vec::new();
    for handle in handles {
        results.push(handle.await.unwrap());
    }
    results
}
```

### Graceful Shutdown

```rust
use tokio::signal;
use tokio::sync::watch;

async fn run_server() -> Result<(), Error> {
    let (shutdown_tx, shutdown_rx) = watch::channel(false);

    let server = tokio::spawn(async move {
        let mut rx = shutdown_rx;
        loop {
            tokio::select! {
                _ = rx.changed() => {
                    println!("Shutting down...");
                    break;
                }
                _ = handle_request() => {}
            }
        }
    });

    signal::ctrl_c().await?;
    let _ = shutdown_tx.send(true);
    server.await?;
    Ok(())
}
```

## Performance Patterns

### Zero-Cost Abstractions with Iterators

```rust
// Good: Iterator chains - compiled to efficient code
fn sum_of_squares(data: &[i64]) -> i64 {
    data.iter()
        .filter(|&&x| x > 0)
        .map(|&x| x * x)
        .sum()
}

// Good: Collect into specific types
fn unique_names(users: &[User]) -> Vec<&str> {
    users.iter()
        .map(|u| u.name.as_str())
        .collect::<HashSet<_>>()
        .into_iter()
        .collect()
}
```

### Cow for Flexible Ownership

```rust
use std::borrow::Cow;

// Good: Cow avoids allocation when possible
fn normalize(input: &str) -> Cow<'_, str> {
    if input.contains(' ') {
        Cow::Owned(input.replace(' ', "_"))
    } else {
        Cow::Borrowed(input)
    }
}

// Usage: no allocation if no spaces
let result = normalize("hello"); // Borrowed, zero-cost
let result = normalize("hello world"); // Owned, allocates only when needed
```

### Vec Pre-allocation

```rust
// Bad: Multiple reallocations
let mut results = Vec::new();
for item in items {
    results.push(process(item));
}

// Good: Single allocation
let mut results = Vec::with_capacity(items.len());
for item in items {
    results.push(process(item));
}

// Best: Use collect (handles capacity automatically)
let results: Vec<_> = items.iter().map(process).collect();
```

### Avoiding Unnecessary Clones

```rust
// Bad: Cloning when borrowing works
fn contains_name(users: &[User], name: &str) -> bool {
    let names: Vec<String> = users.iter().map(|u| u.name.clone()).collect();
    names.contains(&name.to_string())
}

// Good: Work with references
fn contains_name(users: &[User], name: &str) -> bool {
    users.iter().any(|u| u.name == name)
}
```

## Project Structure

### Standard Cargo Layout

```text
my_project/
├── Cargo.toml
├── Cargo.lock
├── src/
│   ├── main.rs          # Binary entry point
│   ├── lib.rs           # Library root
│   ├── config.rs        # Configuration
│   ├── error.rs         # Error types
│   ├── models/
│   │   ├── mod.rs
│   │   ├── user.rs
│   │   └── order.rs
│   ├── handlers/
│   │   ├── mod.rs
│   │   └── api.rs
│   └── services/
│       ├── mod.rs
│       └── auth.rs
├── tests/               # Integration tests
│   └── integration.rs
├── benches/             # Benchmarks
│   └── bench.rs
└── examples/            # Example binaries
    └── basic.rs
```

### Workspace Layout

```toml
# Cargo.toml (workspace root)
[workspace]
members = [
    "crates/core",
    "crates/api",
    "crates/cli",
]

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
```

### Module Organization

```rust
// src/lib.rs
pub mod config;
pub mod error;
pub mod models;
pub mod handlers;
pub mod services;

// Re-export commonly used types
pub use error::AppError;
pub use config::Config;
```

## Cargo Tooling Integration

### Essential Commands

```bash
# Build and run
cargo build
cargo run
cargo run --release

# Testing
cargo test
cargo test -- --nocapture
cargo test specific_test_name

# Linting and formatting
cargo fmt
cargo clippy -- -D warnings

# Dependencies
cargo update
cargo audit
cargo outdated

# Documentation
cargo doc --open
```

### Recommended Clippy Configuration (clippy.toml)

```toml
# clippy.toml
cognitive-complexity-threshold = 25
```

```toml
# Cargo.toml
[lints.clippy]
pedantic = "warn"
unwrap_used = "deny"
expect_used = "warn"
```

## Quick Reference: Rust Idioms

| Idiom | Description |
|-------|-------------|
| Ownership over GC | Use ownership and borrowing instead of garbage collection |
| Error as values | Use Result<T, E> and Option<T>, not exceptions |
| Make invalid states unrepresentable | Leverage the type system for correctness |
| Zero-cost abstractions | Iterators, generics, traits compile to efficient code |
| Fearless concurrency | Compiler prevents data races at compile time |
| Prefer &str over String | Borrow strings when ownership isn't needed |
| Use clippy | `cargo clippy` catches common mistakes |
| Derive common traits | #[derive(Debug, Clone, PartialEq)] |
| Pattern matching | Use match and if let for exhaustive handling |

## Anti-Patterns to Avoid

```rust
// Bad: Using unwrap() in production code
let value = data.get("key").unwrap();

// Bad: Ignoring errors with let _ =
let _ = important_operation();

// Bad: Using String when &str suffices
fn process(data: String) { /* only reads data */ }

// Bad: Cloning to satisfy borrow checker without understanding why
let data = shared_data.clone(); // Understand the ownership first!

// Bad: Using Rc<RefCell<T>> everywhere
// Usually indicates a design issue - prefer ownership restructuring

// Bad: Deeply nested match expressions
match a {
    Some(b) => match b {
        Some(c) => match c { /* ... */ }
        None => { /* ... */ }
    }
    None => { /* ... */ }
}
// Good: Use if let, ? operator, or and_then
let c = a.as_ref().and_then(|b| b.as_ref())?;
```

**Remember**: Rust's compiler is your ally. If the code compiles, it's free of data races, null pointer dereferences, and use-after-free bugs. Embrace the borrow checker, don't fight it.
