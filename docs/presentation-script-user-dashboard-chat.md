# Presentation Script: User Dashboard + Document Chat (via `/feature`)

**Audience:** stakeholders/leadership
**Length:** ~25–30 minutes
**Goal:** demonstrate the `/feature` skill workflow end-to-end by planning and
implementing a real feature — replacing the placeholder dashboard with a
document list, and wiring up chat against a selected document.

Companion plan doc: `docs/plan-user-dashboard-chat.md`.

---

## 0:00–3:00 — Set up the problem

> AI coding assistants are fast, but fast without structure means scope
> creep, inconsistent patterns, and nobody remembering *why* a change
> happened. What we've built here is a lightweight workflow — a Claude Code
> skill called `/feature` — that keeps every change spec'd, tracked, and
> reviewable, without slowing us down. I'll show it live: planning a new
> feature, breaking it into scoped units, implementing one, and verifying
> it — in about 20 minutes.

## 3:00–6:00 — Show the problem it solves in this app

- Open the app, show `/` — the placeholder "Your dashboard is coming soon"
  screen.
- "This is a real gap. Users log in and get nothing. Separately, we already
  built the *backend* capability to chat with a document's contents — it's
  just never been connected to any screen. I wrote up a short plan doc for
  both pieces." (Open `docs/plan-user-dashboard-chat.md` briefly — point at
  the two sections, don't read it verbatim.)
- Anticipate the obvious question — "why not just drop the PDF into a chat
  window?" — before someone asks it:
  > When you upload a document here, we parse it and generate its embeddings
  > up front, once, at upload time — not on the fly inside a chat request.
  > That matters for a few reasons: chat responses stay fast, because the
  > expensive parsing/chunking work is already done and only the question
  > itself needs to be embedded; every user's question retrieves from the
  > same pre-computed chunks, so answers are grounded consistently instead
  > of depending on how a document happened to get re-parsed that session;
  > and that one-time cost is amortized across every future question,
  > instead of being paid again on every single chat message.
  >
  > To put a number on it: parsing the PDF itself is free — that's local
  > text extraction, not an LLM call. The real cost is embedding, and a
  > typical arXiv paper (8–12 pages) extracts to roughly 8,000–15,000
  > tokens, split into ~15–30 chunks that each get embedded once, locally,
  > at upload time. That's the entire cost for unlimited future questions
  > against that paper.

## 6:00–10:00 — Live: `/feature plan`

- Run: `/feature plan docs/plan-user-dashboard-chat.md`
- Narrate while it runs: "This doesn't write any code. It reads the plan and
  splits it into independently-shippable units, in dependency order — here,
  the dashboard has to exist before the chat panel can attach to it."
- Show the two generated files under `context/features/` (03-…, 04-…). "Each
  one has goals, context, and a testing plan. This is our paper trail —
  literally — for why a change happened, not just what changed."

## 10:00–13:00 — Live: `/feature load` + `/feature start`

- Run: `/feature load 03-user-dashboard` (or whatever it names it).
- "Loading activates one spec at a time — only one feature is ever in
  flight, so there's no ambiguity about what's being worked on right now."
- Run: `/feature start`. Point out: it flips status to "In Progress" and
  creates a branch automatically, named from the spec — no manual git
  bookkeeping.

## 13:00–22:00 — Live: implement

- Let it implement the dashboard swap and the chat panel per the spec.
  Narrate at a high level while it works — don't read code line by line:
  - "It's following conventions we already documented for this repo — same
    mutation pattern, same component folder rules — so the output looks
    like something a teammate wrote, not a one-off AI style."
  - "Because it's building against a spec file, if it drifts, we can just
    point back at the goals section instead of trying to remember what we
    asked for five minutes ago."
- Once done: switch to the browser, show the new dashboard, select a
  document, ask it a real question, show the grounded answer come back.

## 22:00–25:00 — Verify + wrap the loop

- Mention (don't necessarily run live, for time): `/feature test`,
  `/feature review` — a lint/build pass and a goals-met check before
  anything merges.
- "Nothing gets committed automatically — the workflow stops for a human
  decision at merge. The AI moves fast inside guardrails we set, not around
  them."

## 25:00–28:00 — Business framing / close

> The payoff isn't that AI writes the code — it's that every change now
> comes with a durable record of intent, is scoped small enough to review in
> minutes, and follows the same conventions whether a person or the
> assistant wrote it. That's what makes this safe to scale beyond one
> feature.

## 28:00–30:00 — Q&A buffer
