---
description: Fix Python import errors, mypy type errors, and environment issues incrementally. Invokes the python-build-resolver agent for minimal, surgical fixes.
---

# Python Build and Fix

This command invokes the **python-build-resolver** agent to incrementally fix Python build/type errors with minimal changes.

## What This Command Does

1. **Run Diagnostics**: Execute `mypy`, `python -m py_compile`, `pip check`
2. **Parse Errors**: Group by file and sort by severity
3. **Fix Incrementally**: One error at a time
4. **Verify Each Fix**: Re-run mypy after each change
5. **Report Summary**: Show what was fixed and what remains

## When to Use

- `mypy` reports type errors
- `ImportError` / `ModuleNotFoundError` occurs
- `pip install` or `poetry install` fails
- After pulling changes that break imports

## Diagnostic Commands Run

```bash
mypy . --strict 2>&1
python -m py_compile src/main.py
pip check
python --version && pip list
```

## Common Errors Fixed

| Error | Typical Fix |
|-------|-------------|
| `ModuleNotFoundError` | `pip install` or fix import path |
| `Incompatible return type` | Fix annotation or return value |
| `Item "None" has no attribute` | Add None check |
| `Cannot assign to type` | Fix type annotation |
| `Missing type annotation` | Add type hints |
| `IndentationError` | Fix whitespace |

## Fix Strategy

1. **Type errors first** — mypy must pass
2. **Import errors second** — All modules must resolve
3. **Runtime errors third** — Fix obvious crashes
4. **One fix at a time** — Verify each change
5. **Minimal changes** — Don't refactor, just fix

## Related

- Agent: `agents/python-build-resolver.md`
- Skill: `skills/python-patterns/`
