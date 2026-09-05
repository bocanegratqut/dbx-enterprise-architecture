# EA Repository

**A generic, metamodel-driven enterprise architecture repository for the
ontology and agent era — DuckDB on a laptop today, Databricks tomorrow, the
same code.** Built first as a proof of concept for a university's data and
analytics unit, on its TOGAF-based metamodel and the curriculum domain; built so any enterprise can
bring its own metamodel.

The repository treats enterprise architecture as what it has become: a data
integration problem. Elements and relationships are rows in a graph you can
query, not shapes in a drawing tool. The metamodel is data, so a new element
type is a row rather than a migration. Everything a person can do in the app
an agent can do through tools, and every answer the agent gives cites the
element identifiers it came from.

## What it does today

| Deliverable | Where |
| ----------- | ----- |
| **Metamodel manager** — the type graph, editable tables for element types, relationship types and attributes, save, export as a YAML pack, reload | Metamodel page |
| **Browse and edit elements** — search by type, text and status; Markdown descriptions, links, typed attributes, relationships in and out, neighbourhood graph, history; optimistic concurrency | Browse and Element pages |
| **CSV ingestion** — `elements.csv`, `relationships.csv`, `links.csv`, an optional mapping for a tool's export (a one-CSV-per-type example included), a validation report, idempotent load | Import page, `ea import` |
| **Impact and traces** — upstream and downstream closure of any element, by type, with completeness hints | Impact page, `ea impact`, `ea trace` |
| **Ask** — questions answered by an agent through tools over the model and composed into a document: the answer, the elements involved, generated architecture diagrams, the tool trace; ungrounded identifiers flagged; downloadable as Markdown; a stub provider runs without any model key | Ask page |
| **Generated architecture views** — any neighbourhood, impact or answer as an architecture diagram in the notation of this repository's own architecture documents (Mermaid, ArchiMate layers and stereotypes from the pack), downloadable as Markdown or as a draft draw.io file with ArchiMate stencils and the element identifier on every shape. Shapes can be dragged to arrange a view (never saved) and the draw.io export follows. Nothing is drawn by hand | Element and Impact pages, Ask page, `ea view` |
| **Graphs with grouping** — every network graph groups its nodes by domain, layer, type, status or source system in labelled boxes, with a grouped grid or an organic layout, coloured from the pack | Element, Impact and Metamodel pages |
| **Notation editor** — how each domain and type is drawn (layer, glyph, stereotype, ArchiMate element, shape, colour) edited in the app with a live preview, saved into the pack | Metamodel page, Notation tab |

The first pack is an anonymised **higher-education** metamodel (59 element types, 27 active; 54
relationship types with provenance, `ANY` targets and stewardship qualifiers).
The sample content is a fictional university's curriculum slice so the demo
runs without any institutional data.

## Quick start

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
make install    # .venv with runtime and dev dependencies
make seed       # data/ea.duckdb with the higher-education pack and the sample model
make run        # http://localhost:8050
```

Without a browser:

```bash
uv run ea stats
uv run ea find "course"
uv run ea get LDC-CURR
uv run ea impact DE-SRS-COURSE --depth 3
uv run ea view LDC-CURR --depth 2                    # Mermaid, archreator notation
uv run ea view DE-SRS-COURSE --impact --fmt drawio --out impact.drawio
uv run ea sql "select type_id, count(*) n from element group by 1 order by 2 desc"
uv run ea validate data/sample            # the validation report without loading
uv run ea import path/to/export --source ea-tool --mapping connectors/tool-export/mapping.yaml
```

Stop the app before running the CLI against the same DuckDB file (one writer
per file), or set `EA_DB_PATH` to another file.

After editing a pack file, load it again (`uv run ea load-pack packs/higher_education/metamodel.yaml`
or **Reload from file** on the Metamodel page): the store holds the pack the app
uses, and the file is only read when asked.

To use a hosted model on the Ask page, set `ANTHROPIC_API_KEY` in the
environment (or a `.env` file); otherwise the stub provider runs the same tools
without a model. `EA_AGENT_PROVIDER` forces `anthropic` or `stub`.

## Loading your own export

1. Export elements and relationships from your current tool as CSV.
2. Either write them in the contract documented in
   [`connectors/README.md`](./connectors/README.md), or add a mapping under
   `connectors/<tool>/mapping.yaml` that renames your columns and type names
   (see [`connectors/tool-export/mapping.yaml`](./connectors/tool-export/mapping.yaml)).
3. `uv run ea validate <dir> --mapping <mapping>` shows what would be rejected
   or flagged; `uv run ea import` loads it. Unknown or inactive types and
   disallowed relationship pairs are flagged, not silently dropped;
   relationships whose ends do not exist are skipped and listed.

## Bringing your own metamodel

A pack is one YAML file: domains, element types (with supertypes, active
flags, attributes, provenance, source of record and owners) and relationship
types (source and target or `ANY`, inverse, qualifiers, provenance). See
[`packs/README.md`](./packs/README.md). Load it with
`uv run ea init --pack packs/<name>/metamodel.yaml`, or edit any pack in the
Metamodel page and export it.

## Configuration

| Variable | Default | Meaning |
| -------- | ------- | ------- |
| `EA_BACKEND` | `duckdb` | Storage engine (`databricks` once the Delta backend lands) |
| `EA_DB_PATH` | `data/ea.duckdb` | DuckDB file |
| `EA_PACK` | `packs/higher_education/metamodel.yaml` | Pack loaded by `ea init` and offered by "Reload from file" |
| `EA_AUTH` | `mock` | `mock` persona locally; `databricks` reads the identity headers Databricks Apps adds |
| `EA_AGENT_PROVIDER` | `auto` | `anthropic` when a key is present, else `stub` |
| `EA_AGENT_MODEL` | (provider default) | Model identifier for the hosted provider |
| `EA_MAX_ROWS` | `5000` | Row cap for Browse and read-only SQL |

## Running on Databricks Apps

`app.yaml` starts the app with `uv run --frozen --no-dev python app.py`,
which binds `0.0.0.0:$DATABRICKS_APP_PORT` under gunicorn with a graceful
timeout under the platform's 15-second SIGTERM budget and logs to stdout. Until
the Delta backend exists the store is a DuckDB file in `/tmp` (ephemeral);
the Delta backend on the same DDL is the first roadmap item
([`architecture/6_transition/`](./architecture/6_transition/README.md)).

## The model of this project

What this project knows about itself lives in
[`architecture/`](./architecture/README.md): why it exists, what information
it manages, which component does what, and where it is going. It is written
with [archreator](https://github.com/roanboc/archreator), an enterprise
architecture method that lives in git as Markdown, with humans approving at
gates and agents doing the modelling and the building in between.
[`AGENTS.md`](./AGENTS.md) states the rule every change follows.

The business case that started this and its review are held privately by the
product owner; [`architecture/reference/`](./architecture/reference/README.md)
says what was derived from them.

## Development

```bash
make check      # ruff, pytest, the two archreator validators — CI runs the same
make lint
make test
```

Layering: `models → metamodel → backend → services → importer / agent → ui`.
SQL only in `backend/`; framework and institution names only in `packs/` and
`connectors/`; the UI holds no logic the CLI does not also have.

## Licence

Apache-2.0 for the engine ([`LICENSE`](./LICENSE)). The higher-education pack
is a university's metamodel, anonymised and expressed as configuration; the
bundled icons are Tabler Icons (MIT) and the bundled diagram renderer is
Mermaid (MIT). See [`NOTICE`](./NOTICE).
