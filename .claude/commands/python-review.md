---
description: Comprehensive Python code review for type safety, security, async patterns, error handling, and performance. Invokes the python-reviewer agent.
---

# Python Code Review

This command invokes the **python-reviewer** agent for comprehensive Python-specific code review.

## What This Command Does

1. **Identify Python Changes**: Find modified `.py` files via `git diff`
2. **Run Static Analysis**: Execute `ruff check`, `mypy`, `bandit`
3. **Security Scan**: Check for injection, pickle/eval, hardcoded secrets
4. **Type Safety Review**: Verify type hints, Optional handling, Protocol usage
5. **Async Review**: Check for blocking in async, missing await
6. **Generate Report**: Categorize issues by severity

## When to Use

- After writing or modifying Python code
- Before committing Python changes
- Reviewing pull requests with Python code

## Review Categories

### CRITICAL (Must Fix)
- SQL/Command injection vulnerabilities
- Hardcoded credentials
- `pickle.loads()` / `eval()` on untrusted data
- Bare `except:` swallowing all errors
- Missing type hints on public functions

### HIGH (Should Fix)
- Blocking I/O in async context
- Mutable default arguments
- Missing None checks on Optional types
- N+1 queries in ORM loops

### MEDIUM (Consider)
- `os.path` instead of `pathlib.Path`
- String concatenation in loops (use `join`)
- List comprehension where generator suffices
- Missing docstrings on public APIs

## Automated Checks Run

```bash
ruff check . --output-format=concise
mypy . --strict
bandit -r src/
ruff format --check .
pytest -v --tb=short
```

## Approval Criteria

| Status | Condition |
|--------|-----------|
| APPROVE | No CRITICAL or HIGH issues |
| WARNING | Only MEDIUM issues |
| BLOCK | CRITICAL or HIGH issues found |

## Related

- Agent: `agents/python-reviewer.md`
- Skills: `skills/python-patterns/`, `skills/python-testing/`
