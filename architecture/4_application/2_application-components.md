# Application components

_[← Application layer](./README.md) · [EA home](../README.md)_

**Status: `◐` draft catalogue** — the components as they exist in the code on
2026-09-05. A row marked **Pending** names the initiative that will build it.
Validated at the **Understanding** gate; the **Design** gate is offered but not
required at Depth 1.

## Layering rule

`models → metamodel → backend → services → views / importer / agent → ui`. A module
imports only from layers to its left. SQL lives in `backend/` only
(principle `P4`); framework and institution names live in `packs/` and
`connectors/` only (principle `P5`).

## Components

| ID | Component | Code | Realizes | State |
| -- | --------- | ---- | -------- | ----- |
| `ACMP1` | **Metamodel registry** — loads a pack, validates references and supertype cycles, resolves type and relationship names, computes inherited attributes and allowed pairs, validates elements and relationships, summarises the metamodel for the agent | `src/ea/metamodel/loader.py`, `src/ea/metamodel/registry.py`, `src/ea/models.py` | `ASVC1` | Running |
| `ACMP2` | **Graph store** — the storage interface: schema, packs, elements, links, relationships, traces, history, read-only SQL | `src/ea/backend/base.py`, `src/ea/backend/sql.py` (portable DDL and recursive trace queries), `src/ea/backend/factory.py` | `ASVC2`, `ASVC4` | Running |
| `ACMP2.1` | **DuckDB backend** — the interface on one DuckDB file; optimistic concurrency on `_version`, change log on every write, frame-based upserts, guarded read-only SQL | `src/ea/backend/duckdb_backend.py` | `ASVC2`, `ASVC4` | Running |
| `ACMP2.2` | **Databricks backend** — the same interface on Delta tables in a Unity Catalog schema through a SQL warehouse, same DDL and MERGE semantics | `src/ea/backend/factory.py` raises until it exists | `ASVC2`, `ASVC4` | **Pending — initiative 3** (plateau `PLAT2`) |
| `ACMP3` | **Repository and graph services** — element and relationship operations with validation and identifier minting; a cached in-process graph for neighbours, traces, impact and completeness; Cytoscape-ready subgraphs | `src/ea/services/repository.py`, `src/ea/services/graph.py` | `ASVC2`, `ASVC4` | Running |
| `ACMP4` | **Importer** — reads a directory of CSV files through a mapping, builds elements, relationships and links, validates against the registry, reports, loads idempotently | `src/ea/importer/csv_import.py`, `src/ea/importer/mapping.py`, `connectors/tool-export/mapping.yaml` | `ASVC3` | Running |
| `ACMP5` | **Agent** — a tool-calling loop with a provider interface: a hosted-model provider when a key is present, a stub provider that runs the tools without a model otherwise; grounding check of every identifier in the answer | `src/ea/agent/agent.py`, `src/ea/agent/tools.py` | `ASVC5` | Running (stub locally; the hosted provider needs a key, see the scope document) |
| `ACMP6` | **Web application** — Dash pages Home, Browse, Element, Metamodel, Impact, Import, Ask on a Mantine shell with AG Grid tables and Cytoscape graphs and Mermaid views rendered in the browser from a bundled library; mock persona locally, forwarded identity headers on Databricks Apps; one graph panel (`src/ea/ui/graph.py`) with grouping, compound-aware layouts and pack-driven colours; the Notation tab; the drag-and-arrange script for generated views (`assets/ea-views.js`) | `src/ea/ui/` (`app.py`, `layout.py`, `context.py`, `components.py`, `pages/`), `app.py`, `app.yaml`, `assets/` | `ASVC1`–`ASVC5` | Running |
| `ACMP7` | **Command line** — `ea` with init, load-pack, export-pack, import, validate, stats, find, get, neighbours, trace, impact, sql, summary | `src/ea/cli.py` | `ASVC1`–`ASVC4` | Running |
| `ACMP8` | **View generator** — builds a view (focus, elements, relationships) from a query or a set of identifiers and renders it: Mermaid in the archreator notation from the pack's `notation`, draw.io with ArchiMate stencils and the element identifier on every shape, at grid positions or at the positions the browser reports | `src/ea/views/model.py`, `src/ea/views/mermaid.py`, `src/ea/views/drawio.py`; the answer composer `src/ea/agent/document.py` | `ASVC6`, `ASVC5` | Running |
| `ACMP9` | **Branch overlay and merge** — the request-scoped current branch, the overlay reads and writes of the store, the diff with base versions and the merge with per-conflict resolution | `src/ea/backend/` (overlay), `src/ea/services/branches.py` | `ASVC7` | **Pending — initiative 4** |
| `ACMP10` | **Proposal agent** — reads sources, resolves names against the model, returns a structured change set with pushback; a stub parses the Proposal Template's tables, a hosted provider reads free text | `src/ea/agent/proposal.py`, `templates/proposal-template.md` | `ASVC9` | **Pending — initiative 5** |

