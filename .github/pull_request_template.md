<!--
  PR TEMPLATE LAYOUT — GitHub fills a PR body from ONE default template, and
  this is it. Every kind of change fills the same body: an initiative names
  its scope document, a pure bug fix says "no scope document" and names what
  broke instead. How to fill it in: the `write-pr-description` skill.
-->
<!--
  Describe the WHOLE branch, not just the latest commit:
    git log --oneline main..HEAD
    git diff main...HEAD --stat
  Keep this body updated as the branch gains commits — a body that was true at
  the first push and stale at the fifth reads as current and is not.
-->

## Summary

<!-- Two to four sentences: what this branch delivers, and why. -->

## Scope document

<!-- Link the initiative's document in architecture/scope/. Its Approvals
     table must already record the gates the change required — Understanding at
     minimum for anything that changes documented behavior.

     A pure bug fix has no scope document. Write "No scope document" and say
     what broke, the root cause, and the fix. -->

## EA layers touched

<!-- Copied from the scope document's alignment table. EVERY layer gets a
     verdict, including an explicit "no change" — silence is not a decision.
     Delete the rows for layers this project does not use, and say so in the
     row rather than dropping it silently. -->

| Layer | Verdict |
| ----- | ------- |
| 0_business-design | |
| 1_strategy | |
| 2_business | |
| 3_information | |
| 4_application | |
| 5_technology | |

## Changes

<!-- Grouped by work package or area, covering the full main...HEAD diff. If
     a changed file is not explainable here, it either needs a mention or does
     not belong on the branch. -->

## Complexity

<!-- What was removed? What new recurring cost does this add — a document to
     keep true, a check to keep green, a copy to hold together — and why is
     it justified? "Nothing removed, nothing recurring added" is a complete
     answer. -->

## Verification

<!-- The commands that were run and what they said, plus anything checked by
     hand. Both validators must be green:

     python3 scripts/check_links.py
     python3 scripts/check_model.py
-->

## Out of scope / follow-ups

<!-- The scope document's gap notes, mirrored: what was deliberately left
     out, and what closing it would take. -->
