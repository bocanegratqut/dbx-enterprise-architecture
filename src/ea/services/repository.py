"""Reads and writes on the graph, validated against the metamodel and audited.

The UI and the agent call this; nobody writes to the backend directly.
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any

from ea.backend.base import DatabaseBackend
from ea.metamodel.registry import Registry
from ea.models import Element, Link, NotFoundError, Relationship, ValidationError


def relationship_key(
    source_system: str, rel_type_id: str, src_id: str, dst_id: str, qualifier: str = ""
) -> str:
    """A deterministic relationship id, so re-importing the same edge is an update, not a duplicate."""
    raw = "|".join([source_system or "", rel_type_id, src_id, dst_id, qualifier or ""])
    return "rel-" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def coerce_attrs(registry: Registry, type_id: str, attrs: dict[str, Any] | None) -> dict[str, Any]:
    """Cast attribute values to their declared type; unknown attributes pass through as strings."""
    if not attrs:
        return {}
    defs = {a.name: a for a in registry.attributes_for(type_id)}
    out: dict[str, Any] = {}
    for k, v in attrs.items():
        if v is None or (isinstance(v, str) and v.strip() == ""):
            continue
        d = defs.get(k)
        if d is None:
            out[k] = v
            continue
        try:
            if d.type == "integer":
                out[k] = int(float(v))
            elif d.type == "number":
                out[k] = float(v)
            elif d.type == "boolean":
                out[k] = v if isinstance(v, bool) else str(v).strip().lower() in ("1", "true", "yes", "y")
            else:
                out[k] = v
        except (TypeError, ValueError):
            out[k] = v
    return out


class RepositoryService:
    def __init__(self, backend: DatabaseBackend, registry: Registry):
        self.backend = backend
        self.registry = registry

    # ------------------------------------------------------------- reads
    def element(self, element_id: str) -> Element:
        e = self.backend.get_element(element_id)
        if e is None:
            raise NotFoundError(element_id)
        return e

    def search(
        self,
        text: str | None = None,
        type_id: str | list[str] | None = None,
        status: str | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> list[Element]:
        return self.backend.find_elements(
            text=text, type_id=type_id, status=status, limit=limit, offset=offset
        )

    def element_detail(self, element_id: str) -> dict[str, Any]:
        e = self.element(element_id)
        t = self.registry.get_type(e.type_id)
        rels = self.backend.relationships_of(element_id, "both")
        other_ids = {r.dst_id if r.src_id == element_id else r.src_id for r in rels}
        others = {o.element_id: o for o in (self.backend.get_element(i) for i in other_ids) if o}
        outgoing, incoming = [], []
        for r in rels:
            rt = self.registry.rel_types.get(r.rel_type_id)
            if r.src_id == element_id:
                other = others.get(r.dst_id)
                outgoing.append(
                    {"relationship": r, "label": (rt.name if rt else r.rel_type_id), "other": other}
                )
            else:
                other = others.get(r.src_id)
                incoming.append(
                    {"relationship": r, "label": (rt.inverse if rt else r.rel_type_id), "other": other}
                )
        return {"element": e, "type": t, "outgoing": outgoing, "incoming": incoming, "links": e.links}

    def stats(self) -> dict[str, Any]:
        by_type = self.backend.count_by_type()
        by_rel = self.backend.count_by_rel_type()
        rows = []
        for t in self.registry.pack.element_types:
            rows.append(
                {
                    "type_id": t.id,
                    "name": t.name,
                    "domain": t.domain,
                    "active": t.active,
                    "count": by_type.get(t.id, 0),
                }
            )
        unknown = [k for k in by_type if k not in self.registry.types]
        rel_rows = [
            {
                "rel_type_id": r.id,
                "name": r.name,
                "source": r.source,
                "target": r.target,
                "count": by_rel.get(r.id, 0),
            }
            for r in self.registry.pack.relationship_types
        ]
        return {
            "elements": sum(by_type.values()),
            "relationships": sum(by_rel.values()),
            "by_type": rows,
            "by_rel_type": rel_rows,
            "unknown_types": unknown,
        }

    def history(self, entity_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        return self.backend.history(entity_id, limit)

    # ------------------------------------------------------------ writes
    def mint_id(self, type_id: str) -> str:
        t = self.registry.get_type(type_id)
        prefix = t.prefix if t and t.prefix else type_id.upper()[:6]
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def create_element(
        self,
        type_id: str,
        name: str,
        actor: str,
        element_id: str | None = None,
        key: str = "",
        description_md: str = "",
        attrs: dict[str, Any] | None = None,
        status: str = "draft",
        lifecycle_status: str = "",
        links: list[Link] | None = None,
        origin: str = "user",
    ) -> Element:
        t = self.registry.resolve_type(type_id)
        if t is None:
            raise ValidationError(self.registry.validate_element(type_id, attrs))
        attrs = coerce_attrs(self.registry, t.id, attrs)
        issues = [i for i in self.registry.validate_element(t.id, attrs) if i.level == "error"]
        if not name or not name.strip():
            issues.append(_err("missing_name", "name is required"))
        if issues:
            raise ValidationError(issues)
        e = Element(
            element_id=element_id or self.mint_id(t.id),
            type_id=t.id,
            name=name.strip(),
            key=key,
            description_md=description_md,
            status=status,
            lifecycle_status=lifecycle_status,
            attrs=attrs,
            origin=origin,
            source_system="" if origin == "user" else origin,
        )
        e = self.backend.insert_element(e, actor)
        if links:
            e.links = self.backend.set_links(e.element_id, links, actor)
        return e

    def update_element(self, element_id: str, actor: str, expected_version: int, **fields: Any) -> Element:
        e = self.element(element_id)
        if "type_id" in fields and fields["type_id"]:
            t = self.registry.resolve_type(fields["type_id"])
            if t is None:
                raise ValidationError([_err("unknown_type", f"unknown element type {fields['type_id']!r}")])
            e.type_id = t.id
        for k in ("name", "key", "description_md", "status", "lifecycle_status"):
            if k in fields and fields[k] is not None:
                setattr(e, k, fields[k])
        if "attrs" in fields and fields["attrs"] is not None:
            e.attrs = coerce_attrs(self.registry, e.type_id, fields["attrs"])
        issues = [i for i in self.registry.validate_element(e.type_id, e.attrs) if i.level == "error"]
        if not e.name.strip():
            issues.append(_err("missing_name", "name is required"))
        if issues:
            raise ValidationError(issues)
        e = self.backend.update_element(e, actor, expected_version)
        if "links" in fields and fields["links"] is not None:
            e.links = self.backend.set_links(element_id, fields["links"], actor)
        else:
            e.links = self.backend.get_links(element_id)
        return e

    def retire_element(self, element_id: str, actor: str, expected_version: int) -> Element:
        return self.update_element(element_id, actor, expected_version, status="retired")

    def add_relationship(
        self,
        rel_type: str,
        src_id: str,
        dst_id: str,
        actor: str,
        qualifier: str = "",
        attrs: dict[str, Any] | None = None,
        origin: str = "user",
    ) -> Relationship:
        src, dst = self.element(src_id), self.element(dst_id)
        rt = self.registry.resolve_rel_type(rel_type, src.type_id, dst.type_id)
        if rt is None:
            allowed = (
                ", ".join(r.name for r in self.registry.allowed_rel_types(src.type_id, dst.type_id)) or "none"
            )
            raise ValidationError(
                [
                    _err(
                        "unknown_relationship_type",
                        f"no relationship {rel_type!r} between {src.type_id} and {dst.type_id}; allowed: {allowed}",
                    )
                ]
            )
        issues = [
            i
            for i in self.registry.validate_relationship(rt.id, src.type_id, dst.type_id, qualifier)
            if i.level == "error"
        ]
        if issues:
            raise ValidationError(issues)
        rel = Relationship(
            relationship_id=relationship_key(origin, rt.id, src_id, dst_id, qualifier),
            rel_type_id=rt.id,
            src_id=src_id,
            dst_id=dst_id,
            qualifier=qualifier,
            attrs=attrs or {},
            status="approved",
            origin=origin,
        )
        if self.backend.get_relationship(rel.relationship_id):
            return self.backend.get_relationship(rel.relationship_id)  # type: ignore[return-value]
        return self.backend.insert_relationship(rel, actor)

    def remove_relationship(self, relationship_id: str, actor: str) -> None:
        self.backend.delete_relationship(relationship_id, actor)


def _err(code: str, message: str):
    from ea.models import Issue

    return Issue("error", code, message)
