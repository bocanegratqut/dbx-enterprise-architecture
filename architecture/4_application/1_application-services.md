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

## Relationships

| From | | To | | Relationship | Note |
| ---- | - | -- | - | ------------ | ---- |
| `ASVC5` | ⚙ «Application Service» Grounded question answering | `ASVC4` | ⚙ «Application Service» Graph query | uses | the agent's tools are the query service |
| `ASVC2` | ⚙ «Application Service» Element browsing and editing | `ASVC1` | ⚙ «Application Service» Metamodel management | constrained by | allowed types, attributes and relationship pairs come from the metamodel |
| `ASVC3` | ⚙ «Application Service» CSV ingestion | `ASVC1` | ⚙ «Application Service» Metamodel management | constrained by | validation report against the pack |
| `ASVC5` | ⚙ «Application Service» Grounded question answering | `ASVC6` | ⚙ «Application Service» Architecture views | uses | every answer document carries at least one view |
| `ASVC6` | ⚙ «Application Service» Architecture views | `ASVC4` | ⚙ «Application Service» Graph query | uses | a view is a rendered query |
