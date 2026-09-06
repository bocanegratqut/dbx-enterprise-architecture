# 0009 — Review before merge, approved per element type by assigned reviewers

_[← Decisions](./README.md)_

**Status:** Accepted 2026-09-06 (initiative 7). **Touches:** `ACMP12`, `DOBJ2.7`, `BPROC2.4`, `ASVC7`.

## Context

Initiative 4 built branches with a per-item merge log, and question 13 left
"who may merge" to the roles. The owner asked for a second person approving a
branch, with reviewers per type, once roles are enforced. The people who care
about a change are the owners of the types it touches (the pack's instance
owners), not one central approver.

## Decision

- **Statuses.** A branch is `open`, then `in_review` once its author requests
  a review, then `approved` when the review is complete, then `merged`; a
  "send back" returns it to `open`; `abandoned` is possible at any time before
  the merge.
- **Frozen while in review.** A branch in review refuses writes, so what the
  reviewers read is what will merge.
- **Reviewers per element type.** A store table assigns users or groups to
  element types; an admin edits it on the Metamodel page. The change set's
  element types decide who must approve. A type with no assignment is
  approved by any Reviewer.
- **Approval is complete** when every touched type has an approval from one
  of its reviewers, none of them the branch's author. One "send back" with a
  comment ends the round.
- **The merge asks the review.** An architect merges only an approved branch;
  an admin may merge an unapproved one, and the change log says so.
- **Every decision is a row** in `branch_review` and an entry in the change
  log with the branch as origin, so the approval is a fact of the model, not
  a memory (principle `P3`).

## Consequences

- The merge log stays the unit of review: reviewers read the same rows the
  merger ticks. Per-row comments are a later refinement.
- A relationship's review follows its ends: a relationship between two types
  needs both types' reviewers only when both are in the change set.
- The Propose page is unchanged: an applied proposal is rows on a branch that
  goes through the same review.

## Alternatives not taken

- **One approver for everything:** the enterprise architecture team would
  become the bottleneck for every data-entity rename.
- **Approval per row:** the truthful unit is the change, which a reviewer
  reads as a whole; per-row approval would let a change land half-approved.
- **Approval by the second person only, no types:** then nobody guarantees
  that the information architect saw the information elements.
