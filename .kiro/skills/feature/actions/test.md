# Test Action

1. Read `context/current-feature.md`, `context/testing-instructions.md`, `context/ai-interaction.md`, and applicable testing sections of `context/coding-standards.md`.
2. Inspect the feature diff for behavior with meaningful logic: business rules, request handling, authorization, validation, data access, boundaries, and pure utilities.
3. Identify existing coverage and follow the repository's test layout, naming, fixtures, and tools.
4. Add focused tests for uncovered behavior. Cover important success, validation, authorization, not-found, and failure paths as applicable. Avoid tests that merely restate framework behavior or inflate coverage.
5. Run the documented targeted tests, then required broader tests and build checks when feasible.
6. Fix failures caused by the feature or new tests. Do not conceal unrelated existing failures.
7. Report tests added, commands and results, remaining gaps, and any validation that could not run.