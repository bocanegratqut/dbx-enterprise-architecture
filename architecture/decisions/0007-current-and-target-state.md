# 0007 — Current and target state as core fields, analysed by work package

_[← Decisions](./README.md)_

**Status:** Proposed, 2026-09-05 (accepted at the Understanding gate of initiative 4). **Touches:** `DOBJ2.1`, `DOBJ2.2`, `ASVC8`.

## Context

The owner wants the organisation to see current state against target state
per artefact, analysed by work package. The repository had a workflow status
(is the record trusted) and the source tool's free-text lifecycle, and no
target.

## Decision

Two small fixed vocabularies on every element and relationship: the current
state (`proposed`, `planned`, `in_implementation`, `live`, `retired`,
`non_existent`) and the target state (`undecided`, `keep`, `new`, `change`,
`decommission`, `merge`), plus the work package that carries the change and a
note. They are core fields of the engine, not pack attributes, because every
framework needs them and the views, the importer and the agent read them. The
work package type is found through the pack's notation (`archimate:
WorkPackage`), so no framework name enters the code. The unit of analysis is
the work package, not a dated plateau.

## Alternatives

- **Pack attributes** — flexible per framework, invisible to the engine; the
  target state page would then be framework-specific.
- **ArchiMate plateaus with dates** — the right long-term model for roadmaps;
  the owner asked for analysis by initiative first, and a plateau can be
  derived from work packages later.
- **A single lifecycle field** — cannot say "live today, decommission next
  year", which is the whole point.

## Consequences

- The importer derives the current state from lifecycle text on load; the
  derivation is a mapping in the connector, editable per tool.
- Generated views mark artefacts by target state; the same markers reach the
  draw.io export.
- The workflow status stays separate: a proposed element can have an approved
  record.
