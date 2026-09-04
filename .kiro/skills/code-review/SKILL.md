---
name: code-review
description: "Review code, pull requests, commits, or diffs for concrete defects. Use when asked for a code review, PR review, change-risk assessment, or prioritized findings, with correctness and security ahead of style."
---

# Code Review

Review the requested change set. If scope is unspecified, inspect the local diff and state the scope used.

Prioritize findings in this order:

1. Bugs and correctness.
2. Security.
3. Performance only when impact is measurable or clearly material.
4. API design and naming.
5. Style only when existing automated checks do not cover it.

For each finding:

- Identify the file and line or smallest useful location.
- State the problem in one sentence.
- Explain what breaks and under which conditions.
- Give a specific fix, including a concise code example when useful.

Focus on problems, not praise. If there are no actionable findings, say `No issues found.` and stop. Do not manufacture feedback, repeat linter output as review commentary, or recommend a public API change without labeling it as breaking.

Return at most the five highest-priority findings. If verified lower-priority findings remain, report only their count.