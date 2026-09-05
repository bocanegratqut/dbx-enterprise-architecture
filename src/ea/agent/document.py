"""An agent answer composed into a document: the answer, the elements it names, generated views, and how it was answered.

The diagrams are built by the app from what the tools returned (and from the
views the model asked for through `propose_view`), never written by the model.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from ea.agent.agent import ID_RE, AgentResult, ToolCall
from ea.agent.tools import ToolBox
from ea.views import View, view_from_ids
from ea.views.mermaid import to_markdown, to_mermaid

MAX_VIEW_NODES = 40


@dataclass
class AnswerDocument:
    question: str
    answer: str
    views: list[View] = field(default_factory=list)
    elements: list[dict[str, Any]] = field(default_factory=list)
    grounded_ids: list[str] = field(default_factory=list)
    ungrounded_ids: list[str] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    provider: str = ""
    model: str = ""
    created_at: str = ""

    @property
    def title(self) -> str:
        return self.question.strip().rstrip("?") or "Question"

    def markdown(self) -> str:
        """The whole document as Markdown with Mermaid fences: renders in the app, on GitHub and in the archreator portal."""
        who = self.provider + (f" · {self.model}" if self.model else "")
        out = [
            f"# {self.title}",
            "",
            f"_Answered {self.created_at} by the architecture assistant ({who}). Every identifier comes from a "
            "tool result over the repository; the diagrams are generated from the model, not drawn._",
            "",
            "## Answer",
            "",
            self.answer.strip(),
            "",
        ]
        if self.elements:
            out += [
                "## Elements in this answer",
                "",
                "| ID | Element | Type | Status |",
                "| -- | ------- | ---- | ------ |",
            ]
            for e in self.elements:
                out.append(f"| `{e['id']}` | {e['name']} | {e['type_name']} | {e.get('status', '')} |")
            out.append("")
        for v in self.views:
            out.append(to_markdown(v))
        if self.ungrounded_ids:
            out += [
                "## Not found in the model",
                "",
                "These identifiers appear in the answer but no tool returned them; treat them as unverified: "
                + ", ".join(f"`{i}`" for i in self.ungrounded_ids),
                "",
            ]
        out += ["## How this was answered", ""]
        if self.tool_calls:
            for i, c in enumerate(self.tool_calls, 1):
                args = ", ".join(f"{k}={v!r}" for k, v in c.input.items())
                out.append(f"{i}. `{c.name}({args})`")
        else:
            out.append("No tools were called.")
        out.append("")
        return "\n".join(out)

    def blocks(self) -> list[tuple[str, str]]:
        """The document as alternating ('md', text) and ('mermaid', code) blocks, for a renderer that draws diagrams itself."""
        parts: list[tuple[str, str]] = []
        buf: list[str] = []
        in_fence = False
        fence: list[str] = []
        for line in self.markdown().split("\n"):
            if not in_fence and line.strip() == "```mermaid":
                in_fence, fence = True, []
                continue
            if in_fence and line.strip() == "```":
                parts.append(("md", "\n".join(buf)))
                buf = []
                parts.append(("mermaid", "\n".join(fence)))
                in_fence = False
                continue
            (fence if in_fence else buf).append(line)
        if buf:
            parts.append(("md", "\n".join(buf)))
        return parts


def _unique(ids: list[str]) -> list[str]:
    out: list[str] = []
    for i in ids:
        if i not in out:
            out.append(i)
    return out


def compose(question: str, result: AgentResult, toolbox: ToolBox) -> AnswerDocument:
    """Build the document for one answer from the result and what the toolbox saw during it."""
    graph, registry = toolbox.graph, toolbox.registry
    g = graph.graph()
    cited = [i for i in _unique(ID_RE.findall(result.answer)) if i in g]
    seen = sorted(i for i in toolbox.seen_ids if i in g)
    ungrounded = list(result.ungrounded_ids)
    grounded = [i for i in cited if i not in ungrounded]
    elements = []
    for i in grounded:
        d = graph.node(i)
        elements.append(
            {"id": i, "name": d["name"], "type_name": d["type_name"], "status": d.get("status", "")}
        )

    views: list[View] = []
    for req in toolbox.requested_views:
        ids = [i for i in _unique(list(req.get("element_ids") or [])) if i in g]
        if ids:
            views.append(
                view_from_ids(
                    registry, graph, ids, req.get("title") or "View", ids[:1], max_nodes=MAX_VIEW_NODES
                )
            )
    if not views:
        focus = [i for i in (ID_RE.findall(question) + grounded) if i in g][:1]
        ids = grounded if len(grounded) >= 2 else _unique(grounded + seen)
        if ids:
            views.append(
                view_from_ids(
                    registry,
                    graph,
                    ids,
                    "Elements in this answer",
                    focus or ids[:1],
                    max_nodes=MAX_VIEW_NODES,
                )
            )
    return AnswerDocument(
        question=question,
        answer=result.answer,
        views=views,
        elements=elements,
        grounded_ids=grounded,
        ungrounded_ids=ungrounded,
        tool_calls=list(result.tool_calls),
        provider=result.provider,
        model=result.model,
        created_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
    )


def first_view_mermaid(doc: AnswerDocument) -> str:
    return to_mermaid(doc.views[0]) if doc.views else ""


_SLUG = re.compile(r"[^A-Za-z0-9]+")


def slug(text: str, limit: int = 40) -> str:
    return (_SLUG.sub("-", text).strip("-").lower() or "answer")[:limit]
