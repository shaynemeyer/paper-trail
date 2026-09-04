---
name: fastapi
description: Review and improve FastAPI + Python + SQLModel code quality in api/app/ (add "fix" to apply changes)
---

Review `api/app/` for FastAPI, Python, SQLModel, and Pydantic code quality issues.

## Checks

### Python
- Python 3.10+ union syntax not used — `str | None` instead of `Optional[str]`, `list[int]` instead of `List[int]`
- Mutable default arguments (e.g. `def f(items=[])`) — use `None` and assign inside
- Bare `except:` clauses — always catch a specific exception type
- Exceptions swallowed silently (`except Exception: pass`) — at minimum log them
- Magic strings/numbers repeated more than once — extract to a named constant
- Functions over 50 lines — flag for extraction

### FastAPI Routes
- Non-async route handler (`def` instead of `async def`)
- Route missing `response_model` — all routes should declare their response shape
- Auth dependency missing — every non-public route must use `Depends(require_user)` or `Depends(require_admin)`
- DB session not injected via `Depends(get_session)` — never instantiate sessions manually
- `from fastapi import HTTPException` imported inside a function body instead of at the top of the file
- Business logic inside route handler — extract to a service function or helper
- Route file handling more than one resource — split into separate files

### SQLModel / Database
- Missing four-schema pattern: `Model`, `ModelCreate`, `ModelUpdate`, `ModelRead` not all defined
- `ModelUpdate` fields not all `Optional` — partial updates require every field to be optional
- PATCH handler not using `model_dump(exclude_unset=True)` — will overwrite fields with `None`
- Synchronous DB call (`session.execute` without `await`)
- Missing `await session.refresh(obj)` after commit — returned object may have stale data
- Missing `await session.commit()` before returning — writes may not be persisted
- Raw SQL strings instead of SQLModel `select()` expressions

### Pydantic / Validation
- Input validated manually (if/raise) instead of using Pydantic field constraints (`min_length`, `gt`, `le`, `pattern`, etc.)
- Response data returned as a plain `dict` instead of a typed response model
- `model_dump()` called without `exclude_unset=True` on partial update payloads

### Auth
- Route accessible without any auth dependency (verify this is intentional for public routes)
- JWT payload fields accessed without `.get()` — direct key access raises `KeyError` on missing claims
- Role check implemented inline in a route instead of using `require_admin`

### Logging
- `print()` used instead of `get_logger(__name__)`
- Log event name is not `snake_case` (e.g. `"ItemCreated"` instead of `"item_created"`)
- Sensitive data logged (passwords, tokens, full request bodies with credentials)
- Mutating operations (POST/PUT/PATCH/DELETE) missing a structured log entry with `user_id`

### Code Quality
- Commented-out code blocks
- Unused imports (Ruff will catch these, but flag if present)
- `TODO` comments that are stale or blocking
- `type: ignore` comments without explanation
- Prefer `uv` over `pip` — use `uv add` to add dependencies and `uv run` to execute scripts/tools

---

## Mode

**Default (no argument / "check"):**
- Scan `api/app/` and report all findings
- Group findings by category
- Do not modify any files

**If asked to "fix":**
- First report all findings grouped by category with numbered items
- Ask: "Which items would you like me to fix? (enter numbers like 1,3,5 or 'all' or 'none')"
- Wait for confirmation before changing anything
- Apply only the approved fixes
- Run `./doit.sh lint-fix` after applying changes to ensure formatting is clean
- Report what changed
