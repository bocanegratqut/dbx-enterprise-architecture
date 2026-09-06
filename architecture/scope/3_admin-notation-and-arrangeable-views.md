# Initiative 3 — Notation editing, arrangeable views, and the app's presentation

_[← Scope index](./README.md) · [EA home](../README.md)_

**Requester:** the product owner (the university's data and analytics unit).
**Agent:** the coding agent in this repository. **Reviewer:** the product owner.
**Baseline:** initiatives 1 and 2, in flight. **Target plateau:** `PLAT1`,
extended.

## Why

Two asks from the owner on 2026-09-05, after seeing the generated views:

1. The metamodel, **including its visual styles**, should be edited in the app
   by an **admin user**. Today the Metamodel page edits types, relationship
   types and attributes, and since initiative 2 carries the notation columns
   in the types grid, but every signed-in user can save, and the visual styles
   have no editor of their own, no preview, and the domain colours the app
   uses are still hard-coded (a breach of principle `P5`).
2. Architects should be able to **move the shapes** of a generated view on the
   canvas, without saving anything, and **export the arrangement to draw.io**.
   Nothing changes in the model; the arrangement lives in the browser for the
   duration of the page (principle `P8` holds: diagrams stay generated views,
   never a store).

## What was checked

- The rendered Mermaid diagram is ordinary SVG: one `g.node` per element with
  a `translate(x, y)` transform, one `path` per relationship whose id names
  both ends, one `g.edgeLabel` per label carrying the edge id, and one
  `g.cluster` per layer with its rectangle. Dragging needs no plugin: a small
  piece of app JavaScript moves the node group, redraws the paths of its
  relationships as straight connectors, and grows the layer box to keep its
  nodes inside. Mermaid's own layout engine is not re-run, so nothing else
  moves.
- The app's client runtime exposes `set_props`, so the browser can hand the
  positions to a store that the draw.io export reads. Nothing is persisted.
- The draw.io renderer already places shapes by coordinates; it takes the
  browser's positions instead of its grid when they are present.

## What changes

| Layer | Change |
| ----- | ------ |
| 1 Strategy | No new element. `P5` is what forces the domain colours into the pack; `P8` is what keeps arrangements unsaved |
| 2 Business | Still a `Gap`. The four roles (Admin, Architect, Reader, Agent) are documented in the design section below and referenced from the front door; none is enforced in the PoC; they become business roles when the business layer is written |
| 3 Information | `DOBJ1.5` Notation gains the domain colour used by the app's badges and graphs; `DOBJ2.4` Architecture view gains a session-only arrangement (positions in the browser, never stored) |
| 4 Application | `ASVC1` Metamodel management gains a notation editor with a live preview; `ASVC6` Architecture views become arrangeable and export the arrangement; `ASVC5` answers are presented view-first with the Markdown copyable; `ASVC4` graph query gets grouped, overlap-free graphs; `ACMP6` carries the new panels, `ACMP8` takes positions |
| Transition | `GAP11` in [1_target-state.md](../6_transition/1_target-state.md) |

## Design

**Roles, documented and not enforced.** The owner decided (2026-09-05) that
the PoC needs no permissions: every user is an admin. The roles are written
down here so that the Databricks workspace groups can carry them when the app
runs there (plateau `PLAT2`), and the business layer, still a gap, can start
from them.

| Role | May | Carried by, later |
| ---- | --- | ----------------- |
| **Admin** | Edit the metamodel and its notation, load packs, import content, everything below | A workspace group named in configuration |
| **Architect** | Create and edit elements, relationships and links; run imports into a draft state; ask the agent | A workspace group; per-type owners and stewards refine it at plateau `PLAT4` |
| **Reader** | Browse, query, ask the agent, download views and documents | Every signed-in workspace user |
| **Agent** | Read through tools and propose views; never writes (principle `P3`) | The app's service principal, on behalf of the asking user |

Element editing stays open to everyone, as it is today.

**Ask page and documents.** The answer document leads with its generated
view, then the answer, then the elements as a styled table with type badges
and links, then the tool trace as a timeline; the ungrounded identifiers, if
any, as a warning under the answer. A "Copy Markdown" button puts the whole
document on the clipboard, and "Download Markdown" and "Download draw.io"
stay. The same typography applies to every Markdown the app renders.

**Graph visualisation.** The three force-directed graphs (Element
neighbourhood, Impact, Metamodel type graph) become one graph panel: a
"group by" selector (domain, layer, type, status, source system; none) that
nests the nodes in labelled boxes, a compound-aware layout that keeps boxes
apart and nodes inside them, nodes coloured and shaped from the notation with
wrapped labels, curved edges with labels on hover, fit and zoom controls and
the legend. The reference is the Databricks industry data model viewer's
domain and sub-domain grouping; the interaction model (click a node to open it,
tap to see its detail) is unchanged.

**Notation editor.** A "Notation" tab on the Metamodel page: one grid for the
domains (colour, default layer, glyph, stereotype, ArchiMate element, shape)
and one for the element types (the same, as overrides; blank means inherit),
with dropdowns for layer, shape and ArchiMate element, and a live preview that
renders one sample node per type with the values in the grids before they are
saved. Saving writes the pack to the store like the other tabs; Export writes
it to YAML. The app's domain colours come from the pack (`notation.colour`,
a palette name, and `notation.hex`), with a neutral default when a domain
declares none; the hard-coded map goes.

