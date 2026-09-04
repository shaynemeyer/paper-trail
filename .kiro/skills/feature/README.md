# Feature Skill

A spec-driven Kiro CLI workflow. Ask Kiro to set up the feature workflow once, then ask it to load, start, review, test, explain, complete, or report the status of tracked work. In interactive chat, `/feature <action>` is an optional shortcut. Asking Kiro to create a feature spec by name and description creates but does not activate it.

## Bundled files

The eight executable action guides are in `actions/`: `setup.md`, `status.md`, `load.md`, `start.md`, `review.md`, `test.md`, `explain.md`, and `complete.md`. `help` and default spec creation are defined directly in `SKILL.md`; no other action files are expected.

Setup uses the four files in `templates/`: `README.md`, `ai-interaction.md`, `current-feature.md`, and `project-overview.md`. It also derives project-specific coding and testing guidance and creates `.kiro/steering/project-context.md` with Kiro workspace-file references.

See `SKILL.md` for state semantics, dispatch rules, and git safety constraints.