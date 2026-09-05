# 0006 — Branches as overlays on the same schema, merged once with base versions

_[← Decisions](./README.md)_

**Status:** Proposed, 2026-09-05 (accepted at the Understanding gate of initiative 4). **Touches:** `ACMP2`, `ACMP3`, `DOBJ2.5`, `DOBJ2.6`.

## Context

Architects want to work from `main`, draft on their own branch and merge
later. The business case proposed zero-copy clones and optimistic concurrency;
the review showed that clones cannot be merged back and that optimistic
concurrency only detects same-row races (`ASM3`). A real version control
system for the model would be a second product.

## Decision

A branch is a set of overlay rows in tables that mirror the main ones (element,
relationship, link), each row carrying the branch, the base version of the main
row it started from, and an operation. Reads on a branch lay the overlay over
`main`; writes on a branch touch only the overlay. Merge applies the overlay to
`main` in one pass, detects conflicts by comparing base versions with `main`'s
current versions, asks the merger to choose per conflict, writes the change
log and closes the branch. A branch is merged once or abandoned; there is no
rebase and no branch of a branch.

## Alternatives

- **Git on exported files** — the model as Markdown or CSV in git, merged with
  git. Real git semantics, but line-based merging of a graph produces conflicts
  humans cannot read, and the app would sit on files rather than on a store.
- **Delta clones per branch** — declined in the review: no merge-back.
- **Event sourcing** — every edit an event, branches as event streams. Cleaner
  history, far more code; the overlay gives the same user-visible behaviour.

## Consequences

- The overlay is a `MERGE` statement on Delta, so the design carries to
  Databricks unchanged.
- Every read path in the store must honour the current branch; the cached
  graph is keyed by branch.
- Long-lived branches accumulate conflicts; the page makes that visible rather
  than hiding it.
