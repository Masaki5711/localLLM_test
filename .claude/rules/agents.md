# Agent Orchestration

## Available Agents (22 agents)

### General Agents (10)

| Agent | Command | When to Use |
|-------|---------|-------------|
| planner | `/plan` | Complex features, refactoring |
| architect | — | Architectural decisions |
| tdd-guide | `/tdd` | New features, bug fixes |
| code-reviewer | `/code-review` | After writing code |
| security-reviewer | — | Before commits |
| build-error-resolver | `/build-fix` | When build fails |
| e2e-runner | `/e2e` | Critical user flows |
| refactor-cleaner | `/refactor-clean` | Code maintenance |
| doc-updater | `/update-docs` | Updating docs |
| database-reviewer | — | DB schema changes |

### Rust Agents (2)

| Agent | Command | When to Use |
|-------|---------|-------------|
| rust-reviewer | `/rust-review` | After writing Rust code |
| rust-build-resolver | `/rust-build` | When cargo build fails |

### Python Agents (2)

| Agent | Command | When to Use |
|-------|---------|-------------|
| python-reviewer | `/python-review` | After writing Python code |
| python-build-resolver | `/python-build` | When mypy/import errors occur |

### TypeScript Agents (2)

| Agent | Command | When to Use |
|-------|---------|-------------|
| ts-reviewer | `/ts-review` | After writing TypeScript code |
| ts-build-resolver | `/ts-build` | When tsc build fails |

### Go Agents (2)

| Agent | Command | When to Use |
|-------|---------|-------------|
| go-reviewer | `/go-review` | After writing Go code |
| go-build-resolver | `/go-build` | When go build fails |

## Language Detection & Auto-Start

| File Extension | Review Agent | Build Agent | Test Command |
|---------------|-------------|-------------|-------------|
| `.rs` | rust-reviewer | rust-build-resolver | `/rust-test` |
| `.py` | python-reviewer | python-build-resolver | `/python-test` |
| `.ts` / `.tsx` | ts-reviewer | ts-build-resolver | `/ts-test` |
| `.go` | go-reviewer | go-build-resolver | `/go-test` |

## Immediate Agent Usage

No user prompt needed:
1. Complex feature requests → **planner** agent
2. Code just written/modified → **code-reviewer** + language-specific reviewer
3. Bug fix or new feature → **tdd-guide** agent
4. Architectural decision → **architect** agent
5. Build/type errors → Language-specific build-resolver

## Parallel Task Execution

ALWAYS use parallel Task execution for independent operations:

```markdown
# GOOD: Parallel execution
Launch 3 agents in parallel:
1. Agent 1: Security analysis
2. Agent 2: Language-specific code review
3. Agent 3: Type checking

# BAD: Sequential when unnecessary
First agent 1, then agent 2, then agent 3
```

## Multi-Perspective Analysis

For complex problems, use split role sub-agents:
- Factual reviewer
- Senior engineer
- Security expert
- Consistency reviewer
- Redundancy checker
