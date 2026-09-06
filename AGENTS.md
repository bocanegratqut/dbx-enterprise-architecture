# AGENTS.md

**EA Repository** — a generic, metamodel-driven enterprise architecture
repository that runs on DuckDB locally and on Databricks later, configured
first with an anonymised higher-education metamodel. This file is the standing instruction for any
coding agent (and any person) working in this repository. The model of the
project itself lives in [`architecture/`](./architecture/README.md); the code
lives in [`src/ea/`](./src/ea).

## The rule that governs everything else

**Strategy and information architecture are validated before any other layer,
and the Requester approves at explicit gates before development.** A change in
requirements is never coded directly: align it through the numbered EA layers
(`architecture/1_strategy` → `3_information` → `4_application`), stop at the
gates for the Requester's approval, record it in a scope document
(`architecture/scope/`), then implement. Pure bug fixes that change no
documented behaviour skip the alignment and the gates, but still keep the
docs true.

**The PoC posture** (initiatives 1 to 5, built; the Databricks step next):
iterate and fail fast inside the approved scope, keep the long-term roadmap in
[`architecture/6_transition/`](./architecture/6_transition/README.md) honest,
and never quietly widen the PoC with a roadmap item.

## Who decides

| Role | Who | Does |
| ---- | --- | ---- |
| **Requester** | The product owner (a university's data and analytics unit), with the information architect validating the information layer | Says what should change — a requirement or a problem, not a diff. **Grants the gate approvals** before any code is written |
| **Agent** | The coding agent (or a person) | Works the change through the layers, stops at each gate, writes the scope document, implements, opens a pull request |
| **Reviewer** | The product owner | Reviews and merges. Nothing ships without a human approving it |

An approval that isn't recorded didn't happen: every gate is written into the
scope document's Approvals table, with who approved, when, and what was shown.

## Modeling depth

**Declared depth: 1 — Application.** The repository manages an enterprise
model but is itself one application; its strategy layer is light (motivation
only), its business and technology layers are declared gaps on the front door
until the PoC has users and runs on Databricks. The enterprise content it holds
(the institution's elements) is data inside the application, not this model.

## Layout

- `architecture/` — the model of this project. Its `README.md` is the front
  door and says, per layer, what is modeled, what is a gap and why.
  **A folder exists only once it holds something.** Every document that
  defines an element says how far it has been validated (`○`, `◐`, `●`);
  `scripts/check_model.py` fails one that declares nothing.
- `architecture/reference/` — says what the model was built from (the owner's
  business case and the institution's metamodel document), which are held
  privately and are not in this public repository.
- `packs/` — metamodels as data (`higher_education` today). `connectors/` — the
  CSV contract and per-tool column mappings (`tool-export`). `data/sample/` — a
  fictional university's curriculum slice so the demo works without real data.
- `src/ea/` — `models` → `metamodel` → `backend` → `services` → `views`,
  `importer`, `agent` → `ui`, plus `cli.py`. `views/` renders a subgraph of the
  model as Mermaid or draw.io from the pack's `notation`; nothing is drawn by
  hand and every shape carries an element identifier (principle `P8`). `ui/graph.py`
  is the one network-graph panel (grouping, layouts, pack colours);
  `assets/ea-views.js` lets a reader arrange a generated view without saving it. A module imports only from layers to its
  left; SQL lives in `backend/` only; framework and institution names live in
  `packs/` and `connectors/` only.
- **Branches and states.** `main` is the model; a branch is an overlay on the
  same tables (decision 0006), and the current branch is a context variable
  (`backend/branching.py`) that every read and write honours: the app sets it
  from the session, the CLI from `--branch`, a service from `use_branch()`.
  Never write to `branch_*` tables directly and never bypass it. Every element
  and relationship carries `current_state`, `target_state`,
  `target_work_package` and `target_note` (decision 0007); the vocabularies
  live in `models.py` and are not extended per pack. The Propose module
  (`agent/proposal.py`) writes only to a branch and only what the architect
  ticked.
- **Roles.** The role is a context variable too (`services/roles.py`), set per
  request from the identity headers (or the debug persona under mock
  authentication) and from `--as` on the command line. `allowed()` is the only
  place that knows what a role may do; every writing path calls `require()`
  and the pages hide what the role may not use. A branch in review is frozen.
  Never add a write path without its `require()`.
- `tests/` — pytest on an in-memory DuckDB. `scripts/` — the two archreator
  validators, run before every push.

## Commands

```bash
make install     # uv sync (runtime and dev dependencies)
make seed        # create data/ea.duckdb, load the higher-education pack and the sample model
make run         # http://localhost:8050 (Dash debug server, no reloader)
make check       # ruff + pytest + the two validators — must be green before pushing
uv run ea --help # the CLI: init, import, validate, find, get, set, neighbours, trace, impact, view, target, health, sql, summary, branch …, reviewers …; --branch and --as on any command
```

The DuckDB file is single-writer: stop the app before running the CLI on the
same file, or point `EA_DB_PATH` elsewhere.

## Conventions

- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, …).
- Documentation language: **English**. Australian spelling in prose is fine;
  identifiers and pack keys are ASCII `snake_case`.
- Element identifiers in `architecture/` follow archreator's prefixes
  (`STK`, `DRV`, `ASM`, `G`, `OUT`, `P`, `DOBJ`, `ASVC`, `ACMP`, `PLAT`,
  `GAP`); identifiers of enterprise content inside the repository follow the
  pack's prefixes (`LDC-…`, `DE-…`) and are not archreator identifiers.
- No model names or vendor identifiers in commit messages, code comments or
  documents; the agent provider is configured by environment variable.
- Nothing institution-specific anywhere, and nothing framework-specific in
  `src/`: a type name belongs in a pack, a column name in a mapping, an example
  in the sample data. **This repository is public: never name the organisation
  it was built for, its people, its tools or its internal systems.**
