# 0003 — The metamodel is a data pack, and typed tables are a generated projection

_[← Decisions](./README.md)_

**Status:** Accepted, 2026-09-05. **Touches:** `ACMP1`, `DOBJ1`.

## Context

The business case asked for a Unity Catalog schema that "strictly maps" to
the institution's active types. The institution's metamodel has 27 active
types, 32 inactive ones that still have instances in the export, relationship
types targeting any element, a stewardship relationship qualified by role, and
it changes (its document is dated 2026-08-11 and supersedes an earlier
version). The owner wants the solution generic for any framework, with the
institution's metamodel as the first configuration.

## Decision

The metamodel is data: a YAML pack (`packs/<framework>/metamodel.yaml`) with
element types (supertypes, active flags, attributes, provenance, source of
record, owners), relationship types (source and target or `ANY`, inverse,
qualifiers, provenance) and domains. The pack loads into `meta_*` tables, the
app edits those tables and exports the pack back. Validation rules derive from
the registry, never from code. Typed, commented tables with keys for Genie,
ERDs and grants are a projection generated from the pack (plateau `PLAT5`),
never the primary store.

## Alternatives

- **DDL per type** — the business case's reading; every metamodel change is a
  migration, and nothing else can adopt the engine.
- **A single untyped triple store** — maximally generic, but loses attributes,
  validation and the ability to generate a readable projection.

## Consequences

- Adding a type or an attribute is a row, not a release.
- Framework names live only in packs and mappings; the code is checked for
  that (principle `P5`).
- The higher-education pack is the institution's configuration and intellectual
  work, credited in `NOTICE`; the content of the higher-education reference model
  it references is licensed and never committed.
