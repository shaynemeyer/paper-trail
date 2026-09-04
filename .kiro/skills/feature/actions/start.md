# Start Action

1. Read `context/current-feature.md`; require a named feature and populated goals. If absent, stop and ask the user to load a feature by name or description. In interactive chat, `/feature load <name>` is an optional shortcut.
2. Read `context/ai-interaction.md` and `context/coding-standards.md`.
3. Inspect git status. If unrelated changes make branching risky, explain the conflict and ask how to proceed.
4. Derive a branch name from the active feature using the documented project convention, or use the remaining argument after `start`. Obtain permission before creating or checking out the branch.
5. After branch creation succeeds, set current status to `In Progress`.
6. List the goals, implement each with minimal scoped changes, and run the documented targeted validation.
7. Report completed goals, validation, and blockers. Do not commit or push.