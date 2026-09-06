# Two gates, and views a reader can decode

_[← Scope index](./README.md) · [EA home](../README.md)_

**ArchiMate viewpoint:** Implementation & Migration.
**Delivered as:** branch `claude/archreator-validation-feedback-gt00b7`.

archreator moves to **0.3**: the Design gate is deleted, a gate that was not
granted no longer gets a row, and the optional open-questions log is retired
in favour of a call the agent takes and marks draft. This initiative applies
all three here, and fixes the two defects in this model that prompted the
method change — 273 node labels that carried a stereotype because nothing else
carried the type, and nine documents that put every diagram first and every
table after.

**No claim about the repository changes.** All 145 elements keep their
identifiers, their names and their status.

## EA alignment (assessed top-down before implementing)

| Layer | Impact |
| ----- | ------ |
| 1_strategy | No change of content. Both documents gain a legend and interleave their diagrams with their tables |
| 2_business | No change of content. `1_actors-and-roles.md` restructured; its status line no longer defers a deployment value to a retired question index |
| 3_information | No change of content. Two references to the retired log become the calls they were already recording |
| 4_application | No change of content. The component catalogue's status line drops the Design gate |
| 5_technology | No change of content. Legend added, diagrams interleaved |
| 6_transition | No change of content. Legend added, diagrams interleaved |

## What the diagrams looked like, and why

**Every content node carried its stereotype** — `⚇ «Business Actor» Product
owner [ACT1]` — because the glyph could not be trusted to say the type. In
this model `▤` meant Data Object, Business Object *and* Artifact; `◍` meant
Stakeholder, Business Actor *and* Business Role; `⚙` meant Business Process,
Business Service, Application Service *and* Technology Service. With three
types to a glyph, the stereotype was the only thing distinguishing them, and
so it could not be dropped.

**And no document had a legend.** The rule that lets a diagram drop its
stereotypes is that the document opens with a legend naming the types; with no
legend, the stereotype was doing the legend's job on every node, 273 times.

Both are fixed together, because neither can be fixed alone: every node now
takes the glyph the method's notation reference assigns its type, and every
element document opens with **How to read this document** — one diagram
declaring the types it uses, marked `%% legend` so the validator knows the
stereotypes on it are deliberate.

**Nine documents stacked all their diagrams before all their tables**, so a
reader met three pictures before the first row that named what was in them.
Each diagram now heads the section whose table it explains. Nothing was
reworded; the sections were reordered and merged.

## Work packages and deliverables

### WP1 — The glyphs distinguish, so the stereotypes can go

- **Deliverables:** 271 node labels across 15 documents relabelled from the
  method's notation reference; two `«Representation»` nodes, a type with no
  prefix in the registry, redrawn as the Artifacts they already are (`ART2`,
  `ART3`) borrowed into the information view.
- **Outcome:** a node reads `<glyph> <name> [<ID>]`, and the glyph is the type.

### WP2 — Every element document opens with its legend

- **Deliverables:** a **How to read this document** section in 14 documents,
  each declaring only the types that document draws.
- **Outcome:** a reader arriving at one document from a deep link has the
  notation in front of them.

### WP3 — A section opens with its own diagram

- **Deliverables:** `1_motivation.md`, `2_value-stream.md`,
  `1_actors-and-roles.md`, `2_processes-and-services.md`, `1_data-objects.md`,
  `1_application-services.md`, `2_application-components.md`, `1_runtime.md`
  and `1_target-state.md` reordered.
- **Outcome:** no document stacks its diagrams ahead of its prose.

### WP4 — Two gates, and no row for one that was not granted

- **Deliverables:** the front door's depth table, the scope index's step 3,
  and the component catalogue's status line.
- **Outcome:** the model names the gates that exist.

### WP5 — The open-questions log is retired

- **Deliverables:** `architecture/scope/open-questions.md` deleted; its index
  entry and three living references rewritten; five merged records and one
  merged decision repointed at this document, their words untouched.
- **Outcome:** what the log held is recorded where it applies. None of its five
  pending rows was a question this model needed answered — see below.

### WP6 — The validator is back in sync

- **Deliverables:** `scripts/check_model.py` taken from the 0.3 scaffold.
- **Outcome:** it now checks a diagram per **section** rather than per
  document, and fails a stereotype on a node outside a fence marked
  `%% legend`. The old copy checked neither, which is why both defects
  survived seven initiatives.

## What happened to the five open questions

| # | What it really was | Where it lives now |
| - | ------------------ | ------------------ |
| 5 | A question about a state that does not exist: source-of-record per type *once feeds exist*, for plateau `PLAT3` | Dropped. It is work nobody has scheduled, and the roadmap already carries the plateau |
| 12 | A call the agent made and shipped in initiative 4 — the two state vocabularies, fixed in the engine | Recorded where the states are defined, still `◐` |
| 13 | Already answered by the model: initiative 7 enforces who may merge (`ROLE1`, `ROLE2`) | Dropped. `1_actors-and-roles.md` answers it |
| 14 | A call the agent made and shipped in initiative 5 — which sources Propose accepts | Recorded in the Propose scope document, still `◐` |
| 15 | A deployment value, not a design question: which workspace groups map onto which role | Named in `1_actors-and-roles.md` as the owner's to supply |

None of the five changed what got built next, and none was answered by anyone
in the seven initiatives it sat open.

## Plateaus

| Plateau | State |
| ------- | ----- |
| **Baseline** (before) | Three gates; a row for every gate that did not apply; five questions nobody was going to answer; 273 nodes whose type only the stereotype carried; nine documents read picture-picture-picture-table-table-table |
| **Target** (delivered) | Two gates; a row only where something was granted; no open questions; a glyph that says the type and a legend that decodes it; each section opening with its own diagram |

## In scope / out of scope

| In scope | Out of scope (gaps, candidate future work) |
| -------- | ------------------------------------------- |
| The model's own documents, at method 0.3 | The pack's notation and the view generator — see the gap note |
| The validator back in sync with the scaffold | Any claim about the repository, its elements or its roadmap |
| The open-questions log retired | Rewriting a merged record. Not a word changes |

## Gap notes

- **The generated views still emit the shape this initiative removed.**
  `src/ea/views/model.py` writes a node as `glyph «Stereotype» Name`, and
  `packs/higher_education/metamodel.yaml` gives three types the glyph `▤`,
  two the glyph `⚙` and Application Component the glyph `▭`. That is the same
  defect as the hand-written documents had, in the product rather than in the
  model — and the same fix applies: give each type a distinguishing glyph in
  the pack, then the stereotype can leave the label. It is **not** done here:
  the generated-view convention is what
  [scope document 2](./2_generated-views.md) recorded as approved, so changing
  it is a change to documented behaviour and belongs to an initiative with its
  own **Understanding** gate.
- **`Representation` and `System Software` have no prefix** in the method's
  registry. The first was redrawn as an Artifact; the second is drawn as the
  Node specialisation ArchiMate makes it. If the model wants either as an
  element in its own right, the method needs a prefix for it.
- **The layer READMEs carry a Layer view whose inner nodes name no element.**
  They came from the plugin's asset templates, which had the same defect and
  were corrected upstream in the same change.

## Approvals

| Gate | Approved by | Date | What was approved |
| ---- | ----------- | ---- | ----------------- |
| | | | |

<!--
  Empty on purpose. This initiative changes no claim about the repository —
  every element keeps its identifier, name and status — so it reaches no gate,
  and under 0.3 a gate that was not granted gets no row.
-->
