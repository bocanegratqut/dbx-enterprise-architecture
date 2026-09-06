# Initiative 4 — Model branches, and current versus target state

_[← Scope index](./README.md) · [EA home](../README.md)_

**Requester:** the product owner. **Agent:** the coding agent in this
repository. **Reviewer:** the product owner. **Baseline:** initiatives 1 to 3.
**Target plateau:** the change-set core of `PLAT4` Governed change, on DuckDB
first, with the same DDL for Delta.

## Why

Two asks from the owner:

1. **Version the enterprise model like code.** Several architects work from
   `main`, add elements and update existing ones on their own branch, and
   merge into `main` later. Today every edit lands immediately, protected only
   by optimistic concurrency and a change log (`GAP5`).
2. **Manage the target state.** The organisation must see, per architectural
   artefact and per work package (initiative), the current state of each
   element (live, retired, in implementation, proposed, non-existent) against
   its target state (new, change, decommission, merge, undecided). Today an
   element has a workflow status (draft, approved, retired) and the source
   tool's free-text lifecycle, and no notion of target.

The review of the business case established that clones and optimistic
concurrency are not git semantics (`ASM3`): proposals need an explicit change
set with base versions and a recorded human decision. This initiative builds
that change-set core.

## What changes

| Layer | Change |
| ----- | ------ |
| 1 Strategy | No new element; `ASM3` and principle `P3` are what this initiative implements |
| 3 Information | New objects `DOBJ2.5` Branch and `DOBJ2.6` Change set; `DOBJ2.1` Element and `DOBJ2.2` Relationship gain a current state, a target state and a target work package |
| 4 Application | New services `ASVC7` Branches and merge, `ASVC8` Target state; `ACMP2` Graph store gains the branch overlay, `ACMP3` the diff and merge, `ACMP6` the branch switch, the Branches page and the Target state page, `ACMP7` a `--branch` option |
| Transition | `GAP5` closed for its change-set core; new `GAP12` No target state model |

## Design

**Branches are overlays on the same schema.** `main` is the element,
relationship and link tables as they are. A branch is a row in a `branch`
table (name, description, work package, status open, merged or abandoned,
who and when) plus three overlay tables with the same columns as the main
ones and three more: the branch, the `base_version` of the main row the change
started from, and an operation (`upsert` or `delete`). Reading on a branch
means reading `main` with the branch's rows laid over it: an element changed
on the branch replaces its main row, one deleted on the branch disappears, a
new one appears. Writing on a branch writes only the overlay. Nothing on
`main` changes until a merge. The same overlay is a `MERGE` statement on
Delta, so the design carries to Databricks unchanged.

**The current branch is a request setting.** The header shows the branch the
reader is on; a selector switches it (kept in the session, never in the URL);
every page, the agent and the importer read and write through it. The command
line takes `--branch`. `main` is the default and is what a visitor sees.

**Diff and merge with base versions.** The Branches page lists a branch's
changes against `main` today: elements added, changed and deleted,
relationships added and removed, each with the main row before and the branch
row after. A change whose base version is older than `main`'s current version
is a **conflict**: somebody changed the same row on `main` since the branch
started. The merge is **per item**: the change set is a merge log in which
every element and relationship is ticked to go to `main` now or left to remain
on the branch, and every conflict asks the merger to choose the branch's row or
`main`'s. A merge writes the change log with the branch as the origin and
records who merged and when; what was merged leaves the branch, what was left
stays, and the branch closes only when nothing remains. Abandon closes it
without writing. Nothing is rebased.

**States are core fields, vocabularies are fixed and small.** Every element
and relationship carries:

| Field | Values | Meaning |
| ----- | ------ | ------- |
| `current_state` | `proposed`, `planned`, `in_implementation`, `live`, `retired`, `non_existent` | What is true of the artefact today. Derived from the source tool's lifecycle text on import and editable afterwards |
| `target_state` | `undecided`, `keep`, `new`, `change`, `decommission`, `merge` | What the organisation intends for it |
| `target_work_package` | an element id | The work package (initiative) that carries the change; the pack says which type plays that role through its notation (`archimate: WorkPackage`) |
| `target_note` | text | Why, and into what (for `merge`) |

