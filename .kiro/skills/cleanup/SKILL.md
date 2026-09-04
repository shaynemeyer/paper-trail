---
name: cleanup
description: "Audit project housekeeping and optionally apply only user-approved fixes. Use when asked to check or clean logs, imports, TODOs, stale files, context drift, environment parity, TypeScript suppressions, or feature history."
---

# Cleanup

Infer the mode from the user's request: `check` by default; `run` and `fix` request an interactive cleanup. For an interactive `/cleanup` invocation, `$ARGUMENTS` may supply the mode.

Audit the codebase for:

1. `context/current-feature.md` history order (oldest to newest), if present.
2. Unnecessary debug logging in the project's source directories.
3. Unused imports.
4. Stale TODO comments.
5. Orphaned or unused files, using build configuration and references as evidence.
6. Context files that no longer match the project.
7. Variable-name parity between `.env` and `.env.production`, if both exist. Compare names, never secret values.
8. Potentially stale `@ts-ignore` comments.

## Modes

- `check` or no argument: report findings and what would change; do not modify files.
- `run` or `fix`: first report numbered findings, then ask which numbers to fix (`all` and `none` are valid). Wait for the answer and change only approved items.
- Any other argument: explain the valid modes and do not modify files.

After approved fixes, run relevant targeted validation and report the exact changes. Do not expose environment values.