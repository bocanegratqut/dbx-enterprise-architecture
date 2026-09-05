# Roadmap

_[← EA home](../README.md) · [Scope documents](../scope/README.md)_

**ArchiMate viewpoint:** Implementation & Migration (Plateau, Gap).

Where this architecture is going, what stands between it and today, and the
order the distance is closed in.

This folder is **the only place in the model permitted to describe a future.**
Every numbered layer describes the current state and is kept that way; scope
documents describe one delivered change each. Neither can hold an intention
without becoming untrustworthy — a target element sitting in a current-state
layer makes the whole layer ambiguous, and a plan spread across scope
documents is a plan nobody can read in one place.

Agent guidance: the `plan-the-transition` skill.

## Analysis order

| #   | Document | Elements | Question it answers |
| --- | -------- | -------- | ------------------- |
| 1   | [1_target-state.md](./1_target-state.md) | Plateaus, Gaps | Where should this be, and what is missing between here and there? |
| 2   | [2_sequence.md](./2_sequence.md) | — | In what order are the gaps closed, and what has to be true first? |

The order is not arbitrary. A gap is the distance between the baseline and a
named plateau, so the plateaus have to exist before a gap can be derived
rather than asserted — and the sequence is an ordering of gaps, so it comes
last.

## What is approved here, and what is not

**Direction** approves this folder: that the destination is right and the order
is right. It is the same gate the strategy layer passes, because both are the
Requester approving a direction.

**It approves no work.** Every initiative on the sequence still enters
`align-change-through-layers`, still aligns through the numbered layers, and
still stops at its own Understanding before anything is built. A roadmap treated as
pre-approval for the changes on it has quietly removed every gate the method
has.

## Status vocabulary

A plateau and a gap each carry a status, and the vocabulary is short on
purpose.

| Status | Means |
| ------ | ----- |
| **Planned** | Named and approved as intent. Nothing is in flight |
| **In flight** | An initiative is open against it. Its scope document names the gaps it closes |
| **Reached** | The state is true today. The row stays, naming the initiative that arrived at it |
| **Abandoned** | No longer the intent. The row stays, with why |

**Nothing here is deleted when it stops being the plan.** A reached plateau
that is removed leaves no evidence the direction was ever chosen, and an
abandoned one that is removed invites somebody to propose it again in two
years. What is retired from a *numbered layer* follows the model's ordinary
Retired convention; what is finished or dropped here changes status instead,
because a roadmap is a record of direction over time rather than a description
of now.

## Keeping it current

A roadmap nobody revisits is worse than none, because it is trusted. Two
moments update it, and both belong to initiatives that are happening anyway:
an initiative opening marks what it is closing as in flight, and an initiative
merging marks what it closed. Where a plateau turns out to be wrong, that is
its own initiative through the skill, not a quiet edit.

## Notation

Glyph, shape and colour follow
the `architecture-document-style` rulebook § ArchiMate on Mermaid,
which stays the single source. Both element types take the Implementation &
Migration rose, ramped from plateau to gap.

**Edges here are solid, and that is not an exception to the notation.** A
dashed edge means the *relationship* is pending — and the dependency between
two plateaus is true today whether or not either is reached: the later one
needs the earlier one now, and will still need it after both arrive. What is
not reached yet is a plateau's own **Status**, which its row carries in words.
Drawing that on the edge would state it twice and state it wrongly.
