# Reference documents

_[← EA home](../README.md) · [Scope documents](../scope/README.md)_

The material this model was built from, kept exactly as it was provided.

**This is not the model.** Nothing here defines an element or carries an
identifier, and the validators do not read it. Neither is it published: the
portal and the PDF hand a reader the model, not the room it came from.

## Naming

`YYYY-MM-DD-<short-description>.<ext>`, plain ASCII with hyphens. The date is,
in order of preference, when the meeting happened, when the document was
shared, or when it was added here; the index row says which.

**The original filename lives in the index, not on disk.**

## Founding documents

The documents this model was built from are held privately by the product
owner and are not in this public repository: the owner's business case for an
EA data platform (2026-09-05), the institution's metamodel document
(2026-08-11) and the review of the business case. What was derived from them
lives in the model:

- **The higher-education pack**
  ([`packs/higher_education/metamodel.yaml`](../../packs/higher_education/metamodel.yaml)):
  the metamodel document's 59 element types and 54 relationship types, with
  their provenance, source of record and diagram membership, anonymised.
- **The strategy layer** ([1_strategy/1_motivation.md](../1_strategy/1_motivation.md)):
  the stakeholders, drivers, assessments, goals and principles that the
  business case and its review argued for.
- **The roadmap** ([6_transition/1_target-state.md](../6_transition/1_target-state.md)):
  the plateaus and gaps the owner set after the review.

The four domain diagrams of the metamodel document (Information, Process,
Integration, Portfolio & Enterprise) are the source of the `diagrams:` tags in
the pack. The higher-education reference model the metamodel cites as the
source of many of its elements is licensed content and is **not** filed here;
an institution loads its own licensed copy.

## What does not belong here

| Not this | Where it goes |
| -------- | ------------- |
| A reading of what a document means | The layer document it informs, cited back here |
| A decision taken in a conversation | [`../decisions/`](../decisions/README.md), or a scope document |
| Anything with an element identifier | The model |
| Credentials, personal data, or anything shared in confidence that the model does not need | Nowhere in the repository |
