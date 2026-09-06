"""Target state: current versus intended state of every artefact, analysed per work package.

The pack says which element type plays the work package through its notation
(`archimate: WorkPackage`); nothing here names a type.
"""

from __future__ import annotations

from typing import Any

from ea.backend.base import DatabaseBackend
from ea.metamodel.registry import Registry
from ea.models import CURRENT_STATES, TARGET_STATES, Element, Relationship

# Colours and glyphs for the target states, shared by the badges, the Mermaid and the draw.io markers.
TARGET_STYLE: dict[str, dict[str, str]] = {
    "undecided": {"colour": "gray", "hex": "#868e96", "glyph": "?", "label": "Undecided"},
    "keep": {"colour": "blue", "hex": "#1c7ed6", "glyph": "=", "label": "Keep"},
    "new": {"colour": "green", "hex": "#2f9e44", "glyph": "+", "label": "New"},
    "change": {"colour": "orange", "hex": "#e8590c", "glyph": "Δ", "label": "Change"},
    "decommission": {"colour": "red", "hex": "#c92a2a", "glyph": "×", "label": "Decommission"},
    "merge": {"colour": "violet", "hex": "#7048e8", "glyph": "⇒", "label": "Merge"},
}
CURRENT_STYLE: dict[str, dict[str, str]] = {
    "proposed": {"colour": "grape", "label": "Proposed"},
    "planned": {"colour": "violet", "label": "Planned"},
    "in_implementation": {"colour": "yellow", "label": "In implementation"},
    "live": {"colour": "green", "label": "Live"},
    "retired": {"colour": "red", "label": "Retired"},
    "non_existent": {"colour": "gray", "label": "Non-existent"},
}
# Current states in which the artefact is not (yet, or any more) real: drawn dashed.
NOT_REAL = {"proposed", "planned", "in_implementation", "non_existent"}


def state_label(state: str, vocabulary: dict[str, dict[str, str]]) -> str:
    return vocabulary.get(state, {}).get("label") or state.replace("_", " ")


class TargetStateService:
    def __init__(self, backend: DatabaseBackend, registry: Registry):
        self.backend = backend
        self.registry = registry

    # ----------------------------------------------------- work packages
    def work_package_type(self) -> str | None:
        """The element type that plays the work package, from the pack's notation."""
        for t in self.registry.pack.element_types:
            if (t.notation or {}).get("archimate") == "WorkPackage":
                return t.id
        for t in self.registry.pack.element_types:
            if t.id == "work_package":
                return t.id
        return None

    def work_packages(self) -> list[Element]:
        wp_type = self.work_package_type()
        if not wp_type:
            return []
        return sorted(self.backend.find_elements(type_id=wp_type, limit=10_000), key=lambda e: e.name.lower())

    # ------------------------------------------------------------ queries
    def elements(self, work_package: str | None = None, only_changes: bool = False) -> list[Element]:
        rows = self.backend.find_elements(limit=1_000_000)
        if work_package:
            rows = [e for e in rows if e.target_work_package == work_package]
        if only_changes:
            rows = [e for e in rows if e.target_state not in ("undecided", "keep")]
        return sorted(rows, key=lambda e: (TARGET_STATES.index(e.target_state), e.type_id, e.name.lower()))

    def relationships(
        self, work_package: str | None = None, only_changes: bool = False
    ) -> list[Relationship]:
        rows = self.backend.find_relationships(limit=1_000_000)
        if work_package:
            rows = [r for r in rows if r.target_work_package == work_package]
        if only_changes:
            rows = [r for r in rows if r.target_state not in ("undecided", "keep")]
        return sorted(rows, key=lambda r: (TARGET_STATES.index(r.target_state), r.rel_type_id, r.src_id))

    def summary(self, work_package: str | None = None) -> dict[str, Any]:
        """Counts by target state, by current state, and the current-by-target matrix, for a work package or all."""
        els = self.elements(work_package)
        rels = self.relationships(work_package)
        by_target = {s: 0 for s in TARGET_STATES}
        by_current = {s: 0 for s in CURRENT_STATES}
        matrix = {c: {t: 0 for t in TARGET_STATES} for c in CURRENT_STATES}
        for e in els:
            by_target[e.target_state] += 1
            by_current[e.current_state] += 1
            matrix[e.current_state][e.target_state] += 1
        rel_by_target = {s: 0 for s in TARGET_STATES}
        for r in rels:
            rel_by_target[r.target_state] += 1
        return {
            "work_package": work_package or "",
            "elements": len(els),
            "relationships": len(rels),
            "by_target": by_target,
            "by_current": by_current,
            "matrix": matrix,
            "relationships_by_target": rel_by_target,
            "changes": sum(1 for e in els if e.target_state not in ("undecided", "keep")),
        }

    def scope_ids(self, work_package: str | None, max_nodes: int = 60) -> list[str]:
        """The elements a target-state view shows: the work package itself, then what it changes, then what it keeps."""
        els = self.elements(work_package)
        changing = [e.element_id for e in els if e.target_state not in ("undecided", "keep")]
        kept = [e.element_id for e in els if e.target_state in ("keep",)]
        undecided = [e.element_id for e in els if e.target_state == "undecided"] if work_package else []
        ids = ([work_package] if work_package else []) + changing + kept + undecided
        return ids[:max_nodes]
