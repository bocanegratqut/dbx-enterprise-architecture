from __future__ import annotations

from ea.ui import ids
from ea.ui.components import MARKDOWN_SNIPPETS, markdown, markdown_editor


def _walk(component):
    yield component
    children = getattr(component, "children", None)
    if children is None:
        return
    if not isinstance(children, list):
        children = [children]
    for child in children:
        if hasattr(child, "to_plotly_json"):
            yield from _walk(child)


def test_markdown_renders_mermaid_fences_as_diagrams():
    rendered = markdown("Intro\n\n```mermaid\nflowchart LR\n  A --> B\n```\n\nOutro", "test-md")
    classes = [getattr(c, "className", "") for c in _walk(rendered)]
    component_ids = [getattr(c, "id", None) for c in _walk(rendered)]

    assert "ea-mermaid-frame" in classes
    assert "ea-mermaid" in classes
    # The render callback declares the reset control as an Input; reader views must ship it too.
    assert {"type": "mermaid-reset", "id": "test-md-mermaid-0"} in component_ids


def test_markdown_editor_exposes_toolbar_textarea_and_preview_ids():
    editor = markdown_editor("sample", "Description (Markdown)", value="**hello**")
    component_ids = [getattr(c, "id", None) for c in _walk(editor)]

    assert editor.id == {"type": ids.MD_WRAP, "id": "sample"}
    assert "mode-edit" in editor.className
    assert {"type": ids.MD_TEXT, "id": "sample"} in component_ids
    assert {"type": ids.MD_PREVIEW, "id": "sample"} in component_ids
    assert {"type": ids.MD_MODE, "id": "sample"} in component_ids
    assert {"type": ids.MD_INSERT, "id": "sample", "kind": "heading"} in component_ids
    assert {"type": ids.MD_INSERT, "id": "sample", "kind": "bold"} in component_ids
    assert {"type": ids.MD_INSERT, "id": "sample", "kind": "table"} in component_ids
    assert {"type": ids.MD_INSERT, "id": "sample", "kind": "mermaid"} in component_ids


def test_markdown_snippets_cover_basic_authoring_actions():
    assert MARKDOWN_SNIPPETS["heading"].startswith("## ")
    assert "**" in MARKDOWN_SNIPPETS["bold"]
    assert "| Column |" in MARKDOWN_SNIPPETS["table"]
    assert MARKDOWN_SNIPPETS["mermaid"].startswith("```mermaid")
