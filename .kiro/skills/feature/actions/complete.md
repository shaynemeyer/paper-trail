# Complete Action

Completion changes git history and branches. Explain the proposed sequence, require required validation to pass, and obtain explicit permission before each commit, merge, push, or branch deletion. Permission for one operation does not imply permission for the next.

1. Run the project's required tests and build checks from `context/ai-interaction.md`. Stop on failures.
2. With permission, stage only feature-related changes and create a focused commit using the documented convention.
3. With permission, switch to the documented base branch and merge the feature branch locally. Do not push yet.
4. After a successful merge, update the source spec status to `Complete — merged YYYY-MM-DD (<merge-or-resulting-commit-sha>)`.
5. Roll history forward before writing the new entry: append any existing `History` entry to the end of `context/feature-history.md`, then reset `context/current-feature.md` to its neutral H1, `Not Started`, empty Goals and Notes placeholders, and this feature as the only History entry.
6. With permission, commit the spec and context update using an appropriate project convention. Do not hardcode a message if project rules differ.
7. With permission, push the base branch once.
8. Ask separately before deleting the local feature branch. If it exists remotely, ask separately before deleting the remote branch.
9. Report commit identifiers, merge strategy, push result, branch state, and reset context.

If the project uses pull requests or merge requests instead of local merges, follow its documented workflow and preserve the same validation, permission, spec-status, and history guarantees.