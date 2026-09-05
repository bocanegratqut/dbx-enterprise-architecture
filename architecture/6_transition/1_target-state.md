# Target state

_[← Roadmap](./README.md) · [EA home](../README.md)_

**Status: `◐` draft catalogue** — the plateaus and gaps as the owner set them
on 2026-09-05 after the business-case review. Approved at the **Direction**
gate (recorded in [scope/1_curriculum-poc.md](../scope/1_curriculum-poc.md));
the gaps beyond `PLAT1` are intent, not work.

## Plateaus

| ID | Plateau | Status | What is true when it is reached |
| -- | ------- | ------ | ------------------------------- |
| `PLAT1` | **Local PoC on DuckDB** — the four deliverables (metamodel manager, element browse and edit, CSV ingestion, grounded agent) run on a DuckDB file with the higher-education pack and the curriculum export; extended by initiative 2 with generated architecture views and answer documents | In flight — initiatives 1 and 2 | The owner can show the app on the curriculum slice; the information architect has seen it |
| `PLAT2` | **Same application on Databricks** — the app runs on Databricks Apps, the store is a Unity Catalog schema of Delta tables, identity comes from the workspace | Planned | Same tests pass against a dev catalog; one deployment bundle |
| `PLAT3` | **Real content with provenance** — every type of the institution's metamodel is loaded, every type declares mirrored, authored or enriched semantics, and the mirrored ones are fed from their sources (the CMDB, the HR system, the project portfolio tool, the information asset register, the data platform's metadata catalogue) by scheduled jobs | Planned | A fact from the CMDB is never edited by hand in the repository; freshness is visible per source |
| `PLAT4` | **Governed change** — proposals are change sets with a base version, an impact assessment and a recorded approval; stewards and owners review in the app; sensitive attributes are granted by role | Planned | No approved status is written without a recorded human decision |
| `PLAT5` | **Semantic front doors** — a typed, commented projection with keys is generated from the metamodel into Unity Catalog; Business Definitions and Measures are published to the Unity Catalog business glossary and metric views; Genie-based agents over the projection, or whichever agent framework the platform offers, traverse the graph and answer in Markdown, with questions, answers and user feedback logged for monitoring and improvement; a tool server exposes the model to external agents | Planned | The three reference questions are answered through a Genie-based agent and through an external agent, with the same identifiers |
| `PLAT6` | **Current EA tool retired** — the repository is the system of record for authored types, the mirror for the rest, and the diagrams architects need are generated from it | Planned | The current tool's licence not renewed; retirement criteria agreed with the IT division's enterprise architecture team |

## Gaps

| ID | Gap | Between | Closed by |
| -- | --- | ------- | --------- |
| `GAP1` | **No Delta backend** — the store interface has one implementation | `PLAT1` and `PLAT2` | Initiative 3: `DatabricksBackend` on the same DDL, opt-in live tests |
| `GAP2` | **No deployment bundle** — `app.yaml` exists, the bundle, catalog, schema, warehouse and grants do not | `PLAT1` and `PLAT2` | Initiative 3 |
| `GAP3` | **No real institutional content** — the sample model stands in for the curriculum export | `PLAT1` and `PLAT3` | The current tool's export loaded through the export mapping (inside initiative 1 once the CSVs arrive) |
| `GAP4` | **No source feeds** — the current EA tool's export is the source of everything; nothing distinguishes a mirrored fact from an authored one yet | `PLAT1` and `PLAT3` | Initiative 4: per-type source-of-record semantics enforced, scheduled feeds |
| `GAP5` | **No change-set model** — edits are immediate, with optimistic concurrency and a change log but no proposal, review or approval | `PLAT1` and `PLAT4` | Initiative 5 |
| `GAP6` | **No projection, glossary or Genie-based agent** — the graph is generic tables only | `PLAT2` and `PLAT5` | Initiative 6: generated typed views with comments and keys, glossary publishing to Unity Catalog, Genie-based agents |
| `GAP7` | **No tool server for external agents** — the agent's tools are in-process | `PLAT2` and `PLAT5` | Initiative 6 |
| `GAP8` | **No retirement criteria for the current EA tool** — nobody has written down what must be true before the current tool goes | `PLAT5` and `PLAT6` | Agreed with the IT division's enterprise architecture team before initiative 7 |
| `GAP9` | **Views are graph layouts, not architecture diagrams** — neighbourhood, impact and agent answers show force-directed graphs; an answer has no picture | `PLAT1` as delivered by initiative 1 and `PLAT1` as extended | Initiative 2 (built 2026-09-05): a view model rendered to Mermaid in the archreator notation on the Element and Impact pages, answers composed into documents with views |
| `GAP10` | **No reusable diagram export** — an architect who wants to start a solution diagram from the model has nothing to open in a diagram tool | `PLAT1` and `PLAT1` as extended | Initiative 2 (built 2026-09-05): the same view exported as a draft draw.io file with ArchiMate stencils and an element identifier on every shape |
| `GAP11` | **No notation editor, hard-coded colours, fixed diagrams, graphs that overlap** — the metamodel's visual styles had no editor, the app's domain colours lived in code, generated diagrams could not be arranged, and the network graphs had no grouping | `PLAT1` as extended by initiative 2 and `PLAT1` as extended further | Initiative 3 (built 2026-09-05): Notation tab with live preview, colours in the pack, draggable views exported to draw.io, one graph panel with grouping and compound layouts; roles documented, none enforced by the owner's decision |

## Relationships

| From | | To | | Relationship | Note |
| ---- | - | -- | - | ------------ | ---- |
| `PLAT2` | ▭ «Plateau» Same application on Databricks | `PLAT1` | ▭ «Plateau» Local PoC on DuckDB | depends on | same code, second engine |
| `PLAT3` | ▭ «Plateau» Real content with provenance | `PLAT1` | ▭ «Plateau» Local PoC on DuckDB | depends on | the importer and the pack |
| `PLAT4` | ▭ «Plateau» Governed change | `PLAT2` | ▭ «Plateau» Same application on Databricks | depends on | workspace identity and grants |
| `PLAT5` | ▭ «Plateau» Semantic front doors | `PLAT2` | ▭ «Plateau» Same application on Databricks | depends on | Unity Catalog is where the projection lives |
| `PLAT5` | ▭ «Plateau» Semantic front doors | `PLAT3` | ▭ «Plateau» Real content with provenance | depends on | a projection of sample data sells nothing |
| `PLAT6` | ▭ «Plateau» Current EA tool retired | `PLAT4` | ▭ «Plateau» Governed change | depends on | authored types need governance before the current tool goes |
| `PLAT6` | ▭ «Plateau» Current EA tool retired | `PLAT5` | ▭ «Plateau» Semantic front doors | depends on | diagrams and glossary must come from somewhere |
