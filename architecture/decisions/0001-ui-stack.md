# 0001 — Dash with Mantine components, AG Grid and Cytoscape for the app

_[← Decisions](./README.md)_

**Status:** Accepted, 2026-09-05. **Touches:** `ACMP6`.

## Context

The owner left the UI framework to the builder ("whatever is best, up to you
as the builder and maintainer"). The app must run on Databricks Apps later
(Python, one process, `0.0.0.0:$DATABRICKS_APP_PORT`, 2 vCPU and 6 GB), show
editable tables for the metamodel manager, render two kinds of graph (the type
graph and an element's neighbourhood), and be maintainable by an AI agent and a
small team. A reference-data management app the business case cites already
runs Dash with AG Grid on Databricks Apps.

## Decision

Dash 4 with dash-mantine-components for the shell and forms, dash-ag-grid for
every editable table, and dash-cytoscape for both graphs. Icons are bundled
SVGs (Tabler, MIT) rendered through a CSS mask, so no request leaves the
browser for an icon. One Dash callback per interaction; no client-side
framework.

## Alternatives

- **Streamlit** — fastest to write, but re-runs the whole script per
  interaction, has no editable grid of this quality and no graph component;
  the reference-data management app moved away from it for the same reasons.
- **React single-page app with a Python API** — best user experience and the
  right answer for a product; twice the code, two build chains, and a
  maintenance burden the PoC cannot justify.
- **Plotly graph for the networks** — no interaction model for tapping a node
  or re-laying out; Cytoscape is built for graphs.

## Consequences

- Graph layouts run in the browser; for the whole type graph of the institution's metamodel (about 60
  nodes) and neighbourhoods of a few dozen elements this is instant. Larger
  subgraphs must be capped server-side (`max_nodes`).
- Dash's dev reloader is off because DuckDB allows one writer per file; the
  dev server restarts by hand.
- Everything the app can do, the CLI can do too, so the UI never holds logic.
