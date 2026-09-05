"""Browse: list and search elements; create a new one."""

from __future__ import annotations

from urllib.parse import parse_qs

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import Input, Output, State, html, no_update

from ea.models import ValidationError
from ea.ui import ids
from ea.ui.components import alert, icon, page_title
from ea.ui.context import AppContext, get_context

COLUMNS = [
    {"field": "element_id", "headerName": "id", "width": 200},
    {"field": "name", "flex": 2},
    {"field": "type", "flex": 1},
    {"field": "status", "width": 110},
    {"field": "lifecycle_status", "headerName": "lifecycle", "width": 120},
    {"field": "source_system", "headerName": "source", "width": 120},
]


def _type_options(ctx: AppContext) -> list[dict[str, str]]:
    counts = ctx.backend.count_by_type()
    opts = [{"value": "", "label": "All types"}]
    for t in ctx.registry.pack.element_types:
        n = counts.get(t.id, 0)
        if t.active or n:
            opts.append({"value": t.id, "label": f"{t.name} ({n})"})
    return opts


def render(ctx: AppContext, search: str | None = None) -> html.Div:
    q = parse_qs((search or "").lstrip("?"))
    preset_type = (q.get("type") or [""])[0]
    return html.Div(
        [
            page_title(
                "Browse",
                "Search by name, id, key or description. Click a row to open the element.",
                dmc.Button("New element", id=ids.NEW_OPEN, leftSection=icon("tabler:plus"), variant="light"),
            ),
            dmc.Group(
                [
                    dmc.Select(
                        id=ids.BROWSE_TYPE,
                        data=_type_options(ctx),
                        value=preset_type,
                        w=320,
                        searchable=True,
                        clearable=False,
                    ),
                    dmc.TextInput(
                        id=ids.BROWSE_TEXT,
                        placeholder="Search…",
                        leftSection=icon("tabler:search"),
                        debounce=400,
                        w=320,
                    ),
                    dmc.Select(
                        id=ids.BROWSE_STATUS,
                        data=[{"value": "", "label": "Any status"}, "draft", "approved", "retired"],
                        value="",
                        w=150,
                    ),
                    dmc.Text(id=ids.BROWSE_COUNT, size="sm", c="dimmed"),
                ],
                gap="sm",
                mb="sm",
            ),
            dag.AgGrid(
                id=ids.BROWSE_GRID,
                columnDefs=COLUMNS,
                rowData=[],
                defaultColDef={"sortable": True, "filter": True, "resizable": True},
                dashGridOptions={
                    "rowSelection": "single",
                    "animateRows": False,
                    "pagination": True,
                    "paginationPageSize": 50,
                },
                className="ag-theme-alpine",
                style={"height": "70vh", "width": "100%"},
            ),
            dmc.Modal(
                id=ids.NEW_MODAL,
                title="New element",
                children=dmc.Stack(
                    [
                        dmc.Select(
                            id=ids.NEW_TYPE,
                            label="Type",
                            data=[{"value": t.id, "label": t.name} for t in ctx.registry.active_types()],
                            searchable=True,
                            required=True,
                        ),
                        dmc.TextInput(id=ids.NEW_NAME, label="Name", required=True),
                        dmc.Textarea(
                            id=ids.NEW_DESC, label="Description (Markdown)", autosize=True, minRows=3
                        ),
                        html.Div(id=ids.NEW_FEEDBACK),
                        dmc.Group([dmc.Button("Create", id=ids.NEW_SAVE)], justify="flex-end"),
                    ]
                ),
            ),
        ]
    )


def register(app: dash.Dash) -> None:
    @app.callback(
        Output(ids.BROWSE_GRID, "rowData"),
        Output(ids.BROWSE_COUNT, "children"),
        Input(ids.BROWSE_TYPE, "value"),
        Input(ids.BROWSE_TEXT, "value"),
        Input(ids.BROWSE_STATUS, "value"),
    )
    def load_rows(type_id, text, status):
        ctx = get_context()
        rows = ctx.repo.search(text or None, type_id or None, status or None, limit=ctx.settings.max_rows)
        total = ctx.backend.count_elements(type_id or None, text or None)
        data = [
            {
                "element_id": e.element_id,
                "name": e.name,
                "type": ctx.registry.types[e.type_id].name if e.type_id in ctx.registry.types else e.type_id,
                "status": e.status,
                "lifecycle_status": e.lifecycle_status,
                "source_system": e.source_system,
            }
            for e in rows
        ]
        return data, f"{len(data)} of {total}"

    @app.callback(
        Output(ids.URL, "pathname", allow_duplicate=True),
        Output(ids.URL, "search", allow_duplicate=True),
        Input(ids.BROWSE_GRID, "selectedRows"),
        prevent_initial_call=True,
    )
    def open_selected(rows):
        if not rows:
            return no_update, no_update
        return f"/element/{rows[0]['element_id']}", ""

    @app.callback(Output(ids.NEW_MODAL, "opened"), Input(ids.NEW_OPEN, "n_clicks"), prevent_initial_call=True)
    def open_modal(n):
        return bool(n)

    @app.callback(
        Output(ids.NEW_FEEDBACK, "children"),
        Output(ids.URL, "pathname", allow_duplicate=True),
        Output(ids.URL, "search", allow_duplicate=True),
        Input(ids.NEW_SAVE, "n_clicks"),
        State(ids.NEW_TYPE, "value"),
        State(ids.NEW_NAME, "value"),
        State(ids.NEW_DESC, "value"),
        prevent_initial_call=True,
        running=[(Output(ids.NEW_SAVE, "loading"), True, False)],
    )
    def create(n, type_id, name, desc):
        if not n:
            return no_update, no_update, no_update
        if not type_id or not (name or "").strip():
            return alert("Type and name are required.", "yellow"), no_update, no_update
        ctx = get_context()
        try:
            e = ctx.repo.create_element(type_id, name, ctx.actor, description_md=desc or "")
        except ValidationError as exc:
            return alert("; ".join(str(i) for i in exc.issues), "red"), no_update, no_update
        ctx.graph.invalidate()
        return no_update, f"/element/{e.element_id}", ""
