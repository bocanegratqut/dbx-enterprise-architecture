"""Application shell: header, navigation and the routed page container."""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import dcc, html

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
    ("Import", "/import", "tabler:file-import"),
    ("Ask", "/ask", "tabler:message-chatbot"),
]


def shell(title: str, pack_name: str) -> dmc.MantineProvider:
    return dmc.MantineProvider(
        theme=THEME,
        defaultColorScheme="light",
        children=[
            dcc.Location(id=ids.URL, refresh=False),
            dcc.Store(id=ids.NAV_VERSION, data=0),
            dcc.Download(id=ids.DOWNLOAD),
            dmc.NotificationContainer(id=ids.NOTIFY, position="top-right"),
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
