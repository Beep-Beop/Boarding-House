---
name: boarding-build
description: Build agent for Boarding House — uses Superpowers workflow, respects plan.md as session continuation anchor
---

# Boarding House Build Agent

**Stack**: FastAPI + SQLAlchemy + MySQL + CustomTkinter desktop GUI
**Test command**: `pytest test/ -v`
**API server**: `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`
**GUI**: `python main.py`
**Seed DB**: `python seed_data.py`

## Plan.md as Continuation Anchor

`plan.md` is the source of truth for what needs doing. When resuming after a context-max reset:
1. Read `plan.md` fully to re-establish context
2. Check git log for what was already committed
3. Cross-reference with plan.md to determine next uncompleted step
4. Proceed from there — do not restart from scratch

## Workflow Sequence

For every task from plan.md:
1. Brainstorming skill auto-triggers — clarify scope
2. Writing-plans skill — break into atomic 2-5 min tasks with file paths
3. Executing-plans or subagent-driven-development skill
4. TDD enforced: write failing test first, then implement (backend API changes only; GUI changes can skip test-first)
5. Run `pytest test/ -v` after each backend task
6. Code-review skill before declaring done
7. Use git worktrees for isolated branch development
8. Commit with `git add` + `git commit` after each verified task

## Tool Mapping (OpenCode vs Claude Code)

- `TodoWrite` → OpenCode's `todowrite`
- `Task` with subagents → OpenCode's `@mention` syntax or `use skill tool to load subagent-driven-development`
- `Skill` tool → OpenCode's native `use skill tool to load <skill-name>`
- File ops → OpenCode's built-in file tools (Read/Write/Edit)

## Auto-Triggers Enabled

- SessionStart context injection: ON
- Brainstorm on new tasks: ON
- Verification gates: ON
