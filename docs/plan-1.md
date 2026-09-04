Use React, TypeScript, Vite, and Tailwind CSS. Work autonomously: create the
project, install dependencies, implement it, verify it, and start the dev
server. Do not use Kiro's native spec workflow.

Core experience:
- Display a prominent natural-language search field
- Search a local dataset of at least 40 realistic sample arXiv papers
- Each paper must include id, title, authors, abstract, category, year,
  arXivUrl, and a precomputed numeric embedding
- Generate a query embedding locally using a deterministic feature-hashing
  function
- Rank papers using cosine similarity
- Show the top 10 results with similarity percentages
- Add category and year filters
- Let users expand and collapse abstracts
- Add a “Why this matches” explanation based on overlapping semantic features
- Include a link to open each original arXiv page
- Provide an example-query button
- Include loading, no-results, and cleared-search states

Important:
The search must be functional, not a visual mockup. Put vectorization and
cosine-similarity logic in separate testable TypeScript modules. Add unit tests
for ranking and filtering.

Visual direction:
Create a sophisticated scientific-editorial interface, not a generic
dashboard. Use a deep charcoal background, electric violet accents, strong
typography, restrained motion, and excellent spacing. Make relevance scores
easy to scan. The app must work on desktop and mobile.

Constraints:
- No backend
- No authentication
- No database
- No calls to arXiv or external AI services at runtime
- Do not fabricate links to nonexistent papers; if the included records are
  synthetic, clearly label them as demo records and omit external links
- Keep the implementation intentionally small

Before coding, briefly show the implementation plan and acceptance criteria.
Then implement without stopping for routine questions. Run tests and verify
that the production build succeeds.