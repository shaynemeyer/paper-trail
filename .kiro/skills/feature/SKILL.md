---
name: feature
description: "Manage a spec-driven feature or fix from setup through status, loading, implementation, review, testing, explanation, and completion. Use when asked to manage tracked feature work or whenever context/current-feature.md tracks the active work."
---

# Feature Workflow

Infer the requested action from the user's request. For an interactive `/feature` invocation, treat the first word of `$ARGUMENTS` as the action. Before every action except `setup` and `help`, read `context/current-feature.md`.

## Actions

| Action | Supporting instructions | Behavior |
| --- | --- | --- |
| `setup` | `actions/setup.md` | Initialize project context and Kiro steering. |
| `status` | `actions/status.md` | Report feature, spec, git, and gate state without changes. |
| `load` | `actions/load.md` | Load a spec or inline description. |
| `start` | `actions/start.md` | Create a branch and implement the active work. |
| `review` | `actions/review.md` | Audit implementation against goals. |
| `test` | `actions/test.md` | Add or verify meaningful tests. |
| `explain` | `actions/explain.md` | Explain changed files and their relationships. |
| `complete` | `actions/complete.md` | Validate, then perform separately approved git and state transitions. |
| `help` | This table | Show available actions and examples. |

For one of the eight actions with a supporting file, read that relative file before proceeding. There are no separate action files for `help` or spec creation.

If the requested action is not one of the actions above, treat the requested skill input as `<name> [description]` for spec creation:

1. Require a filesystem-safe kebab-case name; derive it from the description only when unambiguous.
2. Create `context/features/<name>.md` with an H1, `**Status:** Not Started`, goals, notes, and dependencies. Populate only facts supported by the request; otherwise leave explicit section prompts.
3. Do not activate the spec. Tell the user to ask Kiro to load feature `<name>`. In interactive chat, `/feature load <name>` is an optional shortcut.

If no action or feature description can be inferred, show the action table and ask what they want to do.

## State Model

`context/current-feature.md` contains an H1, `Status` (`Not Started` or `In Progress`; `Complete` is transient), `Goals`, `Notes`, and exactly one latest entry under `History`. During completion, move an existing history entry to the end of `context/feature-history.md` before writing the latest entry.

Specs live in `context/features/` and fixes in `context/fixes/`. Each spec has a status directly below its H1: `Not Started` or `Complete — merged YYYY-MM-DD (<sha>)`. Completed specs stay in place so dependency references remain valid.

## Constraints

- For command-running or git actions, read `context/ai-interaction.md`; read `context/coding-standards.md` before code changes. These project files override generic workflow examples.
- Never commit, merge, push, or delete a branch without explicit permission for that operation. Never do so before required validation passes.
- Do not assume a package manager, framework, test runner, base branch, hosting service, or pull-request terminology; discover them from repository evidence.
- Keep all bundled references relative to this `SKILL.md`.