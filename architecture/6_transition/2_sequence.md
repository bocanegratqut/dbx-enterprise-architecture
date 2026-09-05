# Sequence

_[← Roadmap](./README.md) · [Target state](./1_target-state.md)_

**Status: `◐` draft catalogue** — the order in which the gaps of
[1_target-state.md](./1_target-state.md) are closed. Approved at the
**Direction** gate with the target state; every step still enters the change
process and stops at its own Understanding before it is built.

| Step | Closes | Reaches | Has to be true first | Demo moment |
| ---- | ------ | ------- | -------------------- | ----------- |
| 1 — the PoC (weeks 1–4, initiative 1) | `GAP3` | `PLAT1` | The curriculum export from the current EA tool (elements and relationships as CSV) and the information architect's definition of "curriculum" | Browse and edit the curriculum slice; edit the metamodel live; ask the three reference questions with cited identifiers |
| 1b — generated views (initiative 2) | `GAP9`, `GAP10` | `PLAT1`, extended | Step 1's view queries and agent; the notation per type of the institution's metamodel (question 9, resolved: the default mapping stands) | Ask a question and get a document with an architecture diagram; download the same view as a draft draw.io file |
| 1c — administration and arrangeable views (initiative 3) | `GAP11` | `PLAT1`, extended | Step 1b | An admin edits a type's stereotype and colour and sees the preview change; an architect drags shapes on an impact view and opens the exported draw.io file arranged the same way |
| 2 — Databricks | `GAP1`, `GAP2` | `PLAT2` | A workspace with a SQL warehouse, a dev catalog and Apps enabled; a service principal | The same app on Databricks Apps, the same data in a Unity Catalog schema, the same tests green |
| 3 — provenance and feeds | `GAP4` | `PLAT3` | The per-type source-of-record table agreed with the IT division's enterprise architecture team (open question 5); read access to the extracts of the CMDB, the HR system, the project portfolio tool, the information asset register and the data platform's metadata catalogue (the last through its existing platform pipelines) | A CMDB change appears in the repository without anyone typing it |
| 4 — governed change | `GAP5` | `PLAT4` | Steward and owner roles named per type; the approval record format agreed | An architect proposes a change, sees its impact, a steward approves it, the change log shows both |
| 5 — semantic front doors | `GAP6`, `GAP7` | `PLAT5` | `PLAT2` and `PLAT3`; the glossary publishing target is Unity Catalog (question 6) | A Genie-based agent, or whichever agent framework the platform offers, traverses the projection and answers in Markdown, and an external agent answers the same question from the same projection; questions, answers and user feedback are logged |
| 6 — the current EA tool retired | `GAP8` | `PLAT6` | `PLAT4` and `PLAT5`; the retirement criteria met and the licence date known | The current tool read-only, then off |

Step 1b runs inside the PoC month. Steps 2 and 3 are independent of each other
and can run in either order or in parallel; both need step 1. Step 5 needs both. The PoC is allowed to be
thrown away at any step (principle `P7`); the plateaus are not.
