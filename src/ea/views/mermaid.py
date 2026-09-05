"""Render a view as Mermaid, in the notation the architecture documents of this repository use."""

from __future__ import annotations

import re

from ea.views.model import LAYER_TITLES, View, ViewNode

# archreator's colours per ArchiMate layer (architecture-document-style § ArchiMate on Mermaid).
LAYER_STYLE = {
    "motivation": ("#e6d6f5", "#7e57c2"),
    "strategy": ("#f5deaa", "#c8a24a"),
    "business": ("#fffbb5", "#b8a200"),
    "application": ("#c2f0ff", "#0288d1"),
    "technology": ("#c9e7b7", "#558b2f"),
    "physical": ("#c9e7b7", "#558b2f"),
    "implementation": ("#f8d7da", "#c0392b"),
    "other": ("#eeeeee", "#888888"),
}
# Mermaid node shapes by the pack's `shape` key.
SHAPES = {
    "rect": ('["', '"]'),
    "round": ('("', '")'),
    "stadium": ('(["', '"])'),
    "hex": ('{{"', '"}}'),
    "cyl": ('[("', '")]'),
    "subroutine": ('[["', '"]]'),
    "diamond": ('{"', '"}'),
    "asym": ('>"', '"]'),
}
_SAFE = re.compile(r"[^A-Za-z0-9_]")


def node_id(element_id: str) -> str:
    """A Mermaid-safe identifier for an element id (hyphens and dots are not safe everywhere)."""
    return "n_" + _SAFE.sub("_", element_id)


def _quote(text: str) -> str:
    return text.replace('"', "#quot;").replace("<", "#lt;").replace(">", "#gt;")


def _node_line(n: ViewNode) -> str:
    left, right = SHAPES.get(n.shape, SHAPES["rect"])
    text = _quote(f"{n.label} [{n.id}]")
    return f"{node_id(n.id)}{left}{text}{right}:::{n.layer if n.layer in LAYER_STYLE else 'other'}"


def to_mermaid(view: View, direction: str = "BT") -> str:
    """One subgraph per layer, motivation at the top and technology at the bottom, edges labelled with the relationship name.

    Drawn bottom-to-top: most relationships in an EA model point from the lower layers
    upwards (technology stores data, applications process it, roles own assets), so the
    layout's natural rank order agrees with the ArchiMate stacking instead of fighting it.
    """
    lines = [f"flowchart {direction}"]
    for layer in view.layers():
        lines.append(f'  subgraph {layer}["{LAYER_TITLES.get(layer, layer)}"]')
        for n in view.nodes_in(layer):
            lines.append("    " + _node_line(n))
        lines.append("  end")
    if view.edges:
        lines.append("")
    for e in view.edges:
        lines.append(f'  {node_id(e.src)} -->|"{_quote(e.label)}"| {node_id(e.dst)}')
    # Invisible links keep each layer above the next whatever direction the real relationships
    # point: one link per node of the lower layer towards the layer above (a source sits below
    # its target when drawn bottom-to-top), so the ordering outweighs the real edges in the
    # layout's rank assignment.
    layers = view.layers()
    if len(layers) > 1:
        lines.append("")
        for upper, lower in zip(layers, layers[1:], strict=False):
            anchor = view.nodes_in(upper)[0]
            for n in view.nodes_in(lower):
                lines.append(f"  {node_id(n.id)} ~~~ {node_id(anchor.id)}")
    lines.append("")
    for layer in view.layers():
        fill, stroke = LAYER_STYLE.get(layer, LAYER_STYLE["other"])
        lines.append(f"  classDef {layer} fill:{fill},stroke:{stroke},color:#333")
    for fid in view.focus_ids:
        lines.append(f"  style {node_id(fid)} stroke-width:3px")
    return "\n".join(lines) + "\n"


def to_markdown(view: View) -> str:
    """The view as a Markdown section: title, the fenced diagram, and the elements it shows."""
    out = [f"## {view.title}", ""]
    if view.note:
        out += [f"_{view.note}_", ""]
    out += ["```mermaid", to_mermaid(view).rstrip("\n"), "```", ""]
    out += ["| ID | Element | Type |", "| -- | ------- | ---- |"]
    for n in view.nodes:
        out.append(f"| `{n.id}` | {n.glyph} {n.name} | {n.stereotype or n.type_name} ({n.type_name}) |")
    out.append("")
    return "\n".join(out)
