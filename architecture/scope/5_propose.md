# Initiative 5 — Propose: from a document to a branch

_[← Scope index](./README.md) · [EA home](../README.md)_

**Requester:** the product owner. **Agent:** the coding agent in this
repository. **Reviewer:** the product owner. **Baseline:** initiative 4
(branches and states). **Target plateau:** `PLAT4` Governed change, the intake
side.

## Why

Architects produce solution designs as documents: a page with a description,
tables of components and their relationships, and diagrams. The owner wants a
**Propose** module, next to Ask, where an architect hands such a document (text,
uploaded files, links) to an agent. The agent creates a branch, works out which
of the document's elements already exist in the repository (and links to them)
and which are new (and adopts them as proposed), and writes the change to the
branch for review and merge. When the document does not identify or describe
its elements well enough, the agent pushes back and states the minimum it
needs. In the owner's organisation the document is usually a wiki page that an
agent will reach through a tool connector later; the module stays generic and
is tested locally with a Markdown template the architect can download.

## What changes

| Layer | Change |
| ----- | ------ |
| 1 Strategy | No new element; principle `P3` (agents draft, people approve) and `P6` (answers cite identifiers) govern the module |
| 3 Information | New object `DOBJ3.6` Proposal: the sources handed in, the change set the agent derived, the pushback, and the branch it went to |
| 4 Application | New service `ASVC9` Propose; new component `ACMP10` Proposal agent; `ACMP6` gains the Propose page; the Proposal Template as a downloadable document |
| Transition | New `GAP13` No proposal intake, closed by this initiative |

## Design

**One page, three inputs.** A large text box for pasted text, an upload for
Markdown, text and CSV files, and a list of links the app fetches (with a size
cap and a clear failure message when a link cannot be reached). A branch name
(a new branch is created from `main`), the work package the change belongs to
(an existing one, or a new one described in the document), and a Download
Proposal Template button.

**The Proposal Template** (`templates/proposal-template.md`) is a Markdown
document with a front section (title, work package, owner, summary, decisions),
an Elements table (type, name, existing identifier if known, description,
current state, target state), a Relationships table (source, relationship,
target, note), an optional Mermaid diagram, and an "Open points" section. It
is the shape the agent understands best and the shape the stub understands
completely, so the module works locally without a model key. It is written to
read well on its own, since architects will use it as their design page.

**The agent.** It reads the sources with the same tools Ask has (list types,
search, get element) and returns one structured result: the elements it
identified (each either **linked** to an existing identifier or **new**, with
type, name, description, current and target state), the relationships (both
ends resolved), and the **pushback**: what is missing. The app validates the
result against the metamodel (types, allowed relationship pairs, required
attributes) and shows it as a change-set preview: what will be linked, what
will be created, what could not be resolved. Nothing is written until the
architect clicks Apply to branch. The hosted provider reads free text and
tables alike; the stub provider parses the template's tables and matches names
against the repository, deterministically.

**The pushback rule.** A proposal is complete when every element has a type
the metamodel knows, a name, a description of at least one sentence, a current
and a target state, and every relationship names two resolvable ends with a
relationship type the metamodel allows between them; and the proposal names a
work package. Anything less is listed back to the architect as the minimum to
add, element by element, and nothing is applied.

**The architect stays in charge.** The change-set preview is an editable
merge log: every proposed element and relationship has an include tick, its
fields can be corrected in place, and rows can be added by hand for what the
agent missed or when no model is available. The same page therefore works
without an agent at all: paste nothing, add the rows, apply. What is not
ticked is not written.

**What Apply writes.** New elements as `proposed` with their target state
and the work package; linked elements untouched unless the proposal changes
their target state or note; relationships as declared; all on the branch.
The proposal itself (sources, derived change set, pushback, who and when) is
kept with the branch so the merger can read what the change came from.

## Work packages

| # | Work package | Delivers | Effort |
| - | ------------ | -------- | ------ |
| 1 | Template and parser | `templates/proposal-template.md`; the stub parser of its tables; name matching against the repository; validation against the metamodel; tests | about 1 day |
| 2 | Proposal agent | The structured result, the hosted provider's prompt and tools, the pushback rule, tests with the stub | about 1 day |
| 3 | Propose page | Inputs, template download, analysis, change-set preview, Apply to branch, link to the Branches page; the proposal kept with the branch | about 1 day |

## In scope

Text, Markdown, plain-text and CSV sources; links fetched over HTTP; the
template; the change set written to a branch. Every user may propose (roles are
documented, not enforced).

## Out of scope

PDF, Word and image sources (a later connector); wiki and document-system
connectors through a tool protocol (`PLAT5`); automatic merge; proposals that
change the metamodel; extraction of diagrams from images.

## Delivered

Built on 2026-09-06 on `main`: the Proposal Template; the parser of its tables (Markdown and CSV) and of pasted text; matching by identifier, exact name and near names (flagged, never linked silently); resolution of relationships against the metamodel; the pushback rule; the stub and hosted readers (the hosted one submits through a `submit_proposal` tool after reading the repository with the Ask tools); the Propose page with the editable merge log (include ticks, editable cells, rows added by hand, re-check) and Apply to branch (a new branch or an open one); the proposal kept with the branch; tests in `tests/test_proposal.py`.

## Approvals

| Gate | Decision | By | When | What was shown |
| ---- | -------- | -- | ---- | -------------- |
| Direction | Approved | The product owner | 2026-09-05, in the conversation | The request: a Propose module after Ask; documents, text and links in; a branch out; the agent links existing items and adopts new ones; pushback with the minimum needed; a downloadable template |
| Understanding | Approved with one addition | The product owner | 2026-09-05, in the conversation | This document, the Proposal Template draft and the pushback rule; the addition: the preview is an editable merge log with include ticks and manual rows, usable without the agent |
| Design | N/A — Depth 1; the design section above is the design | — | — | — |

## Open questions

Question 14 in [open-questions.md](./open-questions.md).
