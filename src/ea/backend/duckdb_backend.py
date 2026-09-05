"""DuckDB implementation: one file, zero infrastructure, the same DDL as Delta."""

from __future__ import annotations

import json
import re
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from ea.backend.base import DatabaseBackend
from ea.backend.sql import DDL, ELEMENT_COLUMNS, MIGRATIONS, RELATIONSHIP_COLUMNS, TRACE_IN_SQL, TRACE_OUT_SQL
from ea.metamodel.loader import pack_from_dict
from ea.models import ConflictError, Element, Link, NotFoundError, Pack, Relationship

_READ_ONLY_RE = re.compile(r"^\s*(select|with)\b", re.IGNORECASE)
_FORBIDDEN_RE = re.compile(
    r"\b(insert|update|delete|drop|alter|create|attach|copy|export|import|pragma|call|install|load)\b",
    re.IGNORECASE,
)


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _dumps(value: Any) -> str:
    return json.dumps(value or {}, ensure_ascii=False, sort_keys=True, default=str)


def _loads(value: Any) -> dict[str, Any]:
    if value in (None, ""):
        return {}
    try:
        out = json.loads(value)
        return out if isinstance(out, dict) else {}
    except (TypeError, ValueError):
        return {}


def new_id(prefix: str = "") -> str:
    return (prefix + "-" if prefix else "") + uuid.uuid4().hex[:12]


