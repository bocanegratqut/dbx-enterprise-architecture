"""Command line: initialise, load packs, import CSVs, ask graph questions, work on branches."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from ea.backend.branching import MAIN, set_branch
from ea.config import Settings

app = typer.Typer(
    help="EA repository — a generic, metamodel-driven enterprise architecture repository.",
    no_args_is_help=True,
)
branch_app = typer.Typer(
    help="Branches of the model: create, diff, merge item by item, abandon.", no_args_is_help=True
)
app.add_typer(branch_app, name="branch")


@app.callback()
def main(
    branch: str = typer.Option(
        None,
        "--branch",
        "-b",
        envvar="EA_BRANCH",
        help="Work on this branch instead of main (every read and write of the command honours it).",
    ),
):
    set_branch(branch or MAIN)


def _ctx(settings: Settings | None = None):
    from ea.backend import backend_from_settings
    from ea.metamodel import Registry, load_pack
    from ea.services import GraphService, RepositoryService

    settings = settings or Settings.from_env()
    backend = backend_from_settings(settings)
    packs = backend.list_packs()
    if packs:
        pack = backend.load_pack(packs[0]["pack_id"])
    else:
        pack = load_pack(settings.pack_path)
        backend.save_pack(pack)
    registry = Registry(pack)
    return settings, backend, registry, RepositoryService(backend, registry), GraphService(backend, registry)


def _branches():
    from ea.services import BranchService

    _, backend, registry, *_ = _ctx()
    return backend, registry, BranchService(backend, registry)


@app.command()
def init(
    pack: Path = typer.Option(None, help="metamodel pack to load (default: EA_PACK)"),
    db: Path = typer.Option(None, help="DuckDB file (default: EA_DB_PATH)"),
):
    """Create the database and load a metamodel pack."""
    from ea.metamodel import load_pack

    settings = Settings.from_env()
    if db:
        settings.db_path = str(db)
    if pack:
        settings.pack_path = str(pack)
    _, backend, registry, *_ = _ctx(settings)
    p = load_pack(settings.pack_path)
    backend.save_pack(p)
    typer.echo(
        f"database {settings.db_path}: pack '{p.id}' loaded ({len(p.element_types)} element types, {len(p.relationship_types)} relationship types)"
    )


@app.command("load-pack")
def load_pack_cmd(path: Path):
    """(Re)load a metamodel pack from YAML."""
    from ea.metamodel import load_pack

    _, backend, *_ = _ctx()
    p = load_pack(path)
    backend.save_pack(p)
    typer.echo(f"pack '{p.id}' version {p.version} loaded")


@app.command("export-pack")
def export_pack(out: Path, pack_id: str = typer.Option(None, help="pack id (default: the loaded pack)")):
    """Write the stored metamodel back to YAML."""
    from ea.metamodel import dump_pack

    _, backend, registry, *_ = _ctx()
    p = backend.load_pack(pack_id) if pack_id else registry.pack
    dump_pack(p, out)
    typer.echo(f"pack '{p.id}' written to {out}")


@app.command("import")
def import_cmd(
    directory: Path,
    source: str = typer.Option("", help="source system name recorded on every row"),
    mapping: Path = typer.Option(None, help="mapping YAML for the source's files and columns"),
    dry_run: bool = typer.Option(False, help="validate and report, load nothing"),
    actor: str = typer.Option("import"),
):
    """Import elements, relationships and links from CSV files (validated against the metamodel)."""
    from ea.importer import import_directory, load_mapping

    _, backend, registry, *_ = _ctx()
    m = load_mapping(mapping) if mapping else None
    report = import_directory(backend, registry, directory, source, m, actor, dry_run)
    typer.echo(report.summary())
    for iss in report.issues:
        typer.echo("  " + str(iss))
    raise typer.Exit(code=0 if report.ok else 1)


@app.command()
def validate(directory: Path, source: str = typer.Option(""), mapping: Path = typer.Option(None)):
    """Validate CSV files against the metamodel without loading."""
    import_cmd(directory, source, mapping, True)


@app.command()
def stats():
    """Element and relationship counts per type."""
    _, _, registry, repo, _ = _ctx()
    s = repo.stats()
    typer.echo(f"{s['elements']} elements, {s['relationships']} relationships")
    for row in s["by_type"]:
        if row["count"]:
            typer.echo(f"  {row['count']:6d}  {row['name']}")
    if s["unknown_types"]:
        typer.echo(f"  unknown types in store: {s['unknown_types']}")


@app.command()
def find(text: str, type_id: str = typer.Option(None, "--type"), limit: int = 50):
    """Search elements by name, key, id or description."""
    _, _, registry, repo, _ = _ctx()
    t = registry.resolve_type(type_id) if type_id else None
    for e in repo.search(text, t.id if t else None, limit=limit):
        typer.echo(f"{e.element_id:24s} {e.type_id:32s} {e.name}")


@app.command()
def get(element_id: str):
    """Show an element with its relationships."""
    _, _, _, repo, _ = _ctx()
    d = repo.element_detail(element_id)
    e = d["element"]
    typer.echo(
        f"{e.element_id} [{d['type'].name if d['type'] else e.type_id}] {e.name}  status={e.status} version={e.version}"
    )
    if e.description_md:
        typer.echo(e.description_md)
    if e.attrs:
        typer.echo("attributes: " + json.dumps(e.attrs, ensure_ascii=False))
    for ln in d["links"]:
        typer.echo(f"link: {ln.url} {ln.label}")
    for r in d["outgoing"]:
        o = r["other"]
        typer.echo(
            f"  -> {r['label']}{' (' + r['relationship'].qualifier + ')' if r['relationship'].qualifier else ''}: {o.element_id if o else r['relationship'].dst_id} {o.name if o else ''}"
        )
    for r in d["incoming"]:
        o = r["other"]
        typer.echo(
            f"  <- {r['label']}{' (' + r['relationship'].qualifier + ')' if r['relationship'].qualifier else ''}: {o.element_id if o else r['relationship'].src_id} {o.name if o else ''}"
        )


@app.command()
def neighbours(element_id: str, depth: int = 1, direction: str = "both"):
    """Elements within N hops."""
    _, _, _, _, graph = _ctx()
    sub = graph.neighbours(element_id, depth, direction)
    for n in sub["nodes"]:
        typer.echo(f"{n['depth']}  {n['element_id']:24s} {n['type_name']:32s} {n['name']}")


@app.command()
def trace(
    element_id: str,
    direction: str = typer.Option("out", help="out (what this depends on) or in (what depends on this)"),
    depth: int = 5,
):
    """Transitive reach along relationship direction."""
    _, _, _, _, graph = _ctx()
    for r in graph.trace(element_id, direction, depth):
        typer.echo(
            f"{r['depth']}  {r['element_id']:24s} {r['type_name']:32s} {r['name']}   via {' > '.join(r['rel_labels'])}"
        )


@app.command()
def impact(element_id: str, depth: int = 3):
    """Blast radius: upstream dependants and downstream dependencies, with a completeness footer."""
    _, _, _, _, graph = _ctx()
    res = graph.impact(element_id, depth)
    e = res["element"]
    typer.echo(f"Impact of {e['element_id']} [{e['type_name']}] {e['name']}")
    typer.echo(f"  depends on this (upstream, {len(res['upstream'])}):")
    for r in res["upstream"]:
        typer.echo(f"    {r['depth']}  {r['element_id']:24s} {r['type_name']:32s} {r['name']}")
    typer.echo(f"  this depends on (downstream, {len(res['downstream'])}):")
    for r in res["downstream"]:
        typer.echo(f"    {r['depth']}  {r['element_id']:24s} {r['type_name']:32s} {r['name']}")
    c = res["completeness"]
    typer.echo(
        f"  completeness: {c['populated']}/{c['declared']} relationship types for this element type have any instances"
    )
    for name in c["empty"]:
        typer.echo(f"    no instances: {name}")


@app.command()
def view(
    element_id: str,
    depth: int = 1,
    impact: bool = False,
    fmt: str = "mermaid",
    out: str = "",
):
    """An architecture view of an element as Mermaid (default), Markdown or a draw.io file (--fmt md|drawio)."""
    from ea.views import view_from_impact, view_from_neighbourhood
    from ea.views.drawio import to_drawio
    from ea.views.mermaid import to_markdown, to_mermaid

    _, _, registry, _, graph = _ctx()
    if impact:
        v = view_from_impact(registry, graph, graph.impact(element_id, max(depth, 1) if depth != 1 else 3))
    else:
        v = view_from_neighbourhood(registry, graph, element_id, depth)
    text = {"mermaid": to_mermaid, "md": to_markdown, "drawio": to_drawio}.get(fmt, to_mermaid)(v)
    if out:
        Path(out).write_text(text, encoding="utf-8")
        typer.echo(f"{out}: {len(v.nodes)} elements, {len(v.edges)} relationships")
    else:
        typer.echo(text)


@app.command()
def target(
    work_package: str = typer.Option(
        None, "--work-package", "-w", help="a work package element id; default: all"
    ),
    fmt: str = typer.Option("table", help="table or md (a Markdown section with the marked view)"),
):
    """Current state against target state, per work package: counts, the artefacts, and a marked view."""
    from ea.services import TargetStateService
    from ea.services.target import CURRENT_STYLE, TARGET_STYLE, state_label
    from ea.views import view_from_ids
    from ea.views.mermaid import to_markdown

    _, backend, registry, _, graph = _ctx()
    svc = TargetStateService(backend, registry)
    summary = svc.summary(work_package)
    if fmt == "md":
        title = "Target state"
        if work_package:
            wp = backend.get_element(work_package)
            title = f"Target state of {wp.name if wp else work_package}"
        view = view_from_ids(
            registry, graph, svc.scope_ids(work_package), title, [work_package] if work_package else []
        )
        typer.echo(to_markdown(view, marked=True))
        return
    typer.echo(
        f"{summary['elements']} elements, {summary['relationships']} relationships"
        + (f" under {work_package}" if work_package else "")
        + f"; {summary['changes']} elements change"
    )
    typer.echo("  by target state: " + ", ".join(f"{k} {v}" for k, v in summary["by_target"].items() if v))
    for e in svc.elements(work_package, only_changes=not work_package):
        typer.echo(
            f"  {e.element_id:26s} {e.name[:38]:38s} {state_label(e.current_state, CURRENT_STYLE):18s} -> "
            f"{state_label(e.target_state, TARGET_STYLE):13s} {e.target_note[:50]}"
        )


@branch_app.command("list")
def branch_list(status: str = typer.Option(None, help="open, merged or abandoned")):
    """The branches of the model and how many rows each carries."""
    _, _, svc = _branches()
    rows = svc.list(status)
    if not rows:
        typer.echo("no branches")
    for b in rows:
        typer.echo(
            f"{b.branch_id:32s} {b.status:10s} {b.changes:5d} rows  {b.work_package or '-':20s} {b.created_by} {str(b.created_at)[:16]}  {b.name}"
        )


@branch_app.command("create")
def branch_create(
    name: str,
    description: str = typer.Option("", help="what the branch is for"),
    work_package: str = typer.Option(
        "", "--work-package", "-w", help="the work package element id it belongs to"
    ),
    actor: str = typer.Option("cli"),
):
    """Create a branch from main (its id is derived from the name)."""
    _, _, svc = _branches()
    b = svc.create(name, actor, description, work_package)
    typer.echo(f"branch '{b.branch_id}' created; use --branch {b.branch_id} on other commands to work on it")


@branch_app.command("diff")
def branch_diff(branch_id: str):
    """The branch's change set against main: what was added, changed, deleted, and what conflicts."""
    _, _, svc = _branches()
    cs = svc.diff(branch_id)
    c = cs.counts()
    typer.echo(
        f"branch '{branch_id}' ({cs.branch.status}): {c['added']} added, {c['changed']} changed, {c['deleted']} deleted, {c['conflicts']} conflicts"
    )
    for row in svc.item_rows(cs):
        flag = "  CONFLICT" if row["conflict"] else ""
        fields = f"  [{row['fields']}]" if row["fields"] else ""
        typer.echo(
            f"  {row['change']:8s} {row['kind']:12s} {row['entity_id']:28s} {row['label']}{fields}{flag}"
        )


