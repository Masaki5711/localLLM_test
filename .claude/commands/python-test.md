---
description: Enforce TDD workflow for Python. Write pytest tests first, then implement. Verify 80%+ coverage with pytest-cov.
---

# Python TDD Command

This command enforces test-driven development methodology for Python code using pytest.

## What This Command Does

1. **Define Interfaces**: Scaffold function signatures and type hints first
2. **Write Tests**: Create comprehensive test cases with pytest (RED)
3. **Run Tests**: Verify tests fail for the right reason
4. **Implement Code**: Write minimal code to pass (GREEN)
5. **Refactor**: Improve while keeping tests green
6. **Check Coverage**: Ensure 80%+ coverage

## When to Use

- Implementing new Python functions or classes
- Adding test coverage to existing code
- Fixing bugs (write failing test first)
- Building critical business logic

## TDD Cycle

```
RED     → Write failing test with pytest assertions
GREEN   → Implement minimal code to pass
REFACTOR → Improve code, tests stay green
REPEAT  → Next test case
```

## Test Patterns

### Unit Tests
```python
def test_function_returns_expected():
    assert function(input) == expected
```

### Parametrized Tests
```python
@pytest.mark.parametrize("input,expected", [
    ("a", 1), ("b", 2), ("c", 3),
])
def test_multiple_cases(input, expected):
    assert function(input) == expected
```

### Exception Tests
```python
def test_raises_on_invalid_input():
    with pytest.raises(ValueError, match="invalid"):
        function(invalid_input)
```

### Async Tests
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result.is_ok()
```

## Coverage Commands

```bash
pytest --cov=src --cov-report=html --cov-fail-under=80
```

| Code Type | Target |
|-----------|--------|
| Critical business logic | 100% |
| Public APIs | 90%+ |
| General code | 80%+ |

## Related

- Skill: `skills/python-testing/`
- Skill: `skills/tdd-workflow/`
