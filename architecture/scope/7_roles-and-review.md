# Initiative 7 — Roles enforced, and review before merge

_[← Scope index](./README.md) · [EA home](../README.md)_

**Requester:** the product owner. **Agent:** the coding agent in this
repository. **Reviewer:** the product owner. **Baseline:** initiatives 1 to 6.
**Target plateau:** `PLAT4` Governed change, the roles and the review, on
DuckDB; the workspace identities come with `PLAT2`.

## Why

Two asks from the owner on 2026-09-06: "Implement now the roles and create a
debug version where we can switch between roles with the admin as default",
and "Review before merge: a second person approving a branch, with reviewers
per type, once roles are enforced." Until now every user was an admin
(question 11) and any author could merge their own branch (question 13). A
governed model needs both: a role that says who may write where, and a second
person's recorded decision before `main` moves.

## What changes

| Layer | Change |
| ----- | ------ |
| 1 Strategy | Principle `P3` (agents draft, people approve) gains its enforcement; stage `VS1.3` Review of the value stream is what this delivers |
| 2 Business | The business layer is written: actors `ACT1`–`ACT6`, roles `ROLE1`–`ROLE5` (Admin, Architect, Reviewer, Reader, Agent), business objects `BOBJ1`–`BOBJ3`, the governed change process `BPROC2` with its sub-processes, business services `BSVC1`–`BSVC3` |
| 3 Information | New object `DOBJ2.7` Review; the branch gains the statuses `in_review` and `approved` |
| 4 Application | New component `ACMP12` Roles and review; `ASVC7` gains request, approve, send back; every writing service checks the role; the header gains the debug persona switcher; the Branches page gains the review panel; the Metamodel page gains the Reviewers tab; `--as` on the command line |
| Transition | New `GAP14` No roles, no review before merge, closed by this initiative; `PLAT4` in flight |

## Design

**Roles.** Five roles, cumulative from Reader: Reader (browse, ask, analyse,
download), Reviewer (Reader plus approve or send back the types assigned to
them), Architect (Reader plus write on a branch, import onto a branch, propose,
request review, merge an approved branch), Admin (everything, including the
metamodel, `main`, reviewer assignments and merging without a review), and
Agent (what the assistant may do through tools: read, and draft what an
architect will tick). The role is a property of the request, like the branch:
on the platform it is derived from the identity headers and the workspace
groups through `EA_ROLE_GROUPS` (`admin=ea-admins;architect=ea-architects;reviewer=ea-reviewers`);
a user in no listed group is a Reader. Locally, with `EA_AUTH=mock`, the header
shows a **debug persona switcher** — Admin by default, any of the five roles a
click away — kept in the session next to the branch, so every path can be
walked without a workspace. `EA_ROLE` and `--as` do the same on the command
line.

**Enforcement.** One function, `allowed(user, action, context)`, in the roles
service, called by every writing path: the repository service (create, update,
relationships, bulk edit), the importer, the branch service (create, merge,
abandon), the proposal service (apply), the metamodel page (save, reload), and
the review service. The pages hide or disable what the role may not do and
the callbacks check again, so a stale page cannot write. A refusal names the
role and the action. The agent's tools remain read-only, whatever the role.

**Review before merge.** A branch moves `open → in_review → approved → merged`
(or back to `open` when sent back, or to `abandoned`). The author requests a
review; from then the branch is read-only until decided. The change set's
element types decide who must approve: the **reviewer assignments per type**
(a table an admin edits on the Metamodel page's Reviewers tab, seeded from
nothing) name, per element type, the users or groups that review it; a type
with no assignment may be approved by any Reviewer. A branch is approved when
every type it touches has an approval from one of that type's reviewers, none
of them the author; one "send back" with a comment returns it to `open`. The
merge asks the review service first: an architect merges only an approved
branch, an admin may merge at any time (recorded as such). Every decision is a
row in `branch_review` (who, which types, approve or send back, comment, when)
and a change-log entry with the branch as origin.

**How this fits the earlier initiatives.** Branch overlays, the merge log and
proposals are unchanged; review sits between the merge log and the merge. The
Propose page applies to a branch the architect may write to; an agent never
holds the pen.

## Work packages

| # | Work package | Delivers | Effort |
| - | ------------ | -------- | ------ |
| 1 | Roles | The role model, derivation from groups, the debug persona switcher, `--as`; `allowed()` and its use in every writing path; the pages hiding what the role may not do; tests | about 1 day |
| 2 | Review | Branch statuses, the review table and service, reviewer assignments per type with the Reviewers tab, the review panel on the Branches page, request, approve, send back, the merge gate; `ea branch review/approve`; tests | about 1 day |
| 3 | The business layer | `architecture/2_business/` with actors, roles, business objects, services and processes; the value stream in `1_strategy/`; the technology layer; views at the top of every layer document | about half a day |

## In scope

The five roles, the debug switcher, enforcement in the app and the command
line, the review with reviewers per type, the documents above.

## Out of scope

Row-level or attribute-level grants (restricted attributes stay visible to
every signed-in user until `PLAT2` brings grants); delegation and vacations;
review comments per row; notifications; enforcement inside the agent's
providers (the tools are read-only by construction).

## Delivered

Built on 2026-09-06 on `main`: the roles service (`src/ea/services/roles.py`)
with derivation from groups and the debug persona; the header switcher and
`--as`; `allowed()` called by every writing path with refusals named; the
review service (`src/ea/services/reviews.py`), the `branch_review` and
`reviewer_assignment` tables, the Reviewers tab on the Metamodel page, the
review panel on the Branches page, `ea branch review/approve`; the business and
technology layers and the value stream; tests in `tests/test_roles.py` and
`tests/test_reviews.py`.

## Approvals

| Gate | Decision | By | When | What was shown |
| ---- | -------- | -- | ---- | -------------- |
| Direction | Approved | The product owner | 2026-09-06, in the conversation ("Implement now the roles and create a debug version where we can switch between roles with the admin as default"; "Review before merge: a second person approving a branch, with reviewers per type, once roles are enforced") | The list of what was still missing after initiative 5 |
| Understanding | Approved by the same message | The product owner | 2026-09-06 | The roles as documented in initiative 3 and the review as sketched after initiative 5; this document records the design as built. The mapping of workspace groups onto roles stays open (question 15) |
| Design | N/A — Depth 1; the design section above is the design | — | — | — |
