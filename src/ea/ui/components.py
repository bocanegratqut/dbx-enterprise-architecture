"""Small presentational helpers shared by the pages."""

from __future__ import annotations

import base64
import json
from functools import cache
from pathlib import Path
from typing import Any

import dash_mantine_components as dmc
from dash import dcc, html

from ea.metamodel.registry import Registry
from ea.models import Element, Issue

# Colours come from the pack (a domain's `notation.colour` and `notation.hex`); these are the fallbacks.
FALLBACK_COLOUR, FALLBACK_HEX = "gray", "#adb5bd"
STATUS_COLORS = {"draft": "orange", "approved": "green", "retired": "red"}
LEVEL_COLORS = {"error": "red", "warning": "yellow", "info": "blue"}


ICON_DIR = Path(__file__).resolve().parents[3] / "assets" / "icons"


@cache
def _icon_data_uri(name: str) -> str | None:
    """Tabler outline icon (MIT) shipped with the app, so no request ever leaves the browser for an icon."""
    path = ICON_DIR / f"{name.split(':', 1)[-1]}.svg"
    if not path.is_file():
        return None
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def icon(name: str, size: int = 16, **kwargs: Any) -> html.Span:
    """An inline icon that takes the text colour of its parent (CSS mask over the SVG)."""
    uri = _icon_data_uri(name)
    style = {
        "display": "inline-block",
        "width": f"{size}px",
        "height": f"{size}px",
        "verticalAlign": "middle",
    }
    if uri:
        style.update(
            {
                "backgroundColor": "currentColor",
                "WebkitMaskImage": f"url({uri})",
                "maskImage": f"url({uri})",
                "WebkitMaskSize": "contain",
                "maskSize": "contain",
                "WebkitMaskRepeat": "no-repeat",
                "maskRepeat": "no-repeat",
            }
        )
    style.update(kwargs.pop("style", {}) or {})
    return html.Span(style=style, className="ea-icon", **kwargs)


def element_href(element_id: str) -> str:
    return f"/element/{element_id}"


def domain_colour(registry: Registry, domain_id: str) -> str:
    """The palette name a domain declares in its notation, for badges and legends."""
    d = next((d for d in registry.pack.domains if d.id == domain_id), None)
    return (d.notation.get("colour") if d else None) or FALLBACK_COLOUR


def domain_hex(registry: Registry, domain_id: str) -> str:
    """The fill colour a domain declares in its notation, for graphs."""
    d = next((d for d in registry.pack.domains if d.id == domain_id), None)
    return (d.notation.get("hex") if d else None) or FALLBACK_HEX


def darken(hex_colour: str, amount: float = 0.3) -> str:
    """A darker shade of a hex colour, for borders."""
    h = hex_colour.lstrip("#")
    if len(h) != 6:
        return "#495057"
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    f = 1 - amount
    return f"#{int(r * f):02x}{int(g * f):02x}{int(b * f):02x}"


def type_color(registry: Registry, type_id: str) -> str:
    t = registry.get_type(type_id)
    return domain_colour(registry, t.domain if t else "")


def type_badge(registry: Registry, type_id: str, size: str = "sm") -> dmc.Badge:
    t = registry.get_type(type_id)
    return dmc.Badge(
        t.name if t else type_id, color=type_color(registry, type_id), variant="light", size=size
    )


def status_badge(status: str, size: str = "sm") -> dmc.Badge:
    return dmc.Badge(status, color=STATUS_COLORS.get(status, "gray"), variant="outline", size=size)


def element_anchor(e: Element | dict[str, Any]) -> dmc.Anchor:
    eid = e.element_id if isinstance(e, Element) else e["element_id"]
    name = e.name if isinstance(e, Element) else e["name"]
    return dmc.Anchor(name, href=element_href(eid), size="sm", fw=500)


def markdown(text: str) -> dcc.Markdown:
    return dcc.Markdown(text or "_No description._", link_target="_blank", style={"lineHeight": 1.5})


def kv_table(rows: list[tuple[str, Any]]) -> dmc.Table:
    return dmc.Table(
        [
            dmc.TableTbody(
                [
                    dmc.TableTr(
                        [
                            dmc.TableTd(dmc.Text(k, size="sm", c="dimmed")),
                            dmc.TableTd(v if _is_component(v) else dmc.Text(_fmt(v), size="sm")),
                        ]
                    )
                    for k, v in rows
                ]
            )
        ],
        withRowBorders=False,
        verticalSpacing="xs",
    )