The existing workflow `status` (draft, approved, retired) stays what it is:
whether the record itself is trusted. The two are different questions: a
`live` element can have an `approved` record, a `proposed` one a `draft` record.

**Target state page.** Pick a work package, or all: counts per target state,
a table of every element and relationship with current state against target
state and the note, and a generated view of the work package in which new
artefacts are drawn dashed and green, changed ones amber, decommissioned ones
red and struck through, kept ones plain. The same markers reach the draw.io
export. The Element page gets a State card with the three fields editable, and
the CSV contract gains the columns.

**How the two fit together.** A branch is where a change is drafted; the
target state is what the drafted change says. An architect on a branch adds a
`proposed` element with target `new` under a work package; after the merge,
`main` shows it as proposed and the Target state page counts it under that
work package. When it goes live, its current state changes and its target
becomes `keep`.

## Work packages

| # | Work package | Delivers | Effort |
| - | ------------ | -------- | ------ |
| 1 | Branch overlay in the store | `branch`, `branch_element`, `branch_relationship`, `branch_link` tables; a request-scoped current branch; every read and write of the DuckDB backend honours it; `--branch` on the CLI; tests | about 1.5 days |
| 2 | Diff, merge, abandon | The diff with base versions and conflicts; merge with per-conflict resolution, change log and branch closure; abandon; tests | about 1 day |
| 3 | Branches in the app | Header branch selector and banner, New branch modal, the Branches page (list, diff, conflicts, merge, abandon); the importer loads into the current branch | about 1 day |
| 4 | States | The four fields on elements and relationships, migrations, the CSV contract, import derivation from lifecycle text, the Edit tab and the State card, sample data with a worked work package | about 1 day |
| 5 | Target state page and marked views | The page with work package filter, counts, table and the generated view with state markers in Mermaid and draw.io | about 1 day |

## In scope

Everything above on DuckDB, with the DDL kept portable. Every user may
create, merge and abandon branches (roles are documented, not enforced).

## Out of scope

Rebasing a branch on a moved `main`; branches of branches; per-row review
comments; approval by a second person before merge (that is the approval flow
of `PLAT4`, once roles are enforced); a history of target states over time;
time-based plateaus (a work package is the unit of analysis, as the owner
asked).

## Delivered

Built on 2026-09-06 on `main`: the branch overlay tables and the request-scoped current branch; diff, merge item by item and abandon; the header branch selector, the New branch modal and the Branches page with the merge log; `--branch` and `ea branch …` on the command line; the four state fields with migrations, the CSV columns and the lifecycle derivation; the State card and Edit fields on the Element page; the Target state page with counts, the current-by-target matrix, tables and the marked view (Mermaid and draw.io); `ea target`; the sample data with a worked work package; tests in `tests/test_branches.py`. Found and fixed while building: an element edited on a branch lost its links in the diff and merge (links now follow the element onto the branch); a re-import of unchanged rows produced empty change-set rows (unchanged rows are skipped).

## Approvals

| Gate | Decision | By | When | What was shown |
| ---- | -------- | -- | ---- | -------------- |
| Direction | Approved | The product owner | 2026-09-05, in the conversation | The request: branches from `main` merged later; current versus target state per artefact, analysed by work package |
| Understanding | Approved with one addition | The product owner | 2026-09-05, in the conversation ("ok, yes, understood. build both") | This document and the worked example of the overlay (two architects, a conflict, the merge); the two state vocabularies; the addition: the merge is per item, a merge log where the architect confirms what goes to `main` and what remains on the branch |
| Design | N/A — Depth 1; the design section above is the design | — | — | — |

## Open questions

Questions 12 and 13 in [open-questions.md](./open-questions.md).
