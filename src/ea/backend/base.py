"""The repository contract. The only place SQL is allowed is a backend implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from ea.models import Element, Link, Pack, Relationship


class DatabaseBackend(ABC):
    """Everything the services and the UI need from storage.

    Writes take an `actor` for the audit trail. Updates carry the version the
    caller read; a mismatch raises ConflictError and never overwrites.
    """

    # ------------------------------------------------------------ lifecycle
    @abstractmethod
    def init_schema(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    # ------------------------------------------------------------ metamodel
    @abstractmethod
    def save_pack(self, pack: Pack) -> None:
        """Replace the stored definition of this pack id."""

    @abstractmethod
    def load_pack(self, pack_id: str) -> Pack | None: ...

    @abstractmethod
    def list_packs(self) -> list[dict[str, Any]]: ...

    # ------------------------------------------------------------- elements
    @abstractmethod
    def get_element(self, element_id: str) -> Element | None: ...

    @abstractmethod
    def find_elements(
        self,
        text: str | None = None,
        type_id: str | list[str] | None = None,
        status: str | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> list[Element]: ...

    @abstractmethod
    def count_elements(self, type_id: str | None = None, text: str | None = None) -> int: ...

    @abstractmethod
    def count_by_type(self) -> dict[str, int]: ...

    @abstractmethod
    def insert_element(self, element: Element, actor: str) -> Element: ...

    @abstractmethod
    def update_element(
        self, element: Element, actor: str, expected_version: int | None = None
    ) -> Element: ...

    @abstractmethod
    def upsert_elements(self, elements: list[Element], actor: str) -> tuple[int, int]:
        """Bulk load by element_id. Returns (inserted, updated)."""

    @abstractmethod
    def set_links(self, element_id: str, links: list[Link], actor: str) -> list[Link]: ...

    @abstractmethod
    def get_links(self, element_id: str) -> list[Link]: ...

    # -------------------------------------------------------- relationships
    @abstractmethod
    def get_relationship(self, relationship_id: str) -> Relationship | None: ...

    @abstractmethod
    def relationships_of(self, element_id: str, direction: str = "both") -> list[Relationship]: ...

    @abstractmethod
    def find_relationships(self, rel_type_id: str | None = None, limit: int = 500) -> list[Relationship]: ...

    @abstractmethod
    def count_relationships(self, rel_type_id: str | None = None) -> int: ...

    @abstractmethod
    def count_by_rel_type(self) -> dict[str, int]: ...

    @abstractmethod
    def insert_relationship(self, rel: Relationship, actor: str) -> Relationship: ...

    @abstractmethod
    def update_relationship(
        self, rel: Relationship, actor: str, expected_version: int | None = None
    ) -> Relationship: ...

    @abstractmethod
    def delete_relationship(self, relationship_id: str, actor: str) -> None: ...

    @abstractmethod
    def upsert_relationships(self, rels: list[Relationship], actor: str) -> tuple[int, int]: ...

    # ---------------------------------------------------------------- graph
    @abstractmethod
    def trace(self, element_id: str, direction: str = "out", max_depth: int = 5) -> list[dict[str, Any]]:
        """Reachable elements with depth, node path and relationship-type path."""

    @abstractmethod
    def edges_frame(self) -> pd.DataFrame:
        """All non-retired relationships as (src_id, dst_id, rel_type_id, qualifier, relationship_id)."""

    # ---------------------------------------------------------------- audit
    @abstractmethod
    def history(self, entity_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]: ...

    # ------------------------------------------------------------------ sql
    @abstractmethod
    def query(self, sql: str, params: list[Any] | None = None, limit: int = 1000) -> pd.DataFrame:
        """Read-only SQL for power users and the agent. Anything but a SELECT is refused."""
