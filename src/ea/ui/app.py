"""Dash application factory: shell, routing, the current branch, and page callbacks."""

from __future__ import annotations

import logging
import os
import secrets
from urllib.parse import unquote

import dash
import dash_cytoscape as cyto
import dash_mantine_components as dmc
from dash import MATCH, Input, Output, State, no_update
from flask import session

from ea.backend.branching import MAIN, set_branch
from ea.config import ROOT
from ea.models import ConflictError, NotFoundError
from ea.ui import graph, ids, layout
from ea.ui.components import alert
from ea.ui.context import get_context
from ea.ui.pages import ask, branches, browse, element, home, impact, import_page, metamodel, propose, target

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)

APP_TITLE = "EA Repository"
PAGES = {"browse", "metamodel", "impact", "import", "ask", "branches", "target", "propose"}


def parse_path(pathname: str | None) -> tuple[str, str | None]:
    parts = [unquote(p) for p in (pathname or "/").split("/") if p]
    if not parts:
        return "home", None
    if parts[0] == "element" and len(parts) >= 2:
        return "element", parts[1]
    if parts[0] in PAGES:
        return parts[0], None
    return "home", None


def session_branch() -> str:
    """The branch kept in the reader's session; main when none or when the branch is gone."""
    try:
        return session.get("branch") or MAIN
    except RuntimeError:  # outside a request
        return MAIN


def create_app() -> dash.Dash:
    cyto.load_extra_layouts()  # cose-bilkent and friends for the graph panel
    get_context()  # open the store and load the pack before the first request
    app = dash.Dash(
        __name__,
        title=APP_TITLE,
        external_stylesheets=dmc.styles.ALL,
        suppress_callback_exceptions=True,
        assets_folder=str(ROOT / "assets"),
        update_title=None,
    )
    # The branch a reader is on lives in a signed session cookie. Set EA_SECRET_KEY so sessions
    # survive a restart; without it every restart puts everybody back on main.
    app.server.secret_key = os.environ.get("EA_SECRET_KEY") or secrets.token_hex(32)

    @app.server.before_request
    def _branch_from_session() -> None:
        branch = session_branch()
        if branch != MAIN and get_context().backend.get_branch(branch) is None:
            branch = MAIN
        set_branch(branch)

    def _shell():
        ctx = get_context()
        current = ctx.branch()
        b = ctx.backend.get_branch(current) if current != MAIN else None
        if b is not None and b.status != "open":
            current = MAIN
        return layout.shell(
            APP_TITLE,
            ctx.registry.pack.name,
            ctx.branch_options(),
            current,
            b.changes if b is not None else None,
            ctx.work_package_options(),
        )

    app.layout = _shell  # a function: the header reflects the session's branch on every page load

    @app.callback(
        Output(ids.PAGE, "children"),
        Input(ids.URL, "pathname"),
        Input(ids.URL, "search"),
        Input(ids.NAV_VERSION, "data"),
    )
    def route(pathname, search, _version):
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
            if page == "branches":
                return branches.render(ctx, search)
            if page == "target":
                return target.render(ctx, search)
            if page == "propose":
                return propose.render(ctx)
            return home.render(ctx)
        except Exception as exc:  # noqa: BLE001 — a page error must not blank the shell
            log.exception("page %s failed", page)
            return dmc.Alert(f"{type(exc).__name__}: {exc}", color="red", title="This page failed to render")

    # ---------------------------------------------------------------- branch
    @app.callback(
        Output(ids.NAV_VERSION, "data"),
        Output(ids.BRANCH_BADGE, "children"),
        Input(ids.BRANCH_SELECT, "value"),
        State(ids.NAV_VERSION, "data"),
    )
    def switch_branch(value, version):
        """Keep the chosen branch in the session and re-render the page on it."""
        ctx = get_context()
        chosen = value or MAIN
        if chosen != MAIN and ctx.backend.get_branch(chosen) is None:
            chosen = MAIN
        changed = chosen != session_branch()
        session["branch"] = chosen
        set_branch(chosen)
        b = ctx.backend.get_branch(chosen) if chosen != MAIN else None
        badge = layout.branch_badge(chosen, b.changes if b else None)
        return (int(version or 0) + 1 if changed else no_update), badge

    @app.callback(
        Output(ids.BRANCH_NEW_MODAL, "opened"),
        Input(ids.BRANCH_NEW_OPEN, "n_clicks"),
        prevent_initial_call=True,
    )
    def open_new_branch(n):
        return bool(n)

    @app.callback(
        Output(ids.BRANCH_NEW_FEEDBACK, "children"),
        Output(ids.BRANCH_NEW_MODAL, "opened", allow_duplicate=True),
        Output(ids.BRANCH_SELECT, "data"),
        Output(ids.BRANCH_SELECT, "value"),
        Input(ids.BRANCH_NEW_SAVE, "n_clicks"),
        State(ids.BRANCH_NEW_NAME, "value"),
        State(ids.BRANCH_NEW_DESC, "value"),
        State(ids.BRANCH_NEW_WP, "value"),
        prevent_initial_call=True,
        running=[(Output(ids.BRANCH_NEW_SAVE, "loading"), True, False)],
    )
    def create_branch(n, name, desc, wp):
        if not n:
            return no_update, no_update, no_update, no_update
        ctx = get_context()
        if not (name or "").strip():
            return alert("A branch needs a name.", "yellow"), no_update, no_update, no_update
        try:
            b = ctx.branches.create(name.strip(), ctx.actor, desc or "", wp or "")
        except (ConflictError, NotFoundError, ValueError) as exc:
            return alert(str(exc), "red"), no_update, no_update, no_update
        return None, False, ctx.branch_options(), b.branch_id

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
    for module in (browse, element, metamodel, impact, import_page, ask, branches, target, propose):
        module.register(app)
    return app
