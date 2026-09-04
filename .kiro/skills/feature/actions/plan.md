# Plan Action

Splits a plan document into multiple feature specs under `context/features/` (or
`context/fixes/` for bug fixes) without activating any of them.

1. Interpret text after `plan`:
   - A path to an existing file: read it.
   - Otherwise: treat the text itself as the plan content.
   - If no text follows `plan`, stop and request a plan file path or plan text.
2. Identify discrete, independently implementable units of work in the plan. Split
   along natural seams — typically one unit per changed file/module, or per layer
   (e.g. backend route, frontend client, UI) when one conceptual change spans several.
   As a rule of thumb, size each unit so implementing it — reading the relevant files,
   writing the code, and verifying it — stays under roughly 100K tokens of context;
   split further if a unit looks like it'll run larger than that.
3. Order the units by dependency; a unit that consumes another's output comes after it.
4. Check `context/features/*.md` and `context/fixes/*.md` for the highest existing
   numeric prefix and for specs that already cover part of this plan — skip or note
   any overlap instead of duplicating it.
5. For each unit, create `context/features/<nn-name>.md` (or under `context/fixes/`)
   with an H1, `**Status:** Not Started`, `**Depends on:**` (`none` or sibling
   filenames without extension), and `Context`, `Goals`, `Notes`, and `Testing`
   sections. Reference the source plan (path, or "provided inline") and the section
   it covers under `Context`. Populate only facts supported by the plan; carry over
   exact code/signatures rather than paraphrasing them away.
6. Do not update `context/current-feature.md` and do not create a branch.
7. Report the specs created, in dependency order, with a one-line description each,
   plus any plan sections skipped as already covered. Tell the user to ask Kiro to
   load whichever one they want to start with.
