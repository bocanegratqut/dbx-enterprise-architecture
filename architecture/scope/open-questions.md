# Open Questions

_[← Scope index](./README.md) · [EA home](../README.md)_

A living index of every adopted interpretation, across all scope documents,
that still needs confirmation from a stakeholder who could not be consulted
synchronously. Each row asks for one decision and states the expected
response.

## Pending

### 3 — Information

| # | Question | Adopted interpretation | Expected response | Raised in |
| - | -------- | ---------------------- | ----------------- | --------- |
| 5 | Which source-of-record per type applies once feeds exist? | The `source_of_record` values in the pack (the CMDB, the HR system, the project portfolio tool, the information asset register, the data platform's metadata catalogue, a higher-education reference model, the EA repository itself) as read from the institution's metamodel document | The IT division's enterprise architecture team confirms per type | Initiative 1, for plateau `PLAT3` |
| 12 | Are the two state vocabularies right? | Current: `proposed`, `planned`, `in_implementation`, `live`, `retired`, `non_existent`. Target: `undecided`, `keep`, `new`, `change`, `decommission`, `merge`. Fixed in the engine, on elements and relationships alike | Yes / No, or the words to change | Initiative 4 |

### 4 — Application

| # | Question | Adopted interpretation | Expected response | Raised in |
| - | -------- | ---------------------- | ----------------- | --------- |
| 13 | Who may merge a branch into `main`? | Every user in the PoC (roles documented, not enforced); the merger's name and the time are recorded; a second-person approval comes with enforced roles at plateau `PLAT4` | Yes / No | Initiative 4 |
| 14 | Which sources must Propose accept first? | Pasted text, Markdown, plain-text and CSV uploads, and links fetched over HTTP; PDF, Word and wiki connectors later | Yes / No, or the list | Initiative 5 |

## Resolved

An answered question moves here once the answer is applied to the model, with
the interpretation that was adopted while it was open beside the answer that
was accepted, so a reader can see where the model was built on a guess that
held and where it was corrected.

| # | Architecture layer | Question | Adopted interpretation | Accepted answer | Resolved in |
| - | ------------------ | -------- | ---------------------- | --------------- | ----------- |
| — | 1 — Strategy | Should the first delivery be a phased platform programme? | A phased programme with write-back to the current EA tool, freshness and steward workflows | A proof of concept on the curriculum domain, the current tool's content as source, no write-back; the programme stays on the roadmap | Initiative 1 (owner, 2026-09-05) |
| — | 1 — Strategy | Should the business case get a second version? | A "business case v2" written by the agent | One business case; the review lists the edits the owner makes to it | Initiative 1 (owner, 2026-09-05) |
| 1 | 1 — Strategy | Which elements count as "curriculum" for the PoC? | The Curriculum Logical Data Component, everything within two relationship hops of it, plus every type on the metamodel's Information diagram | Confirmed as adopted | Initiative 3 (owner, 2026-09-05) |
| 2 | 1 — Strategy | Where does the agent's model run for the demo? | Locally with an API key of a hosted model provider; on Databricks through the workspace's model serving later; without a key the stub provider runs the tools only | Locally with an API key of a hosted model provider; on Databricks a Genie-based agent, or whichever agent framework the platform offers, following Databricks good practice | Initiative 3 (owner, 2026-09-05) |
| 3 | 1 — Strategy | Is the first pack public in this repository or a private overlay? | Public, as the institution's configuration of a generic engine, with attribution in `NOTICE`; the reference model's content is never committed | Public and anonymous: the pack is `higher_education` and names no institution; the reference model's content stays uncommitted | Initiative 3 (owner, 2026-09-05) |
| 4 | 3 — Information | Does the current tool's relationship export carry source id, relationship name and target id on every row? | Yes; `connectors/tool-export/mapping.yaml` expects those three columns and a qualifier column for stewardship roles | Yes: the export carries source id, relationship name and target id | Initiative 3 (owner, 2026-09-05) |
| 6 | 3 — Information | Where is the business glossary published on Databricks? | Unity Catalog business glossary and metric views, generated from Business Definition and Measure elements; an external data catalogue stays possible | Unity Catalog is the target for the business glossary | Initiative 3 (owner, 2026-09-05) |
| 7 | 3 — Information | How are Attribute elements populated? | From schemas already in the data platform through platform pipelines, never typed by hand | Confirmed: from schemas already in the data platform, never typed by hand | Initiative 3 (owner, 2026-09-05) |
| 8 | 3 — Information | What retention applies to the change log on Databricks? | Kept indefinitely in the PoC; the university's records policy applies from plateau `PLAT2` | The change log is retained for 2 years | Initiative 3 (owner, 2026-09-05) |
| 9 | 3 — Information | Which ArchiMate stereotype and glyph draws each type of the metamodel? | A default mapping in the pack (`notation` per type): Data Entity and Logical Data Component as Data Object, Information Asset and Business Definition as Business Object, Measure as Value, Data Product as Product, Physical and Logical Application Component as Application Component, Physical and Logical Technology Component as Node and Technology Service, Integration as Flow, Interface as Application Interface, Process as Business Process, Role and Position as Business Role, Actor and Organization Unit as Business Actor, Capability, Work Package, Goal, Driver, Benefit as Outcome, Location, Value Stream, Business Service as their ArchiMate namesakes | The default mapping stands; changes are made in the Notation tab of the Metamodel page | Initiative 3 (owner, 2026-09-05) |
| 10 | 3 — Information | Are answer documents kept in the repository? | Not in the PoC: an answer document is rendered and downloadable; saving it as an element (an assessment attached to the elements it cites) is a plateau `PLAT4` concern | Not stored in the repository. On Databricks the preferred approach is Genie-based agents that know how to traverse the graph and answer in Markdown, with questions, answers and user feedback kept for monitoring and improvement | Initiative 3 (owner, 2026-09-05) |
| 11 | 2 — Business | Who is an admin, and where does the list live? | A configured list of usernames (`EA_ADMINS`) enforced in the PoC | No enforcement in the PoC: every user is an admin; roles documented in [3_admin-notation-and-arrangeable-views.md](./3_admin-notation-and-arrangeable-views.md) and carried by Databricks workspace groups at plateau `PLAT2` | Initiative 3 (owner, 2026-09-05) |
