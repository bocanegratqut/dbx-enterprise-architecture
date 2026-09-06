# Initiative 6 — Search, bulk edit, and the model's health

_[← Scope index](./README.md) · [EA home](../README.md)_

**Requester:** the product owner. **Agent:** the coding agent in this
repository. **Reviewer:** the product owner. **Baseline:** initiatives 1 to 5.
**Target plateau:** `PLAT1` extended; the freshness figures anticipate `PLAT3`.

## Why

The owner named three things "smaller but felt daily": full-text search over
descriptions, bulk edit, and freshness and completeness dashboards. Today the
search reads names, identifiers and descriptions with one substring; twenty
elements that need the same state are twenty edits; and nothing says which
source went stale or which types have no descriptions. Each of these is a
steward's daily friction and none needs a new concept.

## What changes

| Layer | Change |
| ----- | ------ |
| 1 Strategy | No new element; stage `VS1.2` Curate of the value stream is what this serves |
| 2 Business | New process `BPROC6` Watch the model's health, realising `BSVC2` |
| 3 Information | No new object; the change log and the audit fields are what freshness reads |
| 4 Application | `ASVC2` gains word-by-word search with ranking and bulk edit; new service `ASVC10` Model health; new component `ACMP11` Health and search services; the Browse page, the Health page, `ea set`, `ea health` |
| Transition | New `GAP15` Nothing tells the model's health, closed by this initiative |

## Design

**Search.** A query is split into words; every word must match somewhere in
the element's name, key, identifier, description or attribute values, case
folded. Hits are ranked: a name that starts with the query first, a name that
contains every word next, then everything else; the Browse grid shows a
"matched in" passage (the description or attribute around the first hit) so
the reader knows why a row is there. The same function serves `ea find`. No
search index is built: a few thousand rows are scanned in milliseconds on
DuckDB and Delta alike, and an index is a later optimisation, not a design.

**Bulk edit.** The Browse grid selects many rows. A Bulk edit dialog sets, for
every selected element, any of: status, current state, target state, work
package, target note, lifecycle status, or one attribute; a field left empty is
not touched. The edit runs on the current branch through the repository
service, one audited update per element, and reports how many changed and any
that were refused (a validation error on one element does not stop the rest).
`ea set ID... --target-state change --work-package WP-…` does the same from the
command line.

**Health.** A Health page in two halves. *Freshness*, per source system: the
last load, elements and relationships, how many rows have not been updated in
30, 90 and 180 days, and the change-log activity of the last twelve weeks;
plus the elements never updated since their first import. *Completeness*, per
element type: the share of elements with a description, with at least one
link, with at least one relationship, with every required attribute filled,
and with a decided target state; and the relationship-type coverage the impact
footer already computes. Every number links to the Browse page filtered to the
rows behind it, so a steward goes from a number to the fix. `ea health` prints
the same figures.

## Work packages

| # | Work package | Delivers | Effort |
| - | ------------ | -------- | ------ |
| 1 | Search | The ranked word search in the store and the service, the matched-in passage on Browse, `ea find` on the same function; tests | about half a day |
| 2 | Bulk edit | Multi-select on Browse, the dialog, `bulk_update()` in the repository service, `ea set`; tests | about half a day |
| 3 | Health | The health service, the Health page, `ea health`; tests | about one day |

## In scope

Everything above on the current branch semantics: search reads the branch the
reader is on, bulk edit writes to it, health reads it.

## Out of scope

A search index or a vector index; saved searches; bulk edit of relationships;
scheduled health reports and alerts; freshness against the source systems
themselves (that is `PLAT3`, once feeds exist).

## Delivered

Built on 2026-09-06 on `main`: the ranked word search (`src/ea/services/search.py`)
with the matched-in passage on Browse and `ea find`; multi-select and the Bulk
edit dialog on Browse over `RepositoryService.bulk_update()`, and `ea set`; the
health service (`src/ea/services/health.py`), the Health page with freshness
per source and completeness per type, every figure linking to Browse, and
`ea health`; tests in `tests/test_health.py`.

## Approvals

| Gate | Decision | By | When | What was shown |
| ---- | -------- | -- | ---- | -------------- |
| Direction | Approved | The product owner | 2026-09-06, in the conversation ("Smaller but felt daily: full-text search over descriptions, bulk edit, and freshness and completeness dashboards", first in the owner's order of importance) | The list of what was still missing after initiative 5 |
| Understanding | Approved by the same message | The product owner | 2026-09-06 | The three features as described in the earlier answer; this document records the design as built |
| Design | N/A — Depth 1; the design section above is the design | — | — | — |
