## Communication

- Be concise and direct.
- Explain non-obvious decisions briefly.
- Ask before large refactors, architectural changes, or file deletion.
- Do not add features outside the active specification.

## Workflow

1. Document the active work in `context/current-feature.md`.
2. Create a branch using the repository's established naming convention.
3. Implement only the documented goals.
4. Run the repository's documented targeted tests and required build or validation commands. Add meaningful tests for new logic using existing tools and patterns.
5. Iterate on verified failures; do not make random changes.
6. Obtain explicit permission before committing.
7. Obtain explicit permission before merging or pushing.
8. Obtain explicit permission before deleting local or remote branches.
9. Review changed behavior for correctness, security, performance, and consistency.
10. Mark the source spec complete and roll feature history forward only after the merge succeeds.

Replace generic wording in this template during setup with evidence from the target repository: base branch, branch format, commit convention, validation commands, review mechanism, and deployment constraints. If no convention exists, state that and ask before consequential operations.

## When Stuck

- After two or three evidence-based attempts fail, stop, summarize the attempts and evidence, and ask a focused question.
- Preserve unrelated changes and existing patterns.
- Keep changes minimal and avoid unrequested refactors.
- Never add AI attribution to commit messages unless the user explicitly requests it.