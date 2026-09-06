# 0004 — The agent only drafts, only uses tools, and every identifier it cites is checked

_[← Decisions](./README.md)_

**Status:** Accepted, 2026-09-05. **Touches:** `ACMP5`.

## Context

The business case wants agents that "autonomously draft impact assessments"
over a "self-improving knowledge graph". The review found that an agent
answering from its own knowledge about an enterprise model is worthless, and
that an agent writing approved content removes the human gate the method
depends on (principle `P3`).

## Decision

The agent's autonomy is **draft only**: it answers questions and proposes,
it never writes to the store. It reasons only over tool results (search, get,
neighbours, trace, impact, read-only SQL) and its system prompt carries the
metamodel summary and the grounding rule. After every answer the identifiers
it cites are compared with the identifiers the tools returned, and any that
were not returned are flagged in the UI. A stub provider runs the same tools
without a model so the demo works without a key.

## Alternatives

- **Free-text answers from the model's knowledge** — plausible and wrong.
- **An agent with write access behind a confirmation dialog** — a proposal
  model (plateau `PLAT4`) is the right place for that, with base versions and
  a recorded approval, not a dialog.

## Consequences

- The agent is only as good as the tools; a question the tools cannot answer
  gets "not found in the model", which is the correct answer.
- Read-only SQL is guarded (statement shape, forbidden keywords, row cap) and
  runs on the same connection as the app, so it needs no separate credential
  in the PoC; on Databricks it will run as the user (on-behalf-of) so grants
  apply.
- On Databricks the preferred approach is a Genie-based agent, or whichever
  agent framework the platform offers, that traverses the graph and answers in
  Markdown, with questions, answers and user feedback kept for monitoring and
  improvement (question 10 in [the open questions](../scope/8_two-gates-and-readable-views.md)).