@branch_app.command("merge")
def branch_merge(
    branch_id: str,
    include: list[str] = typer.Option(
        None, "--include", "-i", help="item key(s) to merge (element:<id> or relationship:<id>); default: all"
    ),
    resolve: list[str] = typer.Option(
        None, "--resolve", "-r", help="conflict resolution as key=branch or key=main"
    ),
    actor: str = typer.Option("cli"),
):
    """Merge the branch into main, item by item; unresolved conflicts and unticked items remain on the branch."""
    _, _, svc = _branches()
    resolutions = {}
    for r in resolve or []:
        k, _, v = r.partition("=")
        resolutions[k] = v
    res = svc.merge(branch_id, actor, set(include) if include else None, resolutions)
    typer.echo(
        f"merged {len(res.applied)} item(s), dropped {len(res.dropped)}, {res.remaining} remaining; branch {'closed' if res.closed else 'still open'}"
    )


@branch_app.command("abandon")
def branch_abandon(branch_id: str, actor: str = typer.Option("cli")):
    """Close the branch and discard its rows; main is untouched."""
    _, _, svc = _branches()
    svc.abandon(branch_id, actor)
    typer.echo(f"branch '{branch_id}' abandoned")


@app.command()
def sql(query: str, limit: int = 100):
    """Read-only SQL over the repository tables."""
    _, backend, *_ = _ctx()
    typer.echo(backend.query(query, limit=limit).to_string(index=False))


@app.command()
def summary(types: str = typer.Option(None, help="comma-separated type ids to restrict the summary")):
    """The metamodel as Markdown (what the agent is told)."""
    _, _, registry, *_ = _ctx()
    typer.echo(registry.summary_markdown(types.split(",") if types else None))


if __name__ == "__main__":
    app()
