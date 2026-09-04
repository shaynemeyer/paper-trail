# Plan Action

Breaks a larger plan document into multiple feature specs under `context/features/`
(or `context/fixes/` for bug fixes), without activating any of them. Use this when the
user has a design/plan doc covering more ground than one feature — e.g.
`docs/plan-pdf-upload.md` became specs `01-document-upload-api-client` and
`02-document-upload-ui`.

1. Interpret what the user supplied after "plan":
   - A path to an existing file: read it.
   - Inline text: treat it as the plan content directly.
   - Nothing supplied: stop and report that `plan` requires a file path or plan text.

2. Read the plan and identify discrete, independently implementable units of work.
   Split along natural seams — typically one unit per changed file/module, or per
   layer (backend route, frontend client, UI) when a single conceptual change spans
   several. Each unit should be small enough to implement, test, and commit on its
   own, per the workflow in `context/ai-interaction.md`. As a rule of thumb, size each
   unit so implementing it — reading the relevant files, writing the code, and
   verifying it — stays under roughly 100K tokens of context; split further if a
   unit looks like it'll run larger than that.

3. Order the units by dependency (a unit that consumes another's output comes after
   it) — this becomes the numbering.

4. Check `context/features/*.md` (and `context/fixes/*.md`) for the highest existing
   `nn` prefix and for specs that already cover part of this plan — don't duplicate
   an existing spec; skip or note it instead.

5. For each unit, write `context/features/{nn-name}.md` (or `context/fixes/` if it's
   a fix) following the format used by existing specs:

   ```markdown
   # Title

   **Status:** Not Started

   **Depends on:** none | {sibling filename(s) without extension}

   ## Context

   Why this change is needed and what it builds on. Reference the source plan
   (file path, or "provided inline") and which section/step of it this spec covers.

   ## Goals

   Concrete, actionable bullets. Include exact code/signatures the plan specifies;
   don't paraphrase away specifics the plan already nailed down.

   ## Notes

   Constraints, decisions, or things intentionally deferred to a later spec.

   ## Testing

   Per `context/testing-instructions.md` — what to verify and how, for this unit
   specifically.
   ```

6. Do not update `context/current-feature.md` and do not create a branch — `plan`
   only creates spec files, same as running `/feature <name>` for a single spec.
   The user activates one with `load` when ready.

7. Report the specs created, in dependency order, each with a one-line description,
   plus any plan sections that were skipped because they're already covered by an
   existing spec.
