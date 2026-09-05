"""Answer documents: composed from an agent result, with generated views and the grounding record."""

from ea.agent import Agent
from ea.agent.document import compose, slug
from ea.agent.tools import ToolBox
from ea.config import Settings


def _agent(loaded, registry, repo, graph):
    settings = Settings.from_env()
    settings.agent_provider = "stub"
    return Agent(ToolBox(loaded, registry, repo, graph), settings)


def test_impact_question_becomes_a_document_with_a_view(loaded, registry, repo, graph):
    agent = _agent(loaded, registry, repo, graph)
    question = "What is the impact of changing DE-SRS-COURSE?"
    res = agent.ask(question)
    doc = compose(question, res, agent.toolbox)
    assert doc.views and doc.views[0].title.startswith("Impact of")
    assert "DE-SRS-COURSE" in doc.views[0].ids() and doc.views[0].focus_ids == ["DE-SRS-COURSE"]
    assert any(e["id"] == "DE-SRS-COURSE" for e in doc.elements)
    md = doc.markdown()
    assert md.startswith("# What is the impact of changing DE-SRS-COURSE")
    assert "```mermaid" in md and "## Elements in this answer" in md and "## How this was answered" in md
    assert "`impact(" in md and "`propose_view(" in md
    kinds = [k for k, _ in doc.blocks()]
    assert "mermaid" in kinds and kinds[0] == "md"
    assert not doc.ungrounded_ids


def test_detail_question_gets_a_relationship_view(loaded, registry, repo, graph):
    agent = _agent(loaded, registry, repo, graph)
    res = agent.ask("Who owns the Course Catalogue?")
    doc = compose("Who owns the Course Catalogue?", res, agent.toolbox)
    assert doc.views and len(doc.views[0].nodes) >= 2
    assert doc.views[0].title.endswith("and its relationships")


def test_propose_view_tool_filters_unknown_ids(loaded, registry, repo, graph):
    tb = ToolBox(loaded, registry, repo, graph)
    out = tb.tool_propose_view("x", ["LDC-CURR", "NOPE-1", "DE-SRS-COURSE"])
    assert out["accepted"] == ["LDC-CURR", "DE-SRS-COURSE"] and out["unknown"] == ["NOPE-1"]
    assert tb.requested_views[0]["element_ids"] == ["LDC-CURR", "DE-SRS-COURSE"]
    assert tb.tool_propose_view("y", ["NOPE"])["accepted"] == [] and len(tb.requested_views) == 1


def test_slug():
    assert slug("What is the impact of changing DE-SRS-COURSE?") == "what-is-the-impact-of-changing-de-srs-co"