## Relationships

| From | | To | | Relationship | Note |
| ---- | - | -- | - | ------------ | ---- |
| `ACMP6` | ▭ «Application Component» Web application | `ACMP3` | ▭ «Application Component» Repository and graph services | uses | every page goes through the services, never the store |
| `ACMP6` | ▭ «Application Component» Web application | `ACMP4` | ▭ «Application Component» Importer | uses | Import page |
| `ACMP6` | ▭ «Application Component» Web application | `ACMP5` | ▭ «Application Component» Agent | uses | Ask page |
| `ACMP7` | ▭ «Application Component» Command line | `ACMP3` | ▭ «Application Component» Repository and graph services | uses | |
| `ACMP7` | ▭ «Application Component» Command line | `ACMP4` | ▭ «Application Component» Importer | uses | |
| `ACMP5` | ▭ «Application Component» Agent | `ACMP3` | ▭ «Application Component» Repository and graph services | uses | tools are thin wrappers over the services and the read-only SQL of the store |
| `ACMP3` | ▭ «Application Component» Repository and graph services | `ACMP1` | ▭ «Application Component» Metamodel registry | uses | validation and identifier prefixes |
| `ACMP4` | ▭ «Application Component» Importer | `ACMP1` | ▭ «Application Component» Metamodel registry | uses | validation report |
| `ACMP3` | ▭ «Application Component» Repository and graph services | `ACMP2` | ▭ «Application Component» Graph store | uses | through the interface only |
| `ACMP2` | ▭ «Application Component» Graph store | `ACMP2.1` | ▭ «Application Component» DuckDB backend | realized by | |
| `ACMP2` | ▭ «Application Component» Graph store | `ACMP2.2` | ▭ «Application Component» Databricks backend | realized by | **Pending — initiative 3** (the Databricks step of the roadmap) |
| `ACMP6` | ▭ «Application Component» Web application | `ACMP8` | ▭ «Application Component» View generator | uses | Mermaid rendered in the browser from a bundled library |
| `ACMP5` | ▭ «Application Component» Agent | `ACMP8` | ▭ «Application Component» View generator | uses | the answer document embeds views; `propose_view` tool |
| `ACMP8` | ▭ «Application Component» View generator | `ACMP3` | ▭ «Application Component» Repository and graph services | uses | neighbourhood, impact, edges among a set |
| `ACMP8` | ▭ «Application Component» View generator | `ACMP1` | ▭ «Application Component» Metamodel registry | uses | notation per type |
| `ACMP9` | ▭ «Application Component» Branch overlay and merge | `ACMP2` | ▭ «Application Component» Graph store | uses | **Pending — initiative 4** |
| `ACMP6` | ▭ «Application Component» Web application | `ACMP9` | ▭ «Application Component» Branch overlay and merge | uses | **Pending — initiative 4**: branch selector, Branches page |
| `ACMP10` | ▭ «Application Component» Proposal agent | `ACMP3` | ▭ «Application Component» Repository and graph services | uses | **Pending — initiative 5** |
| `ACMP10` | ▭ «Application Component» Proposal agent | `ACMP9` | ▭ «Application Component» Branch overlay and merge | uses | **Pending — initiative 5**: writes to a branch |
| `ACMP6` | ▭ «Application Component» Web application | `ACMP10` | ▭ «Application Component» Proposal agent | uses | **Pending — initiative 5**: Propose page |

## How to add

- **A new element or relationship type**: edit the pack (in the Metamodel page
  or the YAML) and save; no code changes (principle `P1`).
- **A new export format**: add a mapping under `connectors/<tool>/mapping.yaml`;
  the importer needs no change unless the format is not tabular.
- **A new storage engine**: implement `DatabaseBackend` in `src/ea/backend/`
  and register it in `factory.py`; the DDL in `sql.py` is the contract.
- **A new agent provider**: implement the provider protocol in
  `src/ea/agent/agent.py`; the tools stay the same.
- **A new diagram format**: add a renderer over `View` in `src/ea/views/`;
  the view model and the notation in the pack stay the same.
