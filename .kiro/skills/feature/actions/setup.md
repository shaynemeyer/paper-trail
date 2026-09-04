# Setup Action

Initialize the target project without overwriting existing context silently.

1. Create `context/features/`, `context/fixes/`, and `context/research/` if absent.
2. Copy `../templates/ai-interaction.md` to `context/ai-interaction.md`.
3. Use `../templates/project-overview.md` as the structure for `context/project-overview.md`, but inspect the repository and replace prompts with evidenced project facts. State when evidence is absent.
4. Copy `../templates/README.md` to `context/README.md`.
5. Copy `../templates/current-feature.md` to `context/current-feature.md`.
6. Create `context/testing-instructions.md` from the actual test configuration and conventions: when tests are warranted, what to test, and exact validated commands. Do not assume a framework.
7. Create `context/coding-standards.md` from repository evidence: language and naming conventions, framework patterns, organization, error handling, validation, configured linting/formatting, and subproject differences. Do not invent conventions for a thin codebase.
8. Create or update `.kiro/steering/project-context.md` with:

```markdown
---
inclusion: always
---

# Project Context

#[[file:context/project-overview.md]]
#[[file:context/coding-standards.md]]
#[[file:context/ai-interaction.md]]
#[[file:context/testing-instructions.md]]
#[[file:context/current-feature.md]]
```

9. Preserve user content in existing files. Show proposed merges or ask before replacing conflicting content.
10. Confirm the exact directories and files created, updated, skipped, or preserved.