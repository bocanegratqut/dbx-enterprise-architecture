"""Domain model: metamodel definitions, graph content and reports.

Knows nothing about SQL, YAML or Dash. Every other layer imports from here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

ANY = "ANY"
IDENT_RE = re.compile(r"^[a-z][a-z0-9_]{0,79}$")
ELEMENT_STATUSES = ("draft", "approved", "retired")
ATTRIBUTE_TYPES = ("string", "text", "integer", "number", "boolean", "date", "json")


def slugify(text: str) -> str:
    """A pack-style identifier from a human label: 'Logical Data Component' -> 'logical_data_component'."""
    s = re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")
    if not s:
        raise ValueError(f"cannot derive an identifier from {text!r}")
    if s[0].isdigit():
        s = "x" + s
    return s[:80]


def validate_identifier(value: str, what: str = "identifier") -> str:
    if not IDENT_RE.match(value or ""):
        raise ValueError(f"{what} {value!r} must match {IDENT_RE.pattern}")
    return value


# ----------------------------------------------------------------- metamodel


@dataclass
class AttributeDef:
    name: str
    label: str = ""
    type: str = "string"
    required: bool = False
    enum: list[str] | None = None
    description: str = ""
    sensitivity: str = ""
    type_id: str | None = None  # None = common to every element type

    def __post_init__(self) -> None:
        validate_identifier(self.name, "attribute name")
        if self.type not in ATTRIBUTE_TYPES:
            raise ValueError(f"attribute {self.name}: unknown type {self.type!r}")
        self.label = self.label or self.name.replace("_", " ").title()


@dataclass
class Domain:
    id: str
    name: str
    description: str = ""
    notation: dict[str, str] = field(default_factory=dict)  # default drawing convention for its types
    sort_order: int = 0


@dataclass
class ElementType:
    id: str
    name: str
    plural: str = ""
    supertype: str | None = None
    active: bool = True
    deactivation_reason: str = ""
    domain: str = ""
    provenance: str = ""
    prefix: str = ""
    description: str = ""
    examples: list[str] = field(default_factory=list)
    source_of_record: str = ""
    type_owner: str = ""
    instance_owner: str = ""
    attributes: list[AttributeDef] = field(default_factory=list)
    notation: dict[str, str] = field(default_factory=dict)  # glyph, stereotype, archimate, layer, shape
    sort_order: int = 0

    def __post_init__(self) -> None:
        validate_identifier(self.id, "element type id")
        self.plural = self.plural or self.name + "s"
        for a in self.attributes:
            a.type_id = self.id


@dataclass
class RelationshipType:
    id: str
    name: str
    inverse: str = ""
    source: str = ANY
    target: str = ANY
    provenance: str = ""
    qualifiers: list[str] = field(default_factory=list)
    diagrams: list[str] = field(default_factory=list)
    description: str = ""
    src_max: int | None = None
    dst_max: int | None = None
    sort_order: int = 0

    def __post_init__(self) -> None:
        validate_identifier(self.id, "relationship type id")
        self.inverse = self.inverse or f"is {self.name} by"


@dataclass
class Pack:
    id: str
    name: str
    version: str = ""
    description: str = ""
    source: str = ""
    provenance_values: list[str] = field(default_factory=list)
    domains: list[Domain] = field(default_factory=list)
    common_attributes: list[AttributeDef] = field(default_factory=list)
    element_types: list[ElementType] = field(default_factory=list)
    relationship_types: list[RelationshipType] = field(default_factory=list)

    def __post_init__(self) -> None:
        validate_identifier(self.id, "pack id")


# ------------------------------------------------------------------- content


@dataclass
class Link:
    element_id: str
    url: str
    label: str = ""
    link_id: str = ""
    sort_order: int = 0


@dataclass
class Element:
    element_id: str
    type_id: str
    name: str
    key: str = ""
    description_md: str = ""
    status: str = "draft"
    lifecycle_status: str = ""
    source_system: str = ""
    source_ref: str = ""
    external_ids: dict[str, str] = field(default_factory=dict)
    attrs: dict[str, Any] = field(default_factory=dict)
    origin: str = ""
    version: int = 1
    created_at: datetime | None = None
    created_by: str = ""
    updated_at: datetime | None = None
    updated_by: str = ""
    links: list[Link] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.status not in ELEMENT_STATUSES:
            raise ValueError(f"element {self.element_id}: status must be one of {ELEMENT_STATUSES}")


@dataclass
class Relationship:
    relationship_id: str
    rel_type_id: str
    src_id: str
    dst_id: str
    qualifier: str = ""
    attrs: dict[str, Any] = field(default_factory=dict)
    status: str = "draft"
    origin: str = ""
    source_system: str = ""
    source_ref: str = ""
    version: int = 1
    created_at: datetime | None = None
    created_by: str = ""
    updated_at: datetime | None = None
    updated_by: str = ""


@dataclass
class User:
    username: str
    display_name: str = ""
    groups: list[str] = field(default_factory=list)


# ------------------------------------------------------------------- reports


@dataclass
class Issue:
    level: str  # error | warning | info
    code: str
    message: str
    row: int | None = None
    entity: str | None = None
    file: str | None = None

    def __str__(self) -> str:
        where = " ".join(
            p for p in (self.file, f"row {self.row}" if self.row is not None else "", self.entity or "") if p
        )
        return f"[{self.level}] {self.code}: {self.message}" + (f" ({where})" if where else "")


@dataclass
class ImportReport:
    source_system: str
    elements_read: int = 0
    relationships_read: int = 0
    links_read: int = 0
    elements_loaded: int = 0
    relationships_loaded: int = 0
    links_loaded: int = 0
    elements_skipped: int = 0
    relationships_skipped: int = 0
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def summary(self) -> str:
        return (
            f"source={self.source_system} elements {self.elements_loaded}/{self.elements_read} loaded"
            f" ({self.elements_skipped} skipped), relationships {self.relationships_loaded}/{self.relationships_read}"
            f" loaded ({self.relationships_skipped} skipped), links {self.links_loaded}/{self.links_read};"
            f" {len(self.errors)} errors, {len(self.warnings)} warnings"
        )


class ConflictError(Exception):
    """Optimistic-concurrency conflict: the row changed since it was read."""


class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    def __init__(self, issues: list[Issue]):
        self.issues = issues
        super().__init__("; ".join(str(i) for i in issues))
