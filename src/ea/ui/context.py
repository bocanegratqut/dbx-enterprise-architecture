"""One application context: settings, store, registry, services, agent, current user."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field

from ea.agent import Agent
from ea.agent.proposal import ProposalService
from ea.agent.tools import ToolBox
from ea.backend import DatabaseBackend, backend_from_settings
from ea.backend.branching import MAIN, current_branch
from ea.config import Settings
from ea.metamodel import Registry, load_pack
from ea.models import User
from ea.services import BranchService, GraphService, RepositoryService, TargetStateService

log = logging.getLogger(__name__)
_lock = threading.Lock()
_context: AppContext | None = None


@dataclass
class AppContext:
    settings: Settings
    backend: DatabaseBackend
    registry: Registry
    repo: RepositoryService = field(init=False)
    graph: GraphService = field(init=False)
    branches: BranchService = field(init=False)
    target: TargetStateService = field(init=False)
    _agent: Agent | None = field(default=None, init=False)
    _proposals: ProposalService | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.repo = RepositoryService(self.backend, self.registry)
        self.graph = GraphService(self.backend, self.registry)
        self.branches = BranchService(self.backend, self.registry)
        self.target = TargetStateService(self.backend, self.registry)

    @property
    def agent(self) -> Agent:
        if self._agent is None:
            self._agent = Agent(ToolBox(self.backend, self.registry, self.repo, self.graph), self.settings)
        return self._agent

    @property
    def proposals(self) -> ProposalService:
        if self._proposals is None:
            self._proposals = ProposalService(
                self.backend,
                self.registry,
                self.repo,
                self.branches,
                self.target,
                self.settings,
                ToolBox(self.backend, self.registry, self.repo, self.graph),
            )
        return self._proposals

    def reload_registry(self) -> Registry:
        """After the metamodel changed: re-read the stored pack and rebuild everything that depends on it."""
        pack = self.backend.load_pack(self.registry.pack.id) or self.registry.pack
        self.registry = Registry(pack)
        self.repo = RepositoryService(self.backend, self.registry)
        self.graph = GraphService(self.backend, self.registry)
        self.branches = BranchService(self.backend, self.registry)
        self.target = TargetStateService(self.backend, self.registry)
        self._agent = None
        self._proposals = None
        return self.registry

    # ------------------------------------------------------------ branch
    def branch(self) -> str:
        """The branch this request reads and writes (set from the session before the request)."""
        return current_branch()

    def on_branch(self) -> bool:
        return current_branch() != MAIN

    def branch_options(self) -> list[dict[str, str]]:
        """`main` and the open branches, for the header selector."""
        opts = [{"value": MAIN, "label": "main"}]
        for b in self.branches.open():
            opts.append({"value": b.branch_id, "label": f"{b.name} ({b.changes})"})
        return opts

    def work_package_options(self) -> list[dict[str, str]]:
        return [
            {"value": w.element_id, "label": f"{w.name} [{w.element_id}]"}
            for w in self.target.work_packages()
        ]

    def base_url(self) -> str:
        """The URL the app is reached at, for links inside exported files; empty when unknown."""
        try:
            from flask import has_request_context, request

            if has_request_context():
                return request.url_root.rstrip("/")
        except Exception:  # noqa: BLE001 — links are a courtesy, never a failure
            pass
        return ""

    def current_user(self) -> User:
        if self.settings.auth == "databricks":
            try:
                from flask import has_request_context, request

                if has_request_context():
                    email = (
                        request.headers.get("X-Forwarded-Email")
                        or request.headers.get("X-Forwarded-Preferred-Username")
                        or ""
                    )
                    if email:
                        return User(username=email, display_name=email.split("@")[0])
            except Exception:  # noqa: BLE001
                pass
        return User(
            username="architect@example.edu", display_name="Information Architect", groups=["ea-architects"]
        )

    @property
    def actor(self) -> str:
        return self.current_user().username


def get_context() -> AppContext:
    global _context
    with _lock:
        if _context is None:
            settings = Settings.from_env()
            backend = backend_from_settings(settings)
            packs = backend.list_packs()
            if packs:
                pack = backend.load_pack(packs[0]["pack_id"])
            else:
                pack = load_pack(settings.pack_path)
                backend.save_pack(pack)
                log.info("loaded pack %s from %s", pack.id, settings.pack_path)
            _context = AppContext(settings, backend, Registry(pack))
        return _context
