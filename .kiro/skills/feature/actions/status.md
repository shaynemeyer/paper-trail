# Status Action

This action is read-only: do not modify files or git state and do not request permission.

1. Read the H1, `Status`, and latest `History` entry in `context/current-feature.md`.
2. Count complete and outstanding Markdown specs under `context/features/` and `context/fixes/`. The next item is the lowest-numbered outstanding spec whose declared dependencies are complete; do not assume every project numbers specs.
3. Inspect the current branch, uncommitted changes, and commits not present on the configured upstream.
4. Read gate commands from `context/ai-interaction.md`. Run only fast, non-mutating checks; report slow, unavailable, or service-dependent gates as not checked with a reason.
5. Report blockers or pending decisions.

Use a compact format:

```text
Current:   <feature and status, or nothing loaded>
Progress:  <complete/total and next item>
Git:       <branch, working tree, upstream state>
Gates:     <results or not checked with reason>
Previous:  <latest history entry or none>
Next:      <recommended action>
```