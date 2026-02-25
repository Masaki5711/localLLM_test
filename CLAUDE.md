# CLAUDE.md - Factory Knowledge GraphRAG System

## Project Overview

生産工場向けローカルLLMナレッジ・データ関連性分析システム。
完全閉域網（オンプレミス）環境で稼働し、RAG + ナレッジグラフを統合した GraphRAG アーキテクチャを採用。

**目的**: 属人化の解消、データ間関連性分析（ナレッジグラフ可視化）、セキュアな情報活用

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | TypeScript / React |
| Backend (API Gateway) | Rust / Axum |
| ETL Pipeline | Python / LlamaIndex, LangChain, unstructured |
| LLM Engine | Ollama or vLLM (Llama 3, Qwen etc.) |
| Vector DB | Milvus or Qdrant |
| Graph DB | Neo4j |

## Project Structure

```
.claude/
  agents/       # 20 specialized agents (planner, code-reviewer, security-reviewer, etc.)
  commands/     # 30+ slash commands (/plan, /tdd, /code-review, /build-fix, etc.)
  rules/        # Coding standards, git workflow, security, testing, hooks, patterns
  skills/       # Language patterns, TDD, security review, continuous learning
  hooks.json    # Auto-format, type-check, lint hooks
  settings.json # Project-level settings
spesification.md  # Full system specification (Japanese)
```

## Development Workflow

### 1. Plan First
Complex features -> use `/plan` or planner agent before coding.

### 2. TDD (Mandatory)
```
RED -> GREEN -> REFACTOR
```
Write tests first. Minimum 80% coverage. Use `/tdd` or language-specific test commands:
- TypeScript: `/ts-test`
- Rust: `/rust-test`
- Python: `/python-test`
- Go: `/go-test`

### 3. Code Review (Automatic)
After writing code, use `/code-review` plus language-specific reviewer:
- TypeScript: `/ts-review`
- Rust: `/rust-review`
- Python: `/python-review`
- Go: `/go-review`

### 4. Build Errors
Use language-specific build resolvers:
- TypeScript: `/ts-build`
- Rust: `/rust-build`
- Python: `/python-build`
- Go: `/go-build`

## Coding Standards (Critical)

### Immutability
NEVER mutate objects. Always return new instances with spread/copy.

### File Organization
- Many small files > few large files
- 200-400 lines typical, 800 max
- Functions < 50 lines
- No deep nesting (> 4 levels)

### Error Handling
Always handle errors with try/catch. Throw user-friendly messages.

### Input Validation
Use Zod (TypeScript) or equivalent for all user input validation.

### Forbidden in Production Code
- `console.log` (JS/TS) -> use proper logger
- `println!` (Rust) -> use `log`/`tracing` crate
- `print()` (Python) -> use `logging` module
- Hardcoded secrets -> use environment variables

## Hooks (Auto-enforced)

### PreToolUse
- Dev servers blocked outside tmux
- tmux reminder for long-running commands
- Review reminder before `git push`
- Block random `.md`/`.txt` file creation (only README.md, CLAUDE.md, AGENTS.md, CONTRIBUTING.md allowed)

### PostToolUse (on Edit)
| Language | Auto-format | Type Check | Lint Warning |
|----------|------------|------------|-------------|
| TS/JS | Prettier | `tsc --noEmit` | console.log detection |
| Rust | rustfmt | `cargo check` | println! detection |
| Python | ruff/black | mypy | print() detection |

### Stop
- console.log audit on all modified files

## Security Requirements

- **Air-gapped**: No external internet access. All components run on-premises.
- **RBAC**: Active Directory integration for role-based access control.
- **No hardcoded secrets**: Always use environment variables.
- **Input validation**: All user inputs must be validated.
- **SQL injection prevention**: Parameterized queries only.
- **Run security-reviewer agent** before commits involving auth, user input, or API endpoints.

## Architecture Notes

### GraphRAG Flow
1. Query -> Intent understanding + keyword extraction
2. Hybrid search: Vector search (semantic) + Graph traversal (structural)
3. Re-ranking of combined results
4. Prompt construction with source citations (hallucination prevention)
5. Local LLM generates answer
6. Return: answer + source links + knowledge graph visualization

### ETL Pipeline
1. Directory monitoring (new/updated/deleted files)
2. Parse: PDF, Word, Excel, CSV, PowerPoint
3. Chunking by semantic boundaries (headings, paragraphs)
4. Entity extraction: equipment, process, defect names
5. Embed -> Vector DB; Entities -> Graph DB

### Knowledge Graph Schema
- **Nodes**: Document, Equipment, Process, Defect, Part
- **Edges**: DESCRIBES, USES, OCCURRED_IN, MENTIONS

## Git Conventions

```
<type>: <description>
```
Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`

## Agent Orchestration

Always use **parallel Task execution** for independent operations. Key agents:

| Scenario | Agent |
|----------|-------|
| Complex feature | planner |
| After writing code | code-reviewer + language-specific reviewer |
| New feature / bug fix | tdd-guide |
| Architecture decision | architect |
| Build failure | Language-specific build-resolver |
| Security concern | security-reviewer |
| DB schema change | database-reviewer |
| E2E tests | e2e-runner |

## Model Selection

| Model | Use Case |
|-------|----------|
| Haiku 4.5 | Lightweight agents, frequent invocation, worker agents |
| Sonnet 4.6 | Main development, orchestration, complex coding |
| Opus 4.6 | Deep reasoning, architecture decisions, research |

## Key Commands Quick Reference

| Command | Purpose |
|---------|---------|
| `/plan` | Create implementation plan |
| `/tdd` | Test-driven development workflow |
| `/code-review` | Review code quality |
| `/build-fix` | Fix build errors |
| `/e2e` | End-to-end testing |
| `/refactor-clean` | Remove dead code |
| `/verify` | Verification |
| `/checkpoint` | Save progress checkpoint |
| `/update-docs` | Update documentation |
| `/learn` | Extract reusable patterns |
