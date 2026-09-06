"""Application shell: header with the branch selector, navigation and the routed page container."""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import dcc, html

from ea.backend.branching import MAIN
from ea.ui import ids
from ea.ui.components import icon

THEME = {
    "primaryColor": "indigo",
    "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "defaultRadius": "md",
    "headings": {"fontWeight": "650"},
}

NAV = [
    ("Home", "/", "tabler:home"),
    ("Browse", "/browse", "tabler:list-search"),
    ("Metamodel", "/metamodel", "tabler:hierarchy-2"),
    ("Impact", "/impact", "tabler:radar"),
    ("Target state", "/target", "tabler:target-arrow"),
    ("Branches", "/branches", "tabler:git-branch"),
    ("Import", "/import", "tabler:file-import"),
    ("Ask", "/ask", "tabler:message-chatbot"),
    ("Propose", "/propose", "tabler:file-plus"),
]


def branch_badge(branch_id: str, changes: int | None = None) -> dmc.Badge:
    """What the header says about the branch the reader is on."""
    if branch_id == MAIN:
        return dmc.Badge(
            "main", variant="light", color="gray", size="lg", leftSection=icon("tabler:git-branch", 12)
        )
    label = f"branch · {changes} change{'s' if changes != 1 else ''}" if changes is not None else "branch"
    return dmc.Badge(
        label, variant="filled", color="orange", size="lg", leftSection=icon("tabler:git-branch", 12)
    )


def new_branch_modal(work_packages: list[dict[str, str]]) -> dmc.Modal:
    return dmc.Modal(
        id=ids.BRANCH_NEW_MODAL,
        title="New branch",
        children=dmc.Stack(
            [
                dmc.Text(
                    "A branch starts from main as it is now. What you add, change or remove on it stays on the "
                    "branch until you merge it, item by item, on the Branches page.",
                    size="sm",
                    c="dimmed",
                ),
                dmc.TextInput(
                    id=ids.BRANCH_NEW_NAME, label="Name", required=True, placeholder="CMS upgrade phase 2"
                ),
                dmc.Textarea(id=ids.BRANCH_NEW_DESC, label="What it is for", autosize=True, minRows=2),
                dmc.Select(
                    id=ids.BRANCH_NEW_WP,
                    label="Work package",
                    data=work_packages,
                    searchable=True,
                    clearable=True,
                    placeholder="Optional",
                ),
                html.Div(id=ids.BRANCH_NEW_FEEDBACK),
                dmc.Group(
                    [
                        dmc.Button(
                            "Create and switch", id=ids.BRANCH_NEW_SAVE, leftSection=icon("tabler:git-branch")
                        )
                    ],
                    justify="flex-end",
                ),
            ]
        ),
    )


def shell(
    title: str,
    pack_name: str,
    branch_options: list[dict[str, str]],
    current: str = MAIN,
    changes: int | None = None,
    work_packages: list[dict[str, str]] | None = None,
) -> dmc.MantineProvider:
    return dmc.MantineProvider(
        theme=THEME,
        defaultColorScheme="light",
        children=[
            dcc.Location(id=ids.URL, refresh=False),
            dcc.Store(id=ids.NAV_VERSION, data=0),
            dcc.Download(id=ids.DOWNLOAD),
            dmc.NotificationContainer(id=ids.NOTIFY, position="top-right"),
            new_branch_modal(work_packages or []),
            dmc.AppShell(
                [
                    dmc.AppShellHeader(
                        dmc.Group(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            icon("tabler:topology-star-3", 20), className="ea-brand-mark"
                                        ),
                                        dmc.Stack(
                                            [
                                                dmc.Title(title, order=4, style={"lineHeight": 1.1}),
                                                dmc.Text(
                                                    "model first · agent ready · DuckDB now, Databricks next",
                                                    size="xs",
                                                    c="dimmed",
                                                ),
                                            ],
                                            gap=0,
                                        ),
                                    ],
                                    className="ea-brand",
                                ),
                                dmc.Group(
                                    [
                                        html.Div(branch_badge(current, changes), id=ids.BRANCH_BADGE),
                                        dmc.Select(
                                            id=ids.BRANCH_SELECT,
                                            data=branch_options,
                                            value=current,
                                            w=240,
                                            size="sm",
                                            allowDeselect=False,
                                            leftSection=icon("tabler:git-branch", 14),
                                            comboboxProps={"withinPortal": True},
                                        ),
                                        dmc.Tooltip(
                                            dmc.ActionIcon(
                                                icon("tabler:plus", 16),
                                                id=ids.BRANCH_NEW_OPEN,
                                                variant="light",
                                                size="lg",
                                            ),
                                            label="New branch from main",
                                        ),
                                        dmc.Badge(pack_name, variant="light", color="indigo", size="lg"),
                                        dmc.Badge("PoC", variant="outline", color="gray", size="lg"),
                                    ],
                                    gap="xs",
                                ),
                            ],
                            justify="space-between",
                            h=56,
                            px="md",
                        )
                    ),
                    dmc.AppShellNavbar(
                        dmc.Stack(
                            [
                                dmc.NavLink(
                                    label=label,
                                    href=href,
                                    leftSection=icon(ic, 18),
                                    id=f"nav-{href.strip('/') or 'home'}",
                                    variant="light",
                                )
                                for label, href, ic in NAV
                            ]
                            + [
                                dmc.Divider(my="sm"),
                                dmc.Text(
                                    "A generic, metamodel-driven EA repository. Local DuckDB now, Databricks next.",
                                    size="xs",
                                    c="dimmed",
                                    px="sm",
                                ),
                            ],
                            gap=2,
                            p="xs",
                        )
                    ),
                    dmc.AppShellMain(
                        html.Div(id=ids.PAGE, style={"padding": "1rem 1.5rem", "maxWidth": 1400})
                    ),
                ],
                header={"height": 56},
                navbar={"width": 220, "breakpoint": "sm"},
                padding="md",
            ),
        ],
    )
