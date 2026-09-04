# Load Action

1. Interpret text after `load`:
   - For a single token, look for that filename, with or without `.md`, in `context/features/` and `context/fixes/`.
   - For multiple words, first treat the first token as a possible spec name and the remainder as a description. If no matching spec exists, use all text as an inline description and derive a clear kebab-case name.
   - If no text follows `load`, stop and request a spec filename or feature description.
2. If an existing spec is marked complete, report that and obtain confirmation before loading it.
3. Update `context/current-feature.md`: include the feature name in the H1, set status to `Not Started`, populate goals as bullets, and preserve relevant notes and constraints from the spec or description.
4. Do not alter `History`.
5. Confirm the loaded feature and summarize its goals.