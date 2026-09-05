# Project Scope Documents

_[← Repository README](../../README.md) · [Enterprise architecture](../README.md)_

One document per delivered (or in-flight) initiative, numbered
chronologically. While the [EA docs](../README.md) describe the
**current** state of the system, each scope document describes one
**change**: what plateau it started from, what it delivered, and what it
deliberately left out.

**ArchiMate viewpoint:** Implementation & Migration (Work Package,
Deliverable, Plateau, Gap).

## The EA-first change process

Every change in requirements follows the same order — the same order the EA
folders are numbered in:

1. **Align the EA first.** Walk the layers top-down and record what the
   change means for each: [1_strategy](../1_strategy/README.md) (does it
   serve an existing goal, or introduce a new driver?) → business (a `Gap`
   row on the front door today) → [3_information](../3_information/README.md)
   (new or changed data objects, flows, storage?) →
   [4_application](../4_application/README.md) (which services, components,
   interfaces change?) → technology (a `Gap` row today). Update the affected
   EA documents in the same change. If the change adds or modifies a
   stakeholder, driver, goal or principle, the initiative becomes strategy
   discovery first, ending at **Direction** approval; implementation follows
   as a separate initiative.
2. **Document the scope.** Add the next-numbered file to this folder
   describing plateaus, work packages, in and out of scope, gaps, and gate
   approvals — before implementation starts, refined as it proceeds.
3. **Pass the gates.** Before any code, the Requester approves the strategy
   and information changes (**Understanding**) and chooses whether to also
   review the solution design before it is coded (**Design**, optional).
   Approvals are recorded in the scope document's Approvals table — who
   approved, when, and what was shown, with `N/A — <why>` for a gate that
   could have applied and didn't. An approval can be granted in the
   conversation or in a reply on the pull request.
4. **Implement.** Only then write the code, keeping the scope document and
   EA docs in sync with what is actually delivered.

Adopted interpretations that still need a stakeholder's confirmation are
kept in [open-questions.md](./open-questions.md). Single consequential calls
smaller than an initiative are in [the decisions index](../decisions/README.md).

**A merged scope document is never rewritten**: it is the record of what was
approved on a date and against what information. When the current-state
documents drift from reality after a run of initiatives, restating them is
its own initiative with its own Understanding.

## Initiatives

| #   | Scope document | Delivered as | Summary |
| --- | --------------- | ------------ | ------- |
| 1   | [1_curriculum-poc.md](./1_curriculum-poc.md) | the working branch (in flight) | The PoC: generic metamodel-driven repository on DuckDB with the higher-education pack, CSV ingestion, browse and edit, metamodel manager and a grounded agent, on the curriculum slice of the institution's content |
| 2   | [2_generated-views.md](./2_generated-views.md) | the working branch (built, demo pending) | Generated architecture views in archreator-style Mermaid, agent answers as documents with diagrams, and a draft draw.io export over the same view model; no hand diagramming |
| 3   | [3_admin-notation-and-arrangeable-views.md](./3_admin-notation-and-arrangeable-views.md) | the working branch (built; demo pending) | Notation editor with live preview and domain colours as pack data; draggable shapes on generated views exported to draw.io without saving; the Ask page view-first with copyable Markdown; grouped, overlap-free graphs; roles documented, none enforced |
