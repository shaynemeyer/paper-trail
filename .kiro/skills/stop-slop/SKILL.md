---
name: stop-slop
description: "Produce concrete, production-oriented code and prose without generic AI filler. Use when asked for clearer names, useful comments, realistic examples, less boilerplate, direct prose, or complete implementation instead of demonstration code."
---

# Stop Slop

Apply the durable rules in `../../steering/stop-slop.md` to the current request. In particular, use domain-specific names, comment only non-obvious intent, prefer concrete implementation over demonstration code, and never leave TODO placeholders.

If domain terminology is necessary but cannot be inferred safely, ask a focused question rather than inventing generic concepts. Keep the response direct and identify any information that prevents a complete implementation.