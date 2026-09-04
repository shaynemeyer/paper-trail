# Explain Action

1. Read `context/current-feature.md` and `context/ai-interaction.md`.
2. Determine the documented base branch and inspect the feature diff. Include untracked files that belong to the feature.
3. For each created, modified, renamed, or deleted file, give its status and a one- or two-sentence explanation of what changed and why. Highlight important functions, components, migrations, or patterns.
4. End with a concise account of the data flow, control flow, and dependencies connecting the changes.

Use this structure:

```markdown
### Files Changed

**path/to/file** (new|modified|renamed|deleted)
Explanation.

### How It All Connects

Summary of the implementation flow.
```

Do not modify files or git state.