# Hooks System

## Design Principle

- **Rule of Silence**: No output when no problems detected
- **One hook does one thing**: Don't mix detection and correction

## Hook Types

| Type | Timing | Purpose |
|------|--------|---------|
| PreToolUse | Before tool execution | Validation, blocking |
| PostToolUse | After tool execution | Auto-format, quality checks |
| Stop | Session ends | Final verification |

## Current Hooks (in ~/.claude/settings.json)

### PreToolUse
| Hook | Action | Output Condition |
|------|--------|-----------------|
| tmux reminder | Suggest tmux for long-running commands | Outside tmux only |
| git push review | Review before push | Always |
| doc blocker | Block unnecessary .md/.txt creation | Always (block) |

### PostToolUse
| Hook | Action | Output Condition |
|------|--------|-----------------|
| PR creation | Log PR URL | After `gh pr create` |
| Prettier | Auto-format JS/TS/Vue files | Silent (always runs) |
| TypeScript check | Run `tsc --noEmit` on .ts/.tsx edits | Errors only |
| ESLint check | Run ESLint on .ts/.tsx edits | Errors only |
| console.log warning | Detect console.log in JS/TS | Detection only |
| rustfmt | Auto-format .rs files | Silent (always runs) |
| cargo check | Run `cargo check` on .rs edits | Errors only |
| println! warning | Detect println! in .rs files | Detection only |
| ruff format | Auto-format .py files | Silent (always runs) |
| mypy check | Run `mypy` on .py edits | Errors only |
| print() warning | Detect print() in .py files | Detection only |

### Stop
| Hook | Action | Output Condition |
|------|--------|-----------------|
| console.log audit | Check all modified files | Detection only |
