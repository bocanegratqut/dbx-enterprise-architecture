# 0008 — Roles derived from workspace groups, a debug persona locally, one permission function

_[← Decisions](./README.md)_

**Status:** Accepted 2026-09-06 (initiative 7). **Touches:** `ACMP12`, `ROLE1`–`ROLE5`, `BOBJ1`–`BOBJ3`.

## Context

The owner asked for the roles documented in initiative 3 to be enforced, with
a debug version in which a local user switches between roles, Admin by
default. On the platform the identity comes from Databricks Apps as forwarded
headers, and membership from workspace groups (question 11, resolved:
Databricks groups). Locally there is no identity provider.

## Decision

- **A role is a property of the request**, like the branch: derived once per
  request and held in a context variable. Five roles, cumulative from Reader:
  Reader, Reviewer, Architect, Admin, and Agent for the assistant.
- **From groups through configuration.** `EA_ROLE_GROUPS` maps a group name
  to each role; a user in none of them is a Reader. The mapping is
  configuration, never code, so the same build serves any workspace.
- **A debug persona locally.** With `EA_AUTH=mock` the header carries a
  persona switcher whose default is Admin; the choice lives in the session.
  It never exists on the platform: the switcher is rendered only under mock
  authentication, and the role derivation ignores the session there.
- **One permission function.** `allowed(user, action, context)` in the roles
  service is the only place that knows what a role may do. Every writing path
  calls it; the pages ask it to hide controls and the callbacks ask it again.
  A refusal is an exception that names the role and the action.
- **The agent's tools stay read-only** whatever the caller's role, so an
  admin asking the assistant gains nothing an architect would not.

## Consequences

- Roles are testable without a browser: set the role, call the service,
  expect the refusal.
- The command line takes `--as` (or `EA_ROLE`) for the same reason and with
  the same default, so a script runs as the role it should.
- Attribute-level grants (restricted attributes) are not roles; they wait for
  the platform's column grants (`PLAT2`, `PLAT4`).

## Alternatives not taken

- **A configured list of admin usernames** (`EA_ADMINS`, the interpretation
  offered in question 11): usernames drift; groups are what a workspace
  already administers.
- **Permissions on the store's tables:** the store is one file locally and
  one schema on the platform; row-level grants would not express "on a
  branch, not on main".
