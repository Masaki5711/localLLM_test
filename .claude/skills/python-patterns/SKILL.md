---
description: Idiomatic Python patterns, best practices, and conventions for building robust, maintainable Python applications.
user_invocable: true
---

# Python Patterns

## Core Principles

1. **Explicit is better than implicit** (Zen of Python)
2. **Type hints everywhere** — `def func(x: int) -> str:`
3. **Immutability preferred** — dataclasses with `frozen=True`, tuple over list
4. **Composition over inheritance** — Protocol/ABC over deep class hierarchies

## Project Structure

```
project/
├── pyproject.toml          # Project config (PEP 621)
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── models.py       # Data models (Pydantic/dataclass)
│       ├── services.py     # Business logic
│       ├── repository.py   # Data access
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py   # API endpoints
│       └── utils.py        # Pure utility functions
├── tests/
│   ├── conftest.py         # Shared fixtures
│   ├── test_models.py
│   ├── test_services.py
│   └── integration/
│       └── test_api.py
└── .env.example
```

## Type Hints

```python
from typing import Protocol, TypeVar, Generic
from collections.abc import Sequence, Mapping

# Use built-in generics (Python 3.10+)
def process(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Union types (Python 3.10+)
def find(id: int) -> User | None:
    ...

# Protocol for structural typing
class Repository(Protocol):
    def find_by_id(self, id: int) -> Model | None: ...
    def save(self, entity: Model) -> Model: ...

# TypeVar for generics
T = TypeVar("T")

class Result(Generic[T]):
    def __init__(self, value: T | None = None, error: str | None = None):
        self.value = value
        self.error = error
```

## Data Models

```python
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

# Immutable data (internal)
@dataclass(frozen=True)
class UserId:
    value: int

# Pydantic for API/validation
class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r"^[\w.-]+@[\w.-]+\.\w+$")
    age: int = Field(ge=0, le=150)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}
```

## Error Handling

```python
# Custom exceptions with hierarchy
class AppError(Exception):
    """Base application error."""

class NotFoundError(AppError):
    def __init__(self, entity: str, id: int):
        super().__init__(f"{entity} with id={id} not found")
        self.entity = entity
        self.id = id

class ValidationError(AppError):
    def __init__(self, field: str, message: str):
        super().__init__(f"Validation failed for {field}: {message}")

# Usage
def get_user(user_id: int) -> User:
    user = repository.find_by_id(user_id)
    if user is None:
        raise NotFoundError("User", user_id)
    return user
```

## Async Patterns

```python
import asyncio
import httpx

# Async context manager
async def fetch_data(urls: list[str]) -> list[dict]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

# Async generator
async def stream_events(source: EventSource) -> AsyncIterator[Event]:
    async for raw in source.listen():
        event = parse_event(raw)
        if event.is_valid():
            yield event

# Graceful shutdown
async def main():
    try:
        await run_server()
    except asyncio.CancelledError:
        logger.info("Shutting down gracefully")
    finally:
        await cleanup()
```

## Dependency Injection

```python
from dataclasses import dataclass

@dataclass
class UserService:
    repository: UserRepository
    email_client: EmailClient

    def create_user(self, request: CreateUserRequest) -> User:
        user = User(name=request.name, email=request.email)
        saved = self.repository.save(user)
        self.email_client.send_welcome(saved.email)
        return saved

# Composition at app startup
def create_app() -> Application:
    db = Database(os.environ["DATABASE_URL"])
    repo = SqlUserRepository(db)
    email = SmtpEmailClient(os.environ["SMTP_HOST"])
    service = UserService(repository=repo, email_client=email)
    return Application(user_service=service)
```

## Logging

```python
import logging
import structlog

# Structured logging
logger = structlog.get_logger(__name__)

def process_order(order_id: int) -> None:
    log = logger.bind(order_id=order_id)
    log.info("processing_order_started")
    try:
        result = _do_process(order_id)
        log.info("processing_order_completed", result=result)
    except Exception:
        log.exception("processing_order_failed")
        raise
```

## Performance Patterns

```python
from functools import lru_cache
from itertools import islice

# Caching
@lru_cache(maxsize=128)
def expensive_computation(key: str) -> Result:
    ...

# Generator for large datasets
def read_large_file(path: Path) -> Iterator[str]:
    with open(path) as f:
        for line in f:
            yield line.strip()

# Batch processing
def process_in_batches(items: Sequence[T], batch_size: int = 100) -> None:
    it = iter(items)
    while batch := list(islice(it, batch_size)):
        process_batch(batch)

# __slots__ for memory efficiency
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
```

## Anti-Patterns to Avoid

| Anti-Pattern | Fix |
|-------------|-----|
| `from module import *` | Import specific names |
| Mutable default args `def f(x=[])` | Use `None` sentinel |
| Bare `except:` | Catch specific exceptions |
| `type(x) == int` | `isinstance(x, int)` |
| `== None` | `is None` |
| `os.path` for new code | `pathlib.Path` |
| Global mutable state | Dependency injection |
| `print()` for logging | `logging` / `structlog` |
| Deep inheritance | Composition + Protocol |
| `pickle` for untrusted data | `json` / `msgpack` |

## Quick Reference

```python
# Comprehensions over loops
squares = [x**2 for x in range(10)]
evens = {x for x in items if x % 2 == 0}
lookup = {item.id: item for item in items}

# Context managers
with open("file.txt") as f, db.transaction() as tx:
    ...

# Walrus operator (3.8+)
if (n := len(items)) > 10:
    print(f"Too many items: {n}")

# match statement (3.10+)
match command:
    case {"action": "create", "name": str(name)}:
        create(name)
    case {"action": "delete", "id": int(id)}:
        delete(id)
    case _:
        raise ValueError("Unknown command")
```

## Tooling

```bash
# Formatter + Linter (all-in-one)
ruff check . --fix
ruff format .

# Type checking
mypy . --strict

# Security audit
pip-audit
bandit -r src/

# Dependency management
poetry install    # or: pip install -e ".[dev]"

# Virtual environment
python -m venv .venv && source .venv/bin/activate
```
