# Initiative 1 — Curriculum PoC of the EA Repository

_[← Scope index](./README.md) · [EA home](../README.md)_

**Requester:** the product owner (the university's data and analytics unit),
with the information architect validating the information layer. **Agent:** the
coding agent in this repository. **Reviewer:** the product owner.

## Why

The university wants to bring enterprise architecture into the data platform
because it has become a data-integration problem rather than a modelling one
(driver `DRV1`). The business case of 2026-09-05 was reviewed before anything
was built; the review (held privately with the business case) replaced its two
technical cornerstones and the owner reframed the first delivery as a proof of
concept to show and sell within a month, on the curriculum domain, with the
current EA tool's content as the only source for now.

## Baseline and target

- **Baseline:** no repository. The institution's content lives in the current EA
  tool, a diagram-centric tool; exports are possible as CSV.
- **Target plateau:** `PLAT1` Local PoC on DuckDB
  ([6_transition/1_target-state.md](../6_transition/1_target-state.md)).
- **Gap closed:** `GAP3` once the curriculum export is loaded; the code for
  every other deliverable is in place with the sample model.

## Work packages

| # | Work package | Delivers | State (2026-09-05) |
| - | ------------ | -------- | ------------------ |
| 1 | Repository skeleton and the higher-education pack | `pyproject.toml`, `uv.lock`, Apache-2.0 licence, `NOTICE`, `Makefile`; `packs/higher_education/metamodel.yaml` with all 59 exported types (27 active, 32 inactive with instances), 54 relationship types with provenance, `ANY` targets and stewardship qualifiers | Done |
| 2 | Metamodel registry and graph store | `src/ea/metamodel/`, `src/ea/backend/` (portable DDL, DuckDB backend, optimistic concurrency, change log, recursive traces) | Done |
| 3 | CSV ingestion | `connectors/README.md` contract, `connectors/tool-export/mapping.yaml`, `src/ea/importer/` with validation report, idempotent load | Done |
| 4 | Sample model and command line | `data/sample/` (a fictional university's curriculum slice, 45 elements, 93 relationships), `ea` CLI | Done |
| 5 | Web application | Home, Browse, Element (Markdown, links, attributes, relationships, graph, history), Metamodel manager (type graph, editable tables, YAML export), Impact, Import, Ask | Done; verified in a headless browser |
| 6 | Agent | Tool loop over the model with a stub provider (no key) and a hosted-model provider (key required); grounding check on identifiers | Done; stub verified, hosted provider needs a key to verify |
| 7 | Architecture and review documents | This model at `◐`, the business-case review, README and agent instructions | Done |
| 8 | Real curriculum export | The current tool's export loaded through the export mapping; the three reference questions answered on it | **Waiting for the export** |
| 9 | Demo and endorsement | Walk-through with the information architect; Understanding gate recorded below | **Pending** |

## In scope

- Everything generic: metamodel as data, graph store, importer, app, agent.
- The institution's metamodel as the first pack and its content as the only
  content source; one-off CSV exports, loaded manually through the Import page
  or the CLI.
- The curriculum domain as the first content: the Curriculum Logical Data
  Component, everything within two relationship hops of it, and every type on
  the metamodel's Information diagram (the information architect may narrow or
  widen this; open question 1).
- The business glossary (Business Definition, Measure) authored in the
  repository, because the owner decided it should not be a separate silo.
- The Attribute type kept in the pack (inactive in the institution's metamodel)
  so that schemas already in the data platform can populate it later.

## Out of scope (kept on the roadmap)

Write-back to the current EA tool; freshness and steward workflows; proposals
and change sets; scheduled feeds from the CMDB, the HR system, the project
portfolio tool, the information asset register and the data platform's metadata
catalogue; the Delta backend and the deployment bundle; the Unity Catalog
projection, glossary publishing and Genie-based agents; a tool server for
external agents; retirement of the current EA tool. Each is a gap
in [6_transition/1_target-state.md](../6_transition/1_target-state.md).

## Layers touched

| Layer | Change |
| ----- | ------ |
| 1 Strategy | New: stakeholders, drivers, assessments from the review, goals, outcomes, principles ([1_motivation.md](../1_strategy/1_motivation.md)) |
| 2 Business | Not modeled (Depth 1); roles named above |
| 3 Information | New: metamodel, architecture graph, exchange and audit objects ([1_data-objects.md](../3_information/1_data-objects.md)) |
| 4 Application | New: five services, eight components ([4_application](../4_application/README.md)) |
| 5 Technology | Not modeled; the local runtime is one Python process over one DuckDB file, the Databricks runtime is plateau `PLAT2` |
| Transition | New: six plateaus, eight gaps, the sequence ([6_transition](../6_transition/README.md)) |

## Approvals

| Gate | Decision | By | When | What was shown |
| ---- | -------- | -- | ---- | -------------- |
| Direction | Approved | the product owner (Requester) | 2026-09-05, in the conversation | The PoC plan: scope (curriculum, the current EA tool's content as source, CSV exports, DuckDB first with Delta later, no write-back or steward flows, one business case), the design pillars, the four deliverables, the build sequence and the roadmap now written in [1_motivation.md](../1_strategy/1_motivation.md) and [6_transition](../6_transition/1_target-state.md) |
| Understanding | **Pending** | the product owner and the information architect | — | To be shown: [1_motivation.md](../1_strategy/1_motivation.md), [1_data-objects.md](../3_information/1_data-objects.md), the higher-education pack, and the app on the curriculum export. On approval the three documents move from `◐` to `●` |
| Design | N/A — the owner chose "whatever is best, up to you as the builder"; the design is recorded in [decisions](../decisions/README.md) and reviewed through the running app | — | — | — |

The Direction approval covers the plan as it was shown; the code was written
after it. Nothing in this initiative is treated as approved content of the
enterprise model: every loaded element keeps the status it had in the source tool.

## Open questions

Tracked in [open-questions.md](./8_two-gates-and-readable-views.md); the ones raised by this
initiative are numbered 1 to 8 there.
