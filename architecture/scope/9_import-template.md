# Project Scope — Import Template

_[← Scope index](./README.md) · [Model home](../README.md)_

**ArchiMate viewpoint:** Implementation & Migration.
**Delivered as:** the working branch.

This initiative adds a downloadable CSV import template to the Import page so a prospective adopter can get the expected file shape from the product itself, instead of reading the connector contract and inventing the files by hand.

## EA alignment (assessed top-down before implementing)

| Layer | Impact |
| ----- | ------ |
| 0_business-design | Not used — this is a Depth 1 application project. |
| 1_strategy | No new strategy element. The change serves `G4` (Goal 4 — Show a working PoC within a month) by making local validation easier, and `G5` (Goal 5 — Reusable by any enterprise) by giving adopters a generic import starting point. |
| 2_business | No change. The existing content entry and curation work still covers import; no new role, process, service or rule is introduced. |
| 3_information | No new stored data object. The template represents the existing `DOBJ3` (Data Object 3 — Exchange and audit) exchange files contract and does not change the CSV columns or validation rules. |
| 4_application | The Import page gains a Download template action that emits a short guide with sample `elements.csv`, `relationships.csv` and `links.csv` files in one archive. |
| 5_technology | No runtime, build, hosting or storage change. |

## Approvals

| Gate | Approved by | Date | What was approved |
| ---- | ----------- | ---- | ----------------- |
| Gate 0 — Business model | N/A — subject is a single application. | 2026-09-07 | N/A |
| Gate 1 — Strategy | N/A — no new stakeholder, driver, goal, principle or value stream change. | 2026-09-07 | N/A |
| Gate 2 — Business | Requester | 2026-09-07 | This scope document and the no-change verdicts for strategy, business and information; approved in the conversation. |
| Gate 3 — Solution design | N/A — not requested by the Requester. | 2026-09-07 | N/A |

## Plateaus

| Plateau | State |
| ------- | ----- |
| **Baseline** (before) | The Import page explains the CSV contract and points to the command line, but the user must open documentation or examples to assemble files. |
| **Target** (delivered) | The Import page offers a downloadable template archive containing a short guide and the three contract CSVs with example rows and headers. |

## Work packages and deliverables

### WP1 — Downloadable import template

- **Deliverables:** `templates/import-template/`, `src/ea/ui/pages/import_page.py`, `src/ea/ui/ids.py`, tests for the download callback.
- **Outcome:** A user can download a ready-to-edit import template directly from the Import page.

## In scope / out of scope

| In scope | Out of scope (gaps, candidate future work) |
| -------- | ------------------------------------------- |
| A generic template for the existing no-mapping CSV contract. | A per-metamodel generated template with every type-specific attribute column. |
| A single downloadable archive from the Import page. | A wizard, spreadsheet validation, or in-app editing of template rows. |
| Brief page text explaining the relationship to `connectors/README.md`. | Changing importer semantics, validation rules, mappings, or sample repository content. |

## Gap notes

- A generated per-pack template would need attribute-aware template generation from the loaded metamodel; this initiative deliberately keeps the template stable and generic.
- Spreadsheet-native validation would need a separate export format and client workflow; CSV remains the repository contract.

## Open questions

- None.