# Initiative 2 — Generated architecture views and answer documents

_[← Scope index](./README.md) · [EA home](../README.md)_

**Requester:** the product owner (the university's data and analytics unit).
**Agent:** the coding agent in this repository. **Reviewer:** the product owner.
**Baseline:** initiative 1 ([1_curriculum-poc.md](./1_curriculum-poc.md)), in
flight. **Target plateau:** `PLAT1`, extended.

## Why

Architects read architecture diagrams, not graph layouts. The neighbourhood
and impact graphs of initiative 1 are force-directed layouts of typed nodes;
they answer a query but do not look like the diagrams architects work with,
and a new architect gets no picture out of a question to the agent. The owner
considered an embedded draw.io editor with linking and suggestions, then
decided on 2026-09-05 to **avoid diagramming by hand**: diagrams are generated
from the model, the agent answers with a document that carries proper diagrams
in the notation this repository's own architecture uses (Mermaid, archreator
style), and, later, the agent can offer a draft draw.io file with the relevant
components for an architect to reuse. Hand-drawn diagrams as a store are the
current EA tool's problem this project exists to leave behind (assessment `ASM7`,
principle `P8`).

## What changes

| Layer | Change |
| ----- | ------ |
| 1 Strategy | New assessment `ASM7` and principle `P8` in [1_motivation.md](../1_strategy/1_motivation.md); approved at Direction below |
| 3 Information | New objects: `DOBJ1.5` Notation (per element type, in the pack), `DOBJ2.4` Architecture view, `DOBJ3.5` Answer document, in [1_data-objects.md](../3_information/1_data-objects.md) |
| 4 Application | New service `ASVC6` Architecture views; `ASVC5` answers become documents; new component `ACMP8` View generator, in [4_application](../4_application/README.md) |
| Transition | Gaps `GAP9` and `GAP10` in [1_target-state.md](../6_transition/1_target-state.md); step 1b in [2_sequence.md](../6_transition/2_sequence.md) |
| Decisions | [0005](../decisions/0005-generated-views.md) records why generated views, not an editor |

## Design

**One view model, several renderers.** A view is a subgraph selected from the
model: a focus, the elements, the relationships among them, and a title. It
is produced by the existing queries (neighbourhood to a depth, impact
upstream and downstream) or by an agent answer (the identifiers the tools
returned, plus the relationships among them from the store). The view knows
nothing about drawing. Renderers turn it into:

1. **Mermaid**, in the notation of this repository's architecture documents:
   one subgraph per pack domain, nodes written `glyph «Stereotype» Name [ID]`,
   edges labelled with the relationship name, colours per domain. Rendered in
   the app (Mermaid bundled with the app, no external request) and copied or
   downloaded as Markdown, so the same diagram renders in a pull request, in
   the archreator portal and in any Markdown viewer.
2. **draw.io**, later: the same view as an mxGraph file using ArchiMate 3
   stencils by stereotype, laid out by domain row, each shape carrying the
   element identifier as a custom property and a link to its page. A draft
   for an architect to reuse and arrange, never a store.

**Notation is data.** Each element type in the pack may declare `notation`
(glyph, stereotype, ArchiMate element, shape); a type without one inherits its
domain's default. The engine reads the fields and knows nothing about the institution's metamodel or
ArchiMate (principle `P5`).

**Answers become documents.** An agent answer is composed into a Markdown
document: the question, the answer, a table of the elements involved with
links, one or more views as Mermaid, the identifiers the tools returned, any
identifier the answer cited that no tool returned, and the tool trace. The
diagram is built from tool results by the app, never written by the model
(principle `P6`). The document is rendered in the Ask page and downloadable.
Whether answer documents are saved in the repository is open question 10.

## Work packages

| # | Work package | Delivers | State |
| - | ------------ | -------- | ------ |
| 1 | View model, notation, Mermaid renderer | `src/ea/views/`; `notation` in the pack schema and the higher-education pack; Mermaid views on the Element (Graph tab) and Impact pages beside the existing graphs; copy and download as Markdown; bundled Mermaid | Done 2026-09-05 (verified in a headless browser) |
| 2 | Answer documents | The document composer; the Ask page renders the document with its diagrams; download as `.md`; the hosted provider gets a tool to request an extra view for a set of identifiers | Done 2026-09-05 (stub provider verified; hosted provider needs a key) |
| 3 | draw.io draft export | The mxGraph renderer over the same view model with ArchiMate 3 stencils and the linking contract (`ea_id` custom property, link to the element page); download from the Element, Impact and Ask pages | Done 2026-09-05 (file opens in draw.io; verified by parsing, not by eye) |

## In scope

Generated views only; the three renderers above; the higher-education pack's notation
table (ArchiMate stereotypes per type, open question 9); the sample model as
the demo content; tests for the view model and both renderers on the sample.

## Out of scope

An embedded diagram editor; importing hand-drawn diagrams and linking their
shapes; suggestions of matching elements while drawing; storing diagrams as
the source of relationships. All of it was considered and declined
([decision 0005](../decisions/0005-generated-views.md)); the linking contract
in work package 3 keeps the import path open should the hypothesis that
architects will bring diagrams ever be worth testing.

## Approvals

| Gate | Decision | By | When | What was shown |
| ---- | -------- | -- | ---- | -------------- |
| Direction | Approved | the product owner (Requester) | 2026-09-05, in the conversation | The comparison of an embedded draw.io editor with linking and suggestions, a home-built editor, and generated views; the owner chose generated views ("let's go with the simple one, agreed that we should avoid diagramming by hand"), answer documents with Mermaid diagrams in the archreator style, and a draft draw.io export later. `ASM7` and `P8` record that choice |
| Understanding | Approved | the product owner (Requester) | 2026-09-05, in the conversation ("approved") | This document; `ASM7` and `P8`; `DOBJ1.5`, `DOBJ2.4`, `DOBJ3.5`; `ASVC6` and the changed `ASVC5`; `ACMP8`; the default notation mapping (open question 9) and "answer documents not stored" (open question 10) as the interpretations to proceed on; the three work packages including the draw.io export inside the PoC month |
| Design | N/A — Depth 1, the design section above and decision 0005 are the design; reviewed through the running app | — | — | — |

## Delivered

- `src/ea/views/` (view model, Mermaid and draw.io renderers), `notation` in the
  pack schema and on 47 types of the pack, `Registry.notation()`, the `notation`
  columns in the store with a start-up migration, the metamodel grid editing
  notation, Mermaid bundled under `assets/vendor/`, the Element and Impact pages
  showing the generated view with Markdown and draw.io downloads, the answer
  document composer and the Ask page rendering it, the `propose_view` tool for
  both providers, `ea view` on the command line, nine tests.
- Not delivered: nothing from the three work packages. The demo with the
  information architect is the remaining step of the PoC as a whole
  (initiative 1, work package 9).

## Open questions

Questions 9 and 10 in [open-questions.md](./open-questions.md).
