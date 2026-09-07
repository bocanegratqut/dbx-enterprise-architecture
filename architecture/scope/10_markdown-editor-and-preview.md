# Project Scope — Markdown Editor and Preview

_[← Scope index](./README.md) · [Model home](../README.md)_

**ArchiMate viewpoint:** Implementation & Migration.
**Delivered as:** the working branch (built 2026-09-07; demo pending).

This initiative adds basic Markdown authoring controls and a live preview to the app's Markdown-capable fields, and makes reader views render Markdown consistently, including Mermaid fenced diagrams.

## EA alignment (assessed top-down before implementing)

| Layer | Impact |
| ----- | ------ |
| 0_business-design | Not used — this is a Depth 1 application project. |
| 1_strategy | No new strategy element. The change serves `G1` (Goal 1 — Query the architecture sustainably) by making descriptions and proposal text legible in the app, and `G4` (Goal 4 — Show a working PoC within a month) by improving validation of authored content. |
| 2_business | No new role, process or service. Existing authoring and curation work is unchanged; the authoring surface becomes easier to use. |
| 3_information | No new stored data object and no schema change. Existing Markdown text fields keep storing Markdown source. Mermaid diagrams remain source text inside those fields and are rendered only in the app. |
| 4_application | Shared Markdown editor controls are added for Markdown-capable text fields, with insert actions for heading, bold, table and Mermaid block, plus an edit/preview view. Reader views render Markdown through one shared renderer that also displays Mermaid fences as diagrams. |
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
| **Baseline** (before) | Markdown fields are plain text areas; reader descriptions render Markdown text, but Mermaid fences are not displayed as diagrams. |
| **Target** (delivered) | Markdown-capable fields have basic insert controls and a preview; reader descriptions render Markdown and Mermaid diagrams consistently. |

## Work packages and deliverables

### WP1 — Shared Markdown authoring and rendering

- **Deliverables:** shared UI helpers in `src/ea/ui/components.py`, page adoption in `src/ea/ui/pages/element.py`, `src/ea/ui/pages/browse.py`, `src/ea/ui/pages/ask.py` and `src/ea/ui/pages/propose.py`, supporting IDs in `src/ea/ui/ids.py`, and focused tests.
- **Outcome:** Authors can insert common Markdown structures and preview Markdown before saving or submitting; readers see rendered Markdown with Mermaid diagrams.

## In scope / out of scope

| In scope | Out of scope (gaps, candidate future work) |
| -------- | ------------------------------------------- |
| Heading, bold, table and Mermaid insert actions. | A full rich-text editor, collaborative editing or WYSIWYG Markdown. |
| Edit/preview view for Markdown-capable fields. | Persisting rendered HTML or diagram positions from Markdown descriptions. |
| Mermaid display for fenced `mermaid` blocks in reader/preview views. | Executing arbitrary HTML or script from Markdown. |

## Gap notes

- A full editor would need a larger dependency and a design decision about sanitisation and keyboard behaviour; this initiative keeps Markdown as source text.
- Saved Mermaid layout positions would need a new data model; diagrams embedded in Markdown remain read-only renderings.

## Delivered

Built on 2026-09-07 on the working branch: a shared Markdown renderer and editor in `src/ea/ui/components.py`, pattern IDs in `src/ea/ui/ids.py`, callback registration in `src/ea/ui/app.py`, Markdown authoring controls and previews on the Element, Browse and Propose pages, Ask answer rendering through the same Markdown/Mermaid path, and tests in `tests/test_markdown_components.py`.

## Open questions

- None.