def _is_component(v: Any) -> bool:
    return hasattr(v, "to_plotly_json")


def _fmt(v: Any) -> str:
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return "" if v is None else str(v)


def simple_table(headers: list[str], rows: list[list[Any]], striped: bool = True) -> dmc.Table:
    return dmc.Table(
        [
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h) for h in headers])),
            dmc.TableTbody(
                [
                    dmc.TableTr(
                        [dmc.TableTd(c if not isinstance(c, (str, int, float)) else _fmt(c)) for c in r]
                    )
                    for r in rows
                ]
            ),
        ],
        striped=striped,
        highlightOnHover=True,
        withTableBorder=True,
        verticalSpacing="xs",
        fz="sm",
    )


def issues_table(issues: list[Issue]) -> Any:
    if not issues:
        return dmc.Alert("No issues.", color="green", variant="light")
    rows = [
        [
            dmc.Badge(i.level, color=LEVEL_COLORS.get(i.level, "gray"), size="xs"),
            i.code,
            i.message,
            i.file or "",
            i.row or "",
            i.entity or "",
        ]
        for i in issues
    ]
    return simple_table(["level", "code", "message", "file", "row", "entity"], rows)


def alert(message: str, color: str = "blue") -> dmc.Alert:
    return dmc.Alert(message, color=color, variant="light", withCloseButton=True)


def error_alert(exc: Exception) -> dmc.Alert:
    return alert(str(exc), "red")


def page_title(title: str, subtitle: str | None = None, right: Any = None) -> dmc.Group:
    left = dmc.Stack(
        [dmc.Title(title, order=2), dmc.Text(subtitle, c="dimmed", size="sm") if subtitle else None], gap=2
    )
    return dmc.Group(
        [left, right] if right is not None else [left], justify="space-between", align="flex-start", mb="md"
    )


def empty(text: str) -> html.Div:
    return html.Div(dmc.Text(text, c="dimmed", size="sm"), style={"padding": "1rem 0"})


def mermaid_block(block_id: str, code: str, arrangeable: bool = True) -> html.Div:
    """A generated diagram: the Mermaid source (hidden), the rendered SVG, and, when arrangeable,
    a store of the shape positions that the draw.io export honours and a button to reset them."""
    children: list[Any] = [
        html.Pre(code, id={"type": "mermaid-src", "id": block_id}, hidden=True),
        dcc.Store(id={"type": "mermaid-pos", "id": block_id}, data=None),
        html.Div(id={"type": "mermaid-svg", "id": block_id}, className="ea-mermaid"),
    ]
    if arrangeable:
        children.append(
            dmc.Group(
                [
                    dmc.Text(
                        "Drag a shape to arrange the view; the draw.io export follows. Nothing is saved.",
                        size="xs",
                        c="dimmed",
                    ),
                    dmc.Button(
                        "Reset layout",
                        id={"type": "mermaid-reset", "id": block_id},
                        size="compact-xs",
                        variant="subtle",
                        color="gray",
                        leftSection=icon("tabler:refresh", 12),
                    ),
                ],
                gap="sm",
                mt=4,
            )
        )
    return html.Div(children)


def view_toolbar(
    md_id: str,
    drawio_id: str,
    note: str = "",
    copy_content: str | None = None,
    extra: list[Any] | None = None,
) -> dmc.Group:
    """Download (and optionally copy) buttons under a generated view or document."""
    items: list[Any] = []
    if copy_content is not None:
        items.append(
            dmc.Tooltip(
                dmc.Group(
                    [
                        dcc.Clipboard(content=copy_content, title="Copy Markdown", className="ea-clipboard"),
                        dmc.Text("Copy Markdown", size="xs", fw=500),
                    ],
                    gap=4,
                    className="ea-copy",
                ),
                label="Copy the whole document as Markdown",
            )
        )
    items += [
        dmc.Button(
            "Download Markdown", id=md_id, size="xs", variant="light", leftSection=icon("tabler:download", 14)
        ),
        dmc.Button(
            "Download draw.io",
            id=drawio_id,
            size="xs",
            variant="light",
            leftSection=icon("tabler:download", 14),
        ),
        *(extra or []),
    ]
    if note:
        items.append(dmc.Text(note, size="xs", c="dimmed"))
    return dmc.Group(items, gap="sm", mt="xs", align="center")
