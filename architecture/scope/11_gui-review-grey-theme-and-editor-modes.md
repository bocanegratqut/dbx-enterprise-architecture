# Project Scope — GUI Review, Grey Theme and Editor Modes

_[← Scope index](./README.md) · [Model home](../README.md)_

**ArchiMate viewpoint:** Implementation & Migration.
**Delivered as:** the working branch (built 2026-09-07; demo pending).

This initiative reviews the app's user experience after the Markdown editor landed: a raw/split/preview editor like a code editor, a grey visual theme that keeps diagrams on white, process-ordered actions on the Import and Propose pages, one field per destination on Propose (branch and work package each a single select with a "new" option), the lifecycle text removed from the editing surfaces in favour of the current state, and the debug persona switcher reduced to the four user roles. Two defects found during the review are fixed on the same branch: reader-view Mermaid blocks raised a callback error because they lacked the layout-reset control the renderer declares, and the Impact page offered no elements until two characters were typed.

## EA alignment (assessed top-down before implementing)

| Layer | Impact |
| ----- | ------ |
| 0_business-design | Not used — this is a Depth 1 application project. |
| 1_strategy | No new strategy element. The change serves `G4` (Goal 4 — Show a working PoC within a month): a demo the owner can walk without visual defects. |
| 2_business | No new role, process or service. The Agent role (`ROLE5`) remains the assistant's role; it only leaves the debug persona switcher, which is a testing surface, not a business change. |
| 3_information | No stored data change. `lifecycle_status` stays on the element, in the CSV contract and in the import derivation; it only leaves the editing and browsing surfaces, where the normalised current state is the indicator. |
| 4_application | The web application changes: Markdown editor gains Edit/Split/Preview modes; the shell gains a grey theme; Import orders its actions Download template → Validate only → Load; Propose puts destination (branch, work package, template) left and the proposal right, each destination one select with a New option; Browse and the Element page stop showing and editing the lifecycle text; the Impact selector preloads elements; reader-view Mermaid blocks render without error. |
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
| **Baseline** (before) | Markdown fields show an always-on preview below the text; the app is white throughout; Import and Propose order their actions against the reading flow; Propose has two fields per destination; lifecycle text and current state compete on the browsing and editing surfaces; reader-view Mermaid fails; Impact offers no elements until typed. |
| **Target** (delivered) | Markdown fields switch between raw, split and preview; the shell is grey with white cards and diagrams; actions read left to right in process order; each Propose destination is one field; the current state is the one state indicator on the editing surfaces; reader-view Mermaid renders; Impact offers elements immediately. |

## Work packages and deliverables

### WP1 — Editor modes and reader-view Mermaid fix

- **Deliverables:** `src/ea/ui/components.py`, `src/ea/ui/ids.py`, `assets/styles.css`, `tests/test_markdown_components.py`.
- **Outcome:** Markdown fields behave like a code editor's raw/preview, and Mermaid renders wherever Markdown is displayed.

### WP2 — Grey theme and process-ordered pages

- **Deliverables:** `assets/styles.css`, `src/ea/ui/pages/import_page.py`, `src/ea/ui/pages/propose.py`.
- **Outcome:** A grey shell with white content cards; actions ordered Download template → Validate → Load and destination-left, proposal-right.

### WP3 — One state indicator and persona cleanup

- **Deliverables:** `src/ea/ui/pages/browse.py`, `src/ea/ui/pages/element.py`, `src/ea/ui/layout.py`.
- **Outcome:** Current state is the state shown and edited in the app; the persona switcher offers the four user roles.

### WP4 — Impact preload

- **Deliverables:** `src/ea/ui/pages/impact.py`.
- **Outcome:** The Impact selector lists elements before any typing.

## In scope / out of scope

| In scope | Out of scope (gaps, candidate future work) |
| -------- | ------------------------------------------- |
| Edit/Split/Preview modes on the shared Markdown editor. | A rich-text or WYSIWYG editor. |
| A grey light theme. | A dark theme (rejected: diagrams and pack colours are designed on white). |
| Action order and destination consolidation on Import and Propose. | Reworking the Propose analysis pipeline itself. |
| Lifecycle text off the editing surfaces; current state as the indicator. | Removing `lifecycle_status` from the store, the CSV contract or the import derivation. |
| The persona switcher reduced to Admin, Architect, Reviewer, Reader. | Removing the Agent role from the model or the role service. |
| Fixing reader-view Mermaid and the empty Impact selector. | New Impact analysis features. |

## Gap notes

- A dark theme would need per-pack colour review so generated diagrams stay legible; the grey theme deliberately avoids that.
- Removing `lifecycle_status` from the store would be an information-layer change with import consequences; it stays as source provenance.

## Delivered

Built on 2026-09-07 on the working branch: Edit/Split/Preview modes on the shared Markdown editor and the hidden layout-reset control that fixes reader-view Mermaid (`src/ea/ui/components.py`, `src/ea/ui/ids.py`, `assets/styles.css`); the grey theme (`assets/styles.css`); Import actions ordered Download template → Validate only → Load (`src/ea/ui/pages/import_page.py`); Propose with the destination card first and one select per destination, New options revealing a name input (`src/ea/ui/pages/propose.py`); lifecycle text off Browse, bulk edit and the Element page (`src/ea/ui/pages/browse.py`, `src/ea/ui/pages/element.py`); the persona switcher reduced to the four user roles (`src/ea/ui/layout.py`, `README.md`); the Impact selector preloaded (`src/ea/ui/pages/impact.py`); tests in `tests/test_markdown_components.py`. Role gating was verified in the browser: a Reader sees New element, Bulk edit and Save disabled, and every write path checks the role server-side. Refined on review: the editor's title, insert buttons and mode switch share one header line and the field grows by a native vertical resize handle; the Relationship and other-element selects on the Element page are preloaded instead of empty until typed; every modal carries a full-screen toggle (`modal_title` in `src/ea/ui/components.py`).

## Open questions

- None.
