"""Dash application factory: shell, routing and page callbacks."""

from __future__ import annotations

import logging
from urllib.parse import unquote

import dash
import dash_cytoscape as cyto
import dash_mantine_components as dmc
from dash import MATCH, Input, Output

from ea.config import ROOT
from ea.ui import graph, ids, layout
from ea.ui.context import get_context
from ea.ui.pages import ask, browse, element, home, impact, import_page, metamodel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)

APP_TITLE = "EA Repository"


def parse_path(pathname: str | None) -> tuple[str, str | None]:
    parts = [unquote(p) for p in (pathname or "/").split("/") if p]
    if not parts:
        return "home", None
    if parts[0] == "element" and len(parts) >= 2:
        return "element", parts[1]
    if parts[0] in ("browse", "metamodel", "impact", "import", "ask"):
        return parts[0], None
    return "home", None


def create_app() -> dash.Dash:
    cyto.load_extra_layouts()  # cose-bilkent and friends for the graph panel
    ctx = get_context()
    app = dash.Dash(
        __name__,
        title=APP_TITLE,
        external_stylesheets=dmc.styles.ALL,
        suppress_callback_exceptions=True,
        assets_folder=str(ROOT / "assets"),
        update_title=None,
    )
    app.layout = layout.shell(APP_TITLE, ctx.registry.pack.name)

    @app.callback(Output(ids.PAGE, "children"), Input(ids.URL, "pathname"), Input(ids.URL, "search"))
    def route(pathname, search):
        ctx = get_context()
        page, arg = parse_path(pathname)
        try:
            if page == "element":
                return element.render(ctx, arg or "")
            if page == "browse":
                return browse.render(ctx, search)
            if page == "metamodel":
                return metamodel.render(ctx)
            if page == "impact":
                return impact.render(ctx, search)
            if page == "import":
                return import_page.render(ctx)
            if page == "ask":
                return ask.render(ctx)
            return home.render(ctx)
        except Exception as exc:  # noqa: BLE001 — a page error must not blank the shell
            log.exception("page %s failed", page)
            return dmc.Alert(f"{type(exc).__name__}: {exc}", color="red", title="This page failed to render")

    app.clientside_callback(
        """
        function(code, nReset) {
            const out = dash_clientside.callback_context.outputs_list;
            const target = JSON.stringify({id: out.id.id, type: 'mermaid-svg'});
            const posId = {id: out.id.id, type: 'mermaid-pos'};
            if (!window.eaViews) { return window.dash_clientside.no_update; }
            return window.eaViews.render(target, code || '', function (positions) {
                window.dash_clientside.set_props(posId, {data: positions});
            });
        }
        """,
        Output({"type": ids.MERMAID_POS, "id": MATCH}, "data"),
        Input({"type": ids.MERMAID_SRC, "id": MATCH}, "children"),
        Input({"type": ids.MERMAID_RESET, "id": MATCH}, "n_clicks"),
    )

    graph.register(app)
    for module in (browse, element, metamodel, impact, import_page, ask):
        module.register(app)
    return app
