# Application services

_[← Application layer](./README.md) · [EA home](../README.md)_

**Status: `◐` draft catalogue** — the services the running code offers today,
named after the four deliverables the owner asked for on 2026-09-05. Validated
at the **Understanding** gate.

| ID | Service | Offered to | Where |
| -- | ------- | ---------- | ----- |
| `ASVC1` | **Metamodel management** — see the type graph, edit element types, relationship types, attributes and notation in tables, save to the store, export the result as a YAML pack, reload from file; the Notation tab edits how every domain and type is drawn, with a live preview (every user may write in the PoC; roles are documented, not enforced) | The framework owner, the information architect | Metamodel page; `ea init`, `ea load-pack`, `ea export-pack`, `ea summary` |
| `ASVC2` | **Element browsing and editing** — search by type, text and status; open an element with its Markdown description, links, typed attributes, relationships in and out, neighbourhood graph and history; edit and save with conflict detection; add or remove relationships; create a new element | Architects and stewards | Browse and Element pages; `ea find`, `ea get` |
| `ASVC3` | **CSV ingestion** — validate and load `elements.csv`, `relationships.csv` and `links.csv` against the metamodel, with an optional column mapping for a tool's export format, producing a report of errors and warnings; idempotent on source system and reference | Whoever exports from the current tool (a diagram-centric tool today) | Import page; `ea import`, `ea validate` |
| `ASVC4` | **Graph query** — neighbours to a depth, upstream and downstream traces, impact summary by type and completeness, read-only SQL over the schema | Architects, the agent | Impact page and the Graph tab; `ea neighbours`, `ea trace`, `ea impact`, `ea sql` |
| `ASVC5` | **Grounded question answering** — natural-language questions answered through tools over the model, with the tool trace shown and every identifier in the answer checked against what the tools returned; the answer is composed into a document with the elements involved, generated views and the tool trace, downloadable as Markdown. On Databricks the target is a Genie-based agent, or whichever agent framework the platform offers, that traverses the graph and answers in Markdown, with questions, answers and user feedback logged (plateau `PLAT5`) | Architects, and any user who would rather ask than browse | Ask page |
| `ASVC6` | **Architecture views** — a neighbourhood, an impact or an answer rendered as an architecture diagram in the notation of this repository's own documents (Mermaid), copied or downloaded as Markdown; the same view as a draft draw.io file with ArchiMate stencils and a link on every shape; shapes can be moved on the canvas and the draw.io export follows the arrangement, which is never saved | Architects, the agent | Element (Graph tab), Impact and Ask pages; `ea view` |
| `ASVC7` | **Branches and merge** — start a branch from `main`, work on it (edit, import, ask) as if it were the model, see its change set against `main` with conflicts, merge it with a choice per conflict, or abandon it | Architects | **Pending — initiative 4**: header branch selector, Branches page, `ea --branch` |
| `ASVC8` | **Target state** — current state against target state for every element and relationship, counted and listed per work package, drawn as a generated view with state markers | Architects, the organisation | **Pending — initiative 4**: Target state page, the State card on the Element page |
| `ASVC9` | **Propose** — hand in a document (text, files, links) describing a change; an agent derives the change set, links what exists, adopts what is new as proposed, pushes back when the sources are insufficient; the architect applies the result to a branch | Architects | **Pending — initiative 5**: Propose page, the Proposal Template |

## Relationships

| From | | To | | Relationship | Note |
| ---- | - | -- | - | ------------ | ---- |
| `ASVC5` | ⚙ «Application Service» Grounded question answering | `ASVC4` | ⚙ «Application Service» Graph query | uses | the agent's tools are the query service |
| `ASVC2` | ⚙ «Application Service» Element browsing and editing | `ASVC1` | ⚙ «Application Service» Metamodel management | constrained by | allowed types, attributes and relationship pairs come from the metamodel |
| `ASVC3` | ⚙ «Application Service» CSV ingestion | `ASVC1` | ⚙ «Application Service» Metamodel management | constrained by | validation report against the pack |
| `ASVC5` | ⚙ «Application Service» Grounded question answering | `ASVC6` | ⚙ «Application Service» Architecture views | uses | every answer document carries at least one view |
| `ASVC6` | ⚙ «Application Service» Architecture views | `ASVC4` | ⚙ «Application Service» Graph query | uses | a view is a rendered query |
| `ASVC9` | ⚙ «Application Service» Propose | `ASVC7` | ⚙ «Application Service» Branches and merge | uses | **Pending — initiative 5**: a proposal always lands on a branch |
| `ASVC9` | ⚙ «Application Service» Propose | `ASVC4` | ⚙ «Application Service» Graph query | uses | **Pending — initiative 5**: the agent resolves names against the model |
| `ASVC8` | ⚙ «Application Service» Target state | `ASVC6` | ⚙ «Application Service» Architecture views | uses | **Pending — initiative 4**: the work package view carries state markers |
| `ASVC2` | ⚙ «Application Service» Element browsing and editing | `ASVC7` | ⚙ «Application Service» Branches and merge | constrained by | **Pending — initiative 4**: edits land on the current branch |