**Arrangeable views.** On the Element, Impact and Ask pages the generated
diagram's nodes can be dragged. Relationships follow as straight connectors
with their labels at the midpoint; the layer box grows to contain its nodes.
"Reset layout" re-renders the diagram. The positions of every node, from the
initial layout onwards, sit in a browser-side store; "Download draw.io" sends
them with the request and the export places the shapes exactly there, with
the layer boxes as background groupings sized to their nodes. "Download
Markdown" is unchanged: Mermaid carries no positions. Nothing is saved on the
server, and a reload restores the generated layout.

## Work packages

| # | Work package | Delivers | Effort |
| - | ------------ | -------- | ------ |
| 1 | Roles documented, not enforced | The roles table below, in this document and on the front door; every user is an admin in the PoC; workspace groups map to the roles at plateau `PLAT2` | done with this document |
| 2 | Notation editor and colours as data | Notation tab with domain and type grids, dropdowns, live preview; `notation.colour` and `notation.hex` on domains in the pack schema and the higher-education pack; badges, legend and graph stylesheet read the pack | Done |
| 3 | Arrangeable views and positioned export | Drag on the rendered SVG with connector redraw and layer boxes; positions store; "Reset layout"; draw.io export from positions; tests for the renderer with positions | Done |
| 4 | Ask page and document presentation | The generated view first, then the answer, the elements as a styled table, the tool trace as a timeline; the whole Markdown copyable in one click and downloadable; the same typography for every document in the app; header and navigation polish | Done |
| 5 | Graph visualisation | One graph panel for the Element, Impact and Metamodel pages: group by domain, layer, type, status or source system as nested boxes; a grouped grid (after the Databricks model viewer) and a compound-aware organic layout; nodes styled from the notation; curved edges with wrapped labels; fit, zoom and legend | Done |

## In scope

Everything above, on the sample model; tests for the pack round trip with
colours, the positioned draw.io export and the grouped graph elements.

## Out of scope

Saving arrangements (a stored diagram would be a hand-drawn store, declined in
[decision 0005](../decisions/0005-generated-views.md)); re-running the layout
engine after a move; editing labels or adding shapes on the canvas; any
permission enforcement (owner's decision; workspace groups at `PLAT2`);
steward and owner roles for element editing (`PLAT4`).

## Approvals

| Gate | Decision | By | When | What was shown |
| ---- | -------- | -- | ---- | -------------- |
| Direction | Approved | the product owner (Requester) | 2026-09-05, in the conversation | The request itself: metamodel and visual styles edited in the app by an admin; shapes movable on the canvas without saving, exported to draw.io |
| Understanding | Approved with changes | the product owner (Requester) | 2026-09-05, in the conversation | This document as pushed, with three changes from the owner: (1) no permission enforcement in the PoC, every user is an admin for now, roles are documented for when Databricks groups carry them (question 11 answered: yes, based on Databricks groups); (2) the Ask page and the answer document presentation redesigned: diagram first, richer Markdown styling for tables and the rest, the whole Markdown copyable; (3) the graph visualisation improved after the Databricks industry data model viewer: grouping by domain, sub-domain or other criteria, and layouts that do not overlap. Work packages 4 and 5 below were added for (2) and (3); work package 1 shrank to documentation |
| Design | N/A — Depth 1; the design section above is the design | — | — | — |

## Open questions

Question 11 in [open-questions.md](./8_two-gates-and-readable-views.md).