class DuckDBBackend(DatabaseBackend):
    def __init__(self, path: str | Path = ":memory:"):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = duckdb.connect(self.path)
        self._lock = threading.RLock()
        self.init_schema()

    # ------------------------------------------------------------ helpers
    def _execute(self, sql: str, params: list[Any] | None = None) -> duckdb.DuckDBPyConnection:
        with self._lock:
            return self._conn.execute(sql, params or [])

    def _fetch_df(self, sql: str, params: list[Any] | None = None) -> pd.DataFrame:
        with self._lock:
            return self._conn.execute(sql, params or []).df()

    def _fetch_all(self, sql: str, params: list[Any] | None = None) -> list[tuple]:
        with self._lock:
            return self._conn.execute(sql, params or []).fetchall()

    def _log(
        self, kind: str, entity_id: str, op: str, actor: str, before: Any, after: Any, version: int | None
    ) -> None:
        self._execute(
            "INSERT INTO change_log VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                new_id("chg"),
                kind,
                entity_id,
                op,
                actor,
                _now(),
                _dumps(before) if before else None,
                _dumps(after) if after else None,
                version,
            ],
        )

    # ---------------------------------------------------------- lifecycle
    def init_schema(self) -> None:
        for ddl in DDL.values():
            self._execute(ddl)
        for table, column, dtype in MIGRATIONS:  # older files: add what shipped later
            self._execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {dtype}")

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    # ---------------------------------------------------------- metamodel
    def save_pack(self, pack: Pack) -> None:
        with self._lock:
            for t in (
                "meta_pack",
                "meta_domain",
                "meta_element_type",
                "meta_attribute",
                "meta_relationship_type",
            ):
                self._execute(f"DELETE FROM {t} WHERE pack_id = ?", [pack.id])
            self._execute(
                "INSERT INTO meta_pack VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    pack.id,
                    pack.name,
                    pack.version,
                    pack.description,
                    pack.source,
                    json.dumps(pack.provenance_values),
                    _now(),
                ],
            )
            for d in pack.domains:
                self._execute(
                    "INSERT INTO meta_domain VALUES (?, ?, ?, ?, ?, ?)",
                    [pack.id, d.id, d.name, d.description, d.sort_order, json.dumps(d.notation)],
                )
            for i, a in enumerate(pack.common_attributes):
                self._execute(
                    "INSERT INTO meta_attribute VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        pack.id,
                        None,
                        a.name,
                        a.label,
                        a.type,
                        a.required,
                        json.dumps(a.enum) if a.enum else None,
                        a.description,
                        a.sensitivity,
                        i,
                    ],
                )
            for t in pack.element_types:
                self._execute(
                    "INSERT INTO meta_element_type VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        pack.id,
                        t.id,
                        t.name,
                        t.plural,
                        t.supertype,
                        t.active,
                        t.deactivation_reason,
                        t.domain,
                        t.provenance,
                        t.prefix,
                        t.description,
                        json.dumps(t.examples),
                        t.source_of_record,
                        t.type_owner,
                        t.instance_owner,
                        t.sort_order,
                        json.dumps(t.notation),
                    ],
                )
                for i, a in enumerate(t.attributes):
                    self._execute(
                        "INSERT INTO meta_attribute VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        [
                            pack.id,
                            t.id,
                            a.name,
                            a.label,
                            a.type,
                            a.required,
                            json.dumps(a.enum) if a.enum else None,
                            a.description,
                            a.sensitivity,
                            i,
                        ],
                    )
            for r in pack.relationship_types:
                self._execute(
                    "INSERT INTO meta_relationship_type VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        pack.id,
                        r.id,
                        r.name,
                        r.inverse,
                        r.source,
                        r.target,
                        r.provenance,
                        json.dumps(r.qualifiers),
                        json.dumps(r.diagrams),
                        r.description,
                        r.src_max,
                        r.dst_max,
                        r.sort_order,
                    ],
                )

    def load_pack(self, pack_id: str) -> Pack | None:
        rows = self._fetch_all(
            "SELECT pack_id, name, version, description, source, provenance_values FROM meta_pack WHERE pack_id = ?",
            [pack_id],
        )
        if not rows:
            return None
        pid, name, version, description, source, prov = rows[0]
        domains = [
            {"id": d, "name": n, "description": desc, "notation": json.loads(notation or "{}")}
            for d, n, desc, notation in self._fetch_all(
                "SELECT domain_id, name, description, notation FROM meta_domain WHERE pack_id = ? ORDER BY sort_order",
                [pid],
            )
        ]
        attrs = self._fetch_all(
            "SELECT type_id, name, label, datatype, required, enum_values, description, sensitivity FROM meta_attribute WHERE pack_id = ? ORDER BY sort_order",
            [pid],
        )

        def attr_dict(row: tuple) -> dict[str, Any]:
            _, aname, label, dtype, required, enum_values, adesc, sens = row
            d: dict[str, Any] = {
                "name": aname,
                "label": label,
                "type": dtype,
                "required": bool(required),
                "description": adesc,
                "sensitivity": sens,
            }
            if enum_values:
                d["enum"] = json.loads(enum_values)
            return d

        common = [attr_dict(a) for a in attrs if a[0] is None]
        element_types = []
        for row in self._fetch_all(
            "SELECT type_id, name, plural, supertype_id, active, deactivation_reason, domain_id, provenance, prefix, description, examples, source_of_record, type_owner, instance_owner, notation FROM meta_element_type WHERE pack_id = ? ORDER BY sort_order",
            [pid],
        ):
            tid = row[0]
            element_types.append(
                {
                    "id": tid,
                    "name": row[1],
                    "plural": row[2],
                    "supertype": row[3],
                    "active": bool(row[4]),
                    "deactivation_reason": row[5],
                    "domain": row[6],
                    "provenance": row[7],
                    "prefix": row[8],
                    "description": row[9],
                    "examples": json.loads(row[10] or "[]"),
                    "source_of_record": row[11],
                    "type_owner": row[12],
                    "instance_owner": row[13],
                    "notation": json.loads(row[14] or "{}"),
                    "attributes": [attr_dict(a) for a in attrs if a[0] == tid],
                }
            )
        relationship_types = [
            {
                "id": r[0],
                "name": r[1],
                "inverse": r[2],
                "source": r[3],
                "target": r[4],
                "provenance": r[5],
                "qualifiers": json.loads(r[6] or "[]"),
                "diagrams": json.loads(r[7] or "[]"),
                "description": r[8],
                "src_max": r[9],
                "dst_max": r[10],
            }
            for r in self._fetch_all(
                "SELECT rel_type_id, name, inverse_name, source_type_id, target_type_id, provenance, qualifiers, diagrams, description, src_max, dst_max FROM meta_relationship_type WHERE pack_id = ? ORDER BY sort_order",
                [pid],
            )
        ]
        return pack_from_dict(
            {
                "pack": {
                    "id": pid,
                    "name": name,
                    "version": version,
                    "description": description,
                    "source": source,
                    "provenance_values": json.loads(prov or "[]"),
                },
                "domains": domains,
                "common_attributes": common,
                "element_types": element_types,
                "relationship_types": relationship_types,
            }
        )

    def list_packs(self) -> list[dict[str, Any]]:
        df = self._fetch_df("SELECT pack_id, name, version, loaded_at FROM meta_pack ORDER BY loaded_at DESC")
        return df.to_dict("records")

    # ----------------------------------------------------------- elements
    @staticmethod
    def _row_to_element(row: tuple) -> Element:
        d = dict(zip(ELEMENT_COLUMNS, row, strict=True))
        return Element(
            element_id=d["element_id"],
            type_id=d["type_id"],
            key=d["key"] or "",
            name=d["name"],
            description_md=d["description_md"] or "",
            status=d["status"],
            lifecycle_status=d["lifecycle_status"] or "",
            source_system=d["source_system"] or "",
            source_ref=d["source_ref"] or "",
            external_ids=_loads(d["external_ids"]),
            attrs=_loads(d["attrs"]),
            origin=d["origin"] or "",
            version=int(d["_version"]),
            created_at=d["created_at"],
            created_by=d["created_by"] or "",
            updated_at=d["updated_at"],
            updated_by=d["updated_by"] or "",
        )

    def _element_values(self, e: Element) -> list[Any]:
        return [
            e.element_id,
            e.type_id,
            e.key or None,
            e.name,
            e.description_md or None,
            e.status,
            e.lifecycle_status or None,
            e.source_system or None,
            e.source_ref or None,
            _dumps(e.external_ids),
            _dumps(e.attrs),
            e.origin or None,
            e.version,
            e.created_at,
            e.created_by or None,
            e.updated_at,
            e.updated_by or None,
        ]

    def get_element(self, element_id: str) -> Element | None:
        rows = self._fetch_all(
            f"SELECT {', '.join(ELEMENT_COLUMNS)} FROM element WHERE element_id = ?", [element_id]
        )
        if not rows:
            return None
        e = self._row_to_element(rows[0])
        e.links = self.get_links(element_id)
        return e

    def _where(
        self, text: str | None, type_id: str | list[str] | None, status: str | None
    ) -> tuple[str, list[Any]]:
        clauses, params = [], []
        if text:
            like = f"%{text}%"
            clauses.append("(name ILIKE ? OR key ILIKE ? OR element_id ILIKE ? OR description_md ILIKE ?)")
            params += [like, like, like, like]
        if type_id:
            ids = [type_id] if isinstance(type_id, str) else list(type_id)
            clauses.append(f"type_id IN ({', '.join('?' for _ in ids)})")
            params += ids
        if status:
            clauses.append("status = ?")
            params.append(status)
        return (" WHERE " + " AND ".join(clauses)) if clauses else "", params

    def find_elements(
        self, text=None, type_id=None, status=None, limit: int = 200, offset: int = 0
    ) -> list[Element]:
        where, params = self._where(text, type_id, status)
        rows = self._fetch_all(
            f"SELECT {', '.join(ELEMENT_COLUMNS)} FROM element{where} ORDER BY name, element_id LIMIT ? OFFSET ?",
            params + [limit, offset],
        )
        return [self._row_to_element(r) for r in rows]

    def count_elements(self, type_id=None, text=None) -> int:
        where, params = self._where(text, type_id, None)
        return int(self._fetch_all(f"SELECT COUNT(*) FROM element{where}", params)[0][0])

    def count_by_type(self) -> dict[str, int]:
        return {
            t: int(n)
            for t, n in self._fetch_all(
                "SELECT type_id, COUNT(*) FROM element GROUP BY type_id ORDER BY 2 DESC"
            )
        }

    def insert_element(self, element: Element, actor: str) -> Element:
        if self.get_element(element.element_id):
            raise ConflictError(f"element {element.element_id} already exists")
        now = _now()
        element.version = 1
        element.created_at, element.created_by, element.updated_at, element.updated_by = (
            now,
            actor,
            now,
            actor,
        )
        with self._lock:
            self._execute(
                f"INSERT INTO element VALUES ({', '.join('?' for _ in ELEMENT_COLUMNS)})",
                self._element_values(element),
            )
            self._log("element", element.element_id, "insert", actor, None, self._public(element), 1)
        return element

    def update_element(self, element: Element, actor: str, expected_version: int | None = None) -> Element:
        current = self.get_element(element.element_id)
        if current is None:
            raise NotFoundError(element.element_id)
        expected = expected_version if expected_version is not None else element.version
        if current.version != expected:
            raise ConflictError(
                f"element {element.element_id} changed by {current.updated_by} at {current.updated_at} (version {current.version}, you had {expected})"
            )
        element.version = current.version + 1
        element.created_at, element.created_by = current.created_at, current.created_by
        element.updated_at, element.updated_by = _now(), actor
        with self._lock:
            self._execute(
                "UPDATE element SET type_id=?, key=?, name=?, description_md=?, status=?, lifecycle_status=?, source_system=?, "
                "source_ref=?, external_ids=?, attrs=?, origin=?, _version=?, updated_at=?, updated_by=? WHERE element_id=? AND _version=?",
                [
                    element.type_id,
                    element.key or None,
                    element.name,
                    element.description_md or None,
                    element.status,
                    element.lifecycle_status or None,
                    element.source_system or None,
                    element.source_ref or None,
                    _dumps(element.external_ids),
                    _dumps(element.attrs),
                    element.origin or None,
                    element.version,
                    element.updated_at,
                    element.updated_by,
                    element.element_id,
                    current.version,
                ],
            )
            self._log(
                "element",
                element.element_id,
                "update",
                actor,
                self._public(current),
                self._public(element),
                element.version,
            )
        return element

    @staticmethod
    def _public(e: Element | Relationship) -> dict[str, Any]:
        d = dict(vars(e))
        d.pop("links", None)
        for k in ("created_at", "updated_at"):
            d[k] = str(d[k]) if d.get(k) else None
        return d

    def upsert_elements(self, elements: list[Element], actor: str) -> tuple[int, int]:
        if not elements:
            return 0, 0
        now = _now()
        ids = [e.element_id for e in elements]
        existing: dict[str, tuple] = {}
        for i in range(0, len(ids), 500):
            chunk = ids[i : i + 500]
            for eid, created_at, created_by, version in self._fetch_all(
                f"SELECT element_id, created_at, created_by, _version FROM element WHERE element_id IN ({', '.join('?' for _ in chunk)})",
                chunk,
            ):
                existing[eid] = (created_at, created_by, version)
        rows = []
        for e in elements:
            if e.element_id in existing:
                created_at, created_by, version = existing[e.element_id]
                e.created_at, e.created_by, e.version = created_at, created_by, int(version) + 1
            else:
                e.created_at, e.created_by, e.version = now, actor, 1
            e.updated_at, e.updated_by = now, actor
            rows.append(self._element_values(e))
        df = pd.DataFrame(rows, columns=ELEMENT_COLUMNS)
        with self._lock:
            self._conn.register("_incoming_elements", df)
            self._execute(
                "DELETE FROM element WHERE element_id IN (SELECT element_id FROM _incoming_elements)"
            )
            self._execute(f"INSERT INTO element SELECT {', '.join(ELEMENT_COLUMNS)} FROM _incoming_elements")
            self._conn.unregister("_incoming_elements")
            inserted = len(elements) - len(existing)
            self._log(
                "import",
                actor,
                "upsert_elements",
                actor,
                None,
                {"inserted": inserted, "updated": len(existing)},
                None,
            )
        return inserted, len(existing)

    def set_links(self, element_id: str, links: list[Link], actor: str) -> list[Link]:
        with self._lock:
            self._execute("DELETE FROM element_link WHERE element_id = ?", [element_id])
            out = []
            for i, ln in enumerate(links):
                ln.link_id = ln.link_id or new_id("lnk")
                ln.element_id, ln.sort_order = element_id, i
                self._execute(
                    "INSERT INTO element_link VALUES (?, ?, ?, ?, ?)",
                    [ln.link_id, element_id, ln.url, ln.label or None, i],
                )
                out.append(ln)
        return out

    def get_links(self, element_id: str) -> list[Link]:
        return [
            Link(element_id=element_id, url=u, label=lb or "", link_id=lid, sort_order=so)
            for lid, u, lb, so in self._fetch_all(
                "SELECT link_id, url, label, sort_order FROM element_link WHERE element_id = ? ORDER BY sort_order",
                [element_id],
            )
        ]

    # ------------------------------------------------------ relationships
    @staticmethod
    def _row_to_rel(row: tuple) -> Relationship:
        d = dict(zip(RELATIONSHIP_COLUMNS, row, strict=True))
        return Relationship(
            relationship_id=d["relationship_id"],
            rel_type_id=d["rel_type_id"],
            src_id=d["src_id"],
            dst_id=d["dst_id"],
            qualifier=d["qualifier"] or "",
            attrs=_loads(d["attrs"]),
            status=d["status"],
            origin=d["origin"] or "",
            source_system=d["source_system"] or "",
            source_ref=d["source_ref"] or "",
            version=int(d["_version"]),
            created_at=d["created_at"],
            created_by=d["created_by"] or "",
            updated_at=d["updated_at"],
            updated_by=d["updated_by"] or "",
        )

    @staticmethod
    def _rel_values(r: Relationship) -> list[Any]:
        return [
            r.relationship_id,
            r.rel_type_id,
            r.src_id,
            r.dst_id,
            r.qualifier or None,
            _dumps(r.attrs),
            r.status,
            r.origin or None,
            r.source_system or None,
            r.source_ref or None,
            r.version,
            r.created_at,
            r.created_by or None,
            r.updated_at,
            r.updated_by or None,
        ]

    def get_relationship(self, relationship_id: str) -> Relationship | None:
        rows = self._fetch_all(
            f"SELECT {', '.join(RELATIONSHIP_COLUMNS)} FROM relationship WHERE relationship_id = ?",
            [relationship_id],
        )
        return self._row_to_rel(rows[0]) if rows else None

    def relationships_of(self, element_id: str, direction: str = "both") -> list[Relationship]:
        cond = {"out": "src_id = ?", "in": "dst_id = ?", "both": "(src_id = ? OR dst_id = ?)"}[direction]
        params = [element_id] if direction != "both" else [element_id, element_id]
        rows = self._fetch_all(
            f"SELECT {', '.join(RELATIONSHIP_COLUMNS)} FROM relationship WHERE {cond} AND status <> 'retired' ORDER BY rel_type_id, src_id, dst_id",
            params,
        )
        return [self._row_to_rel(r) for r in rows]

    def find_relationships(self, rel_type_id: str | None = None, limit: int = 500) -> list[Relationship]:
        where = " WHERE rel_type_id = ?" if rel_type_id else ""
        rows = self._fetch_all(
            f"SELECT {', '.join(RELATIONSHIP_COLUMNS)} FROM relationship{where} ORDER BY rel_type_id, src_id, dst_id LIMIT ?",
            ([rel_type_id] if rel_type_id else []) + [limit],
        )
        return [self._row_to_rel(r) for r in rows]

    def count_relationships(self, rel_type_id: str | None = None) -> int:
        where = " WHERE rel_type_id = ?" if rel_type_id else ""
        return int(
            self._fetch_all(
                f"SELECT COUNT(*) FROM relationship{where}", [rel_type_id] if rel_type_id else []
            )[0][0]
        )

    def count_by_rel_type(self) -> dict[str, int]:
        return {
            t: int(n)
            for t, n in self._fetch_all(
                "SELECT rel_type_id, COUNT(*) FROM relationship GROUP BY rel_type_id ORDER BY 2 DESC"
            )
        }

    def insert_relationship(self, rel: Relationship, actor: str) -> Relationship:
        if self.get_relationship(rel.relationship_id):
            raise ConflictError(f"relationship {rel.relationship_id} already exists")
        now = _now()
        rel.version = 1
        rel.created_at, rel.created_by, rel.updated_at, rel.updated_by = now, actor, now, actor
        with self._lock:
            self._execute(
                f"INSERT INTO relationship VALUES ({', '.join('?' for _ in RELATIONSHIP_COLUMNS)})",
                self._rel_values(rel),
            )
            self._log("relationship", rel.relationship_id, "insert", actor, None, self._public(rel), 1)
        return rel

    def update_relationship(
        self, rel: Relationship, actor: str, expected_version: int | None = None
    ) -> Relationship:
        current = self.get_relationship(rel.relationship_id)
        if current is None:
            raise NotFoundError(rel.relationship_id)
        expected = expected_version if expected_version is not None else rel.version
        if current.version != expected:
            raise ConflictError(
                f"relationship {rel.relationship_id} changed by {current.updated_by} at {current.updated_at}"
            )
        rel.version = current.version + 1
        rel.created_at, rel.created_by = current.created_at, current.created_by
        rel.updated_at, rel.updated_by = _now(), actor
        with self._lock:
            self._execute(
                "UPDATE relationship SET rel_type_id=?, src_id=?, dst_id=?, qualifier=?, attrs=?, status=?, origin=?, source_system=?, "
                "source_ref=?, _version=?, updated_at=?, updated_by=? WHERE relationship_id=? AND _version=?",
                [
                    rel.rel_type_id,
                    rel.src_id,
                    rel.dst_id,
                    rel.qualifier or None,
                    _dumps(rel.attrs),
                    rel.status,
                    rel.origin or None,
                    rel.source_system or None,
                    rel.source_ref or None,
                    rel.version,
                    rel.updated_at,
                    rel.updated_by,
                    rel.relationship_id,
                    current.version,
                ],
            )
            self._log(
                "relationship",
                rel.relationship_id,
                "update",
                actor,
                self._public(current),
                self._public(rel),
                rel.version,
            )
        return rel

    def delete_relationship(self, relationship_id: str, actor: str) -> None:
        current = self.get_relationship(relationship_id)
        if current is None:
            raise NotFoundError(relationship_id)
        with self._lock:
            self._execute("DELETE FROM relationship WHERE relationship_id = ?", [relationship_id])
            self._log(
                "relationship", relationship_id, "delete", actor, self._public(current), None, current.version
            )

    def upsert_relationships(self, rels: list[Relationship], actor: str) -> tuple[int, int]:
        if not rels:
            return 0, 0
        now = _now()
        ids = [r.relationship_id for r in rels]
        existing: dict[str, tuple] = {}
        for i in range(0, len(ids), 500):
            chunk = ids[i : i + 500]
            for rid, created_at, created_by, version in self._fetch_all(
                f"SELECT relationship_id, created_at, created_by, _version FROM relationship WHERE relationship_id IN ({', '.join('?' for _ in chunk)})",
                chunk,
            ):
                existing[rid] = (created_at, created_by, version)
        rows = []
        for r in rels:
            if r.relationship_id in existing:
                created_at, created_by, version = existing[r.relationship_id]
                r.created_at, r.created_by, r.version = created_at, created_by, int(version) + 1
            else:
                r.created_at, r.created_by, r.version = now, actor, 1
            r.updated_at, r.updated_by = now, actor
            rows.append(self._rel_values(r))
        df = pd.DataFrame(rows, columns=RELATIONSHIP_COLUMNS)
        with self._lock:
            self._conn.register("_incoming_rels", df)
            self._execute(
                "DELETE FROM relationship WHERE relationship_id IN (SELECT relationship_id FROM _incoming_rels)"
            )
            self._execute(
                f"INSERT INTO relationship SELECT {', '.join(RELATIONSHIP_COLUMNS)} FROM _incoming_rels"
            )
            self._conn.unregister("_incoming_rels")
            inserted = len(rels) - len(existing)
            self._log(
                "import",
                actor,
                "upsert_relationships",
                actor,
                None,
                {"inserted": inserted, "updated": len(existing)},
                None,
            )
        return inserted, len(existing)

    # -------------------------------------------------------------- graph
    def trace(self, element_id: str, direction: str = "out", max_depth: int = 5) -> list[dict[str, Any]]:
        sql = TRACE_OUT_SQL if direction == "out" else TRACE_IN_SQL
        df = self._fetch_df(sql, [element_id, element_id, element_id, max_depth])
        sep = ">" if direction == "out" else "<"
        out = []
        for row in df.itertuples(index=False):
            out.append(
                {
                    "element_id": row.node_id,
                    "depth": int(row.depth),
                    "path": row.path.split(sep),
                    "rel_path": row.rel_path.split(sep) if row.rel_path else [],
                    "direction": direction,
                }
            )
        return out

    def edges_frame(self) -> pd.DataFrame:
        return self._fetch_df(
            "SELECT src_id, dst_id, rel_type_id, qualifier, relationship_id FROM relationship WHERE status <> 'retired'"
        )

    # -------------------------------------------------------------- audit
    def history(self, entity_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        where = " WHERE entity_id = ?" if entity_id else ""
        df = self._fetch_df(
            f"SELECT change_id, entity_kind, entity_id, op, actor, changed_at, before_json, after_json, version FROM change_log{where} ORDER BY changed_at DESC LIMIT ?",
            ([entity_id] if entity_id else []) + [limit],
        )
        return df.to_dict("records")

    # ---------------------------------------------------------------- sql
    def query(self, sql: str, params: list[Any] | None = None, limit: int = 1000) -> pd.DataFrame:
        stripped = re.sub(r"--[^\n]*", "", sql).strip().rstrip(";").strip()
        if ";" in stripped or not _READ_ONLY_RE.match(stripped) or _FORBIDDEN_RE.search(stripped):
            raise ValueError("only a single read-only SELECT/WITH statement is allowed")
        return self._fetch_df(f"SELECT * FROM ({stripped}) AS q LIMIT {int(limit)}", params)
