---
description: Python testing patterns including pytest, fixtures, parametrize, mocking, async testing, and coverage. Follows TDD methodology.
user_invocable: true
---

# Python Testing

## TDD Workflow

```
RED     → Write failing test with pytest assertions
GREEN   → Implement minimal code to pass
REFACTOR → Improve code, tests stay green
REPEAT  → Next test case
```

## Unit Tests

```python
# tests/test_validator.py
import pytest
from mypackage.validator import validate_email, ValidationError

class TestValidateEmail:
    def test_valid_email(self):
        assert validate_email("user@example.com") is True

    def test_empty_email_raises(self):
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_email("")

    def test_invalid_format_raises(self):
        with pytest.raises(ValidationError, match="invalid format"):
            validate_email("not-an-email")
```

## Parametrized Tests

```python
@pytest.mark.parametrize("input_email,expected", [
    ("user@example.com", True),
    ("user+tag@example.com", True),
    ("first.last@example.com", True),
    ("user@sub.domain.com", True),
])
def test_valid_emails(input_email: str, expected: bool):
    assert validate_email(input_email) == expected

@pytest.mark.parametrize("invalid_email", [
    "",
    "no-at-sign",
    "@no-local",
    "no-domain@",
    "spaces in@email.com",
])
def test_invalid_emails(invalid_email: str):
    with pytest.raises(ValidationError):
        validate_email(invalid_email)
```

## Fixtures

```python
# tests/conftest.py
import pytest
from mypackage.database import Database
from mypackage.models import User

@pytest.fixture
def db():
    """In-memory test database."""
    database = Database(":memory:")
    database.create_tables()
    yield database
    database.close()

@pytest.fixture
def sample_user() -> User:
    return User(id=1, name="Test User", email="test@example.com")

@pytest.fixture
def user_service(db) -> UserService:
    repo = SqlUserRepository(db)
    return UserService(repository=repo)
```

## Mocking

```python
from unittest.mock import Mock, patch, AsyncMock

# Mock object
def test_send_notification():
    email_client = Mock()
    service = NotificationService(email_client=email_client)

    service.notify_user(user_id=1, message="Hello")

    email_client.send.assert_called_once_with(
        to="user@example.com", body="Hello"
    )

# Patch decorator
@patch("mypackage.services.external_api")
def test_fetch_data(mock_api):
    mock_api.get.return_value = {"status": "ok"}
    result = fetch_data()
    assert result["status"] == "ok"

# Async mock
@pytest.mark.asyncio
async def test_async_service():
    client = AsyncMock()
    client.fetch.return_value = {"data": [1, 2, 3]}
    service = DataService(client=client)
    result = await service.get_data()
    assert result == [1, 2, 3]
```

## Async Testing

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_process("input")
    assert result.status == "complete"

@pytest.mark.asyncio
async def test_concurrent_processing():
    results = await asyncio.gather(
        process("a"),
        process("b"),
        process("c"),
    )
    assert all(r.is_ok() for r in results)
```

## Integration Tests

```python
# tests/integration/test_api.py
import pytest
from httpx import AsyncClient
from mypackage.app import create_app

@pytest.fixture
async def client():
    app = create_app(testing=True)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post("/api/users", json={
        "name": "Test User",
        "email": "test@example.com",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"

@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    response = await client.get("/api/users/999")
    assert response.status_code == 404
```

## Database Testing

```python
# Using testcontainers
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg.get_connection_url()

@pytest.fixture
def db_session(postgres):
    engine = create_engine(postgres)
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.rollback()
    session.close()
```

## Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_encode_decode_roundtrip(text: str):
    encoded = encode(text)
    decoded = decode(encoded)
    assert decoded == text

@given(st.integers(min_value=0, max_value=1000))
def test_positive_square(n: int):
    assert square(n) >= 0
```

## Coverage

```bash
# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Fail below threshold
pytest --cov=src --cov-fail-under=80

# Branch coverage
pytest --cov=src --cov-branch
```

| Code Type | Target |
|-----------|--------|
| Critical business logic | 100% |
| Public APIs | 90%+ |
| General code | 80%+ |
| Generated code | Exclude |

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_models.py       # Data model tests
│   ├── test_services.py     # Business logic tests
│   └── test_utils.py        # Utility tests
├── integration/
│   ├── test_api.py          # API endpoint tests
│   └── test_repository.py   # Database tests
└── e2e/
    └── test_workflows.py    # Full user flow tests
```

## Best Practices

**DO:**
- Write test FIRST before implementation
- Use descriptive test names: `test_create_user_with_invalid_email_raises`
- One assert per test (prefer)
- Use fixtures for setup/teardown
- Test edge cases: empty, None, max values, unicode
- Use `pytest.raises` for expected exceptions

**DON'T:**
- Write implementation before tests
- Use `sleep()` in tests
- Test private methods directly
- Share mutable state between tests
- Ignore flaky tests
- Use `print()` — use `capfd` fixture or logging
