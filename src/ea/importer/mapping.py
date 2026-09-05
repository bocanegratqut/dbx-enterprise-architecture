"""An import mapping: how a source's files and columns land on the CSV contract.

Without a mapping the importer expects the contract as-is (see connectors/README.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CORE_ELEMENT_COLUMNS = (
    "id",
    "type",
    "name",
    "key",
    "description",
    "status",
    "lifecycle_status",
    "links",
    "source_ref",
    "origin",
)
CORE_RELATIONSHIP_COLUMNS = ("src_id", "rel_type", "dst_id", "qualifier", "status", "source_ref")
CORE_LINK_COLUMNS = ("element_id", "url", "label")


@dataclass
class Mapping:
    source_system: str = ""
    element_files: list[str] = field(default_factory=lambda: ["*element*.csv"])
    relationship_files: list[str] = field(default_factory=lambda: ["*relationship*.csv"])
    link_files: list[str] = field(default_factory=lambda: ["*link*.csv"])
    element_columns: dict[str, str] = field(default_factory=dict)
    relationship_columns: dict[str, str] = field(default_factory=dict)
    link_columns: dict[str, str] = field(default_factory=dict)
    type_names: dict[str, str] = field(default_factory=dict)
    rel_names: dict[str, str] = field(default_factory=dict)
    type_from_filename: bool = False
    element_defaults: dict[str, Any] = field(default_factory=dict)
    relationship_defaults: dict[str, Any] = field(default_factory=dict)
    ignore_columns: list[str] = field(default_factory=list)
    encoding: str = "utf-8-sig"

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Mapping:
        files = d.get("files") or {}
        el = d.get("elements") or {}
        rel = d.get("relationships") or {}
        ln = d.get("links") or {}
        return cls(
            source_system=d.get("source_system", ""),
            element_files=list(files.get("elements") or el.get("files") or ["*element*.csv"]),
            relationship_files=list(files.get("relationships") or rel.get("files") or ["*relationship*.csv"]),
            link_files=list(files.get("links") or ln.get("files") or ["*link*.csv"]),
            element_columns=dict(el.get("columns") or {}),
            relationship_columns=dict(rel.get("columns") or {}),
            link_columns=dict(ln.get("columns") or {}),
            type_names=dict(el.get("type_names") or {}),
            rel_names=dict(rel.get("rel_names") or {}),
            type_from_filename=bool(el.get("type_from_filename", False)),
            element_defaults=dict(el.get("defaults") or {}),
            relationship_defaults=dict(rel.get("defaults") or {}),
            ignore_columns=list(el.get("ignore_columns") or []),
            encoding=d.get("encoding", "utf-8-sig"),
        )


def load_mapping(path: str | Path) -> Mapping:
    with open(path, encoding="utf-8") as fh:
        return Mapping.from_dict(yaml.safe_load(fh) or {})
