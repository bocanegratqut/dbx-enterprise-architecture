# Decisions

_[← Repository README](../../README.md) · [Enterprise architecture](../README.md)_

One file per decision, numbered chronologically, each explaining a single
call that is smaller than an initiative (see [scope/](../scope/README.md))
but consequential enough that a future reader will ask "why this and not the
alternative?".

## Index

| #   | Decision | Status | Touches |
| --- | -------- | ------ | ------- |
| [0001](./0001-ui-stack.md) | Dash with Mantine components, AG Grid and Cytoscape for the app | Accepted 2026-09-05 | `ACMP6` |
| [0002](./0002-store-and-engines.md) | A generic graph schema on DuckDB now and Delta later, with in-process traversal | Accepted 2026-09-05 | `ACMP2`, `ACMP3`, `DOBJ2` |
| [0003](./0003-metamodel-as-data.md) | The metamodel is a data pack, and typed tables are a generated projection | Accepted 2026-09-05 | `ACMP1`, `DOBJ1` |
| [0004](./0004-agent-grounding.md) | The agent only drafts, only uses tools, and every identifier it cites is checked | Accepted 2026-09-05 | `ACMP5` |
| [0005](./0005-generated-views.md) | Generated views, not a diagram editor | Accepted 2026-09-05 | `ACMP8`, `ASVC6`, `P8` |
