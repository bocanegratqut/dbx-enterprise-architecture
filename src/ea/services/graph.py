"""Graph questions: neighbourhoods, traces, impact — with names attached and a completeness footer."""

from __future__ import annotations

from typing import Any

import networkx as nx

from ea.backend.base import DatabaseBackend
from ea.metamodel.registry import Registry
from ea.models import Element, NotFoundError


class GraphService:
    def __init__(self, backend: DatabaseBackend, registry: Registry):
        self.backend = backend
        self.registry = registry
        self._graph: nx.DiGraph | None = None
        self._graph_key: tuple[int, int] | None = None

    # --------------------------------------------------------------- cache
    def invalidate(self) -> None:
        self._graph = None

    def graph(self) -> nx.DiGraph:
        """The whole graph in memory. An EA repository is thousands of nodes; rebuilding takes milliseconds."""
        key = (self.backend.count_elements(), self.backend.count_relationships())
        if self._graph is not None and self._graph_key == key:
            return self._graph
        g = nx.DiGraph()
        for e in self.backend.find_elements(limit=1_000_000):
            g.add_node(
                e.element_id,
                name=e.name,
                type_id=e.type_id,
                status=e.status,
                key=e.key,
                source=e.source_system or "",
            )
        for row in self.backend.edges_frame().itertuples(index=False):
            g.add_edge(
                row.src_id,
                row.dst_id,
                rel_type_id=row.rel_type_id,
                qualifier=row.qualifier
                if isinstance(row.qualifier, str)
                else "",  # NaN from the frame is not a qualifier
                relationship_id=row.relationship_id,
            )
        self._graph, self._graph_key = g, key
        return g

    # ------------------------------------------------------------ helpers
    def _node(self, element_id: str) -> dict[str, Any]:
        g = self.graph()
        if element_id not in g:
            e = self.backend.get_element(element_id)
            if e is None:
                raise NotFoundError(element_id)
            return self._element_dict(e)
        d = g.nodes[element_id]
        t = self.registry.get_type(d.get("type_id", ""))
        return {
            "element_id": element_id,
            "name": d.get("name"),
            "type_id": d.get("type_id"),
            "type_name": t.name if t else d.get("type_id"),
            "status": d.get("status"),
            "key": d.get("key", ""),
            "source": d.get("source", ""),
        }

    def _element_dict(self, e: Element) -> dict[str, Any]:
        t = self.registry.get_type(e.type_id)
        return {
            "element_id": e.element_id,
            "name": e.name,
            "type_id": e.type_id,
            "type_name": t.name if t else e.type_id,
            "status": e.status,
            "key": e.key,
            "source": e.source_system or "",
        }

    def _edge_dict(self, u: str, v: str, data: dict[str, Any]) -> dict[str, Any]:
        rt = self.registry.rel_types.get(data.get("rel_type_id", ""))
        label = rt.name if rt else data.get("rel_type_id")
        if data.get("qualifier"):
            label = f"{label} ({data['qualifier']})"
        return {
            "relationship_id": data.get("relationship_id"),
            "src_id": u,
            "dst_id": v,
            "rel_type_id": data.get("rel_type_id"),
            "label": label,
            "qualifier": data.get("qualifier", ""),
        }

    def node(self, element_id: str) -> dict[str, Any]:
        """One element as the graph knows it (raises NotFoundError)."""
        return self._node(element_id)

    def edges_among(self, ids: list[str]) -> list[dict[str, Any]]:
        """Every relationship whose both ends are in `ids`, as labelled edge dicts."""
        g = self.graph()
        keep = [i for i in ids if i in g]
        sub = g.subgraph(keep)
        return [self._edge_dict(u, v, d) for u, v, d in sub.edges(data=True)]

    # ----------------------------------------------------------- queries
    def neighbours(
        self, element_id: str, depth: int = 1, direction: str = "both", max_nodes: int = 300
    ) -> dict[str, Any]:
        g = self.graph()
        if element_id not in g:
            self._node(element_id)  # raises NotFoundError
            return {"centre": element_id, "nodes": [], "edges": [], "truncated": False}
        if direction == "out":
            reach = nx.single_source_shortest_path_length(g, element_id, cutoff=depth)
        elif direction == "in":
            reach = nx.single_source_shortest_path_length(g.reverse(copy=False), element_id, cutoff=depth)
        else:
            reach = nx.single_source_shortest_path_length(
                g.to_undirected(as_view=True), element_id, cutoff=depth
            )
        ordered = sorted(reach, key=lambda n: (reach[n], n))
        truncated = len(ordered) > max_nodes
        keep = set(ordered[:max_nodes])
        sub = g.subgraph(keep)
        nodes = [dict(self._node(n), depth=reach[n]) for n in sub.nodes]
        edges = [self._edge_dict(u, v, d) for u, v, d in sub.edges(data=True)]
        return {"centre": element_id, "nodes": nodes, "edges": edges, "truncated": truncated}

    def trace(
        self, element_id: str, direction: str = "out", max_depth: int = 5, rel_types: list[str] | None = None
    ) -> list[dict[str, Any]]:
        self._node(element_id)
        rows = self.backend.trace(element_id, direction, max_depth)
        wanted = set(rel_types or [])
        out = []
        for r in rows:
            if wanted and not set(r["rel_path"]) & wanted:
                continue
            node = self._node(r["element_id"])
            labels = []
            for rid in r["rel_path"]:
                rt = self.registry.rel_types.get(rid)
                labels.append(rt.name if rt else rid)
            out.append(
                dict(
                    node,
                    depth=r["depth"],
                    path=r["path"],
                    rel_path=r["rel_path"],
                    rel_labels=labels,
                    direction=direction,
                )
            )
        return out

    def impact(self, element_id: str, max_depth: int = 3) -> dict[str, Any]:
        """What depends on this element (incoming, upstream chain) and what it depends on (outgoing), with a completeness footer."""
        centre = self._node(element_id)
        upstream = self.trace(element_id, "in", max_depth)
        downstream = self.trace(element_id, "out", max_depth)
        by_type: dict[str, int] = {}
        for r in upstream + downstream:
            by_type[r["type_name"]] = by_type.get(r["type_name"], 0) + 1
        return {
            "element": centre,
            "upstream": upstream,
            "downstream": downstream,
            "by_type": dict(sorted(by_type.items(), key=lambda kv: -kv[1])),
            "completeness": self.completeness(centre["type_id"]),
        }

    def completeness(self, type_id: str) -> dict[str, Any]:
        """Which relationship types this element type could have, and how many instances exist for each — an honest footer for any impact answer."""
        by_rel = self.backend.count_by_rel_type()
        out_types, in_types = self.registry.rel_types_for_type(type_id)
        rows = []
        for r in sorted({x.id: x for x in out_types + in_types}.values(), key=lambda x: x.id):
            rows.append(
                {
                    "rel_type_id": r.id,
                    "name": r.name,
                    "source": r.source,
                    "target": r.target,
                    "instances": by_rel.get(r.id, 0),
                }
            )
        empty = [r["name"] + f" ({r['source']} -> {r['target']})" for r in rows if r["instances"] == 0]
        return {"declared": len(rows), "populated": len(rows) - len(empty), "empty": empty, "rows": rows}

    def cytoscape_elements(self, sub: dict[str, Any]) -> list[dict[str, Any]]:
        """The neighbourhood as dash-cytoscape elements."""
        out = []
        for n in sub["nodes"]:
            out.append(
                {
                    "data": {
                        "id": n["element_id"],
                        "label": n["name"],
                        "type_id": n["type_id"],
                        "type_name": n["type_name"],
                        "depth": n.get("depth", 0),
                        "centre": n["element_id"] == sub["centre"],
                    },
                    "classes": n["type_id"] + (" centre" if n["element_id"] == sub["centre"] else ""),
                }
            )
        for e in sub["edges"]:
            out.append(
                {
                    "data": {
                        "id": e["relationship_id"] or f"{e['src_id']}->{e['dst_id']}",
                        "source": e["src_id"],
                        "target": e["dst_id"],
                        "label": e["label"],
                        "rel_type_id": e["rel_type_id"],
                    }
                }
            )
        return out
