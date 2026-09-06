"""Review before merge: request, approve per type, send back, and the merge gate."""

from __future__ import annotations

import pytest

from ea.backend.branching import use_branch
from ea.models import ConflictError, Forbidden
from ea.services import BranchService, RepositoryService, ReviewService, use_role


@pytest.fixture
def stack(loaded, registry):
    repo = RepositoryService(loaded, registry)
    branches = BranchService(loaded, registry)
    reviews = ReviewService(loaded, registry, branches)
    return loaded, repo, branches, reviews


def _draft(repo, branches, name="wp-review", author="arjun", entity="DE-CAW-PROP"):
    with use_role("architect"):
        b = branches.create(name, author)
        with use_branch(b.branch_id):
            cms = repo.element("PAC-CMS")
            repo.update_element("PAC-CMS", author, cms.version, target_state="change", target_note=name)
            repo.create_element(
                "data_entity",
                f"Proposal record {name}",
                author,
                element_id=entity,
                description_md="A proposed unit record.",
            )
            repo.add_relationship("processes", "PAC-CMS", entity, author)
    return b


def test_request_freezes_and_names_the_types(stack):
    loaded, repo, branches, reviews = stack
    b = _draft(repo, branches)
    with use_role("architect"):
        with pytest.raises(Forbidden):
            reviews.request(b.branch_id, "someone-else")
        reviews.request(b.branch_id, "arjun")
    assert branches.get(b.branch_id).status == "in_review"
    types = reviews.touched_types(b.branch_id)
    assert set(types) == {"physical_application_component", "data_entity"}
    reqs = reviews.requirements(b.branch_id)
    assert [r["approved"] for r in reqs] == [False, False]
    # frozen: nobody writes on it now, not even an admin
    with use_branch(b.branch_id):
        cms = repo.element("PAC-CMS")
        with pytest.raises(Forbidden):
            repo.update_element("PAC-CMS", "ada", cms.version, name="x")
    with use_role("architect"):
        with pytest.raises(ConflictError):
            reviews.request(b.branch_id, "arjun")  # already in review


def test_approval_per_type_by_assigned_reviewers(stack):
    loaded, repo, branches, reviews = stack
    reviews.set_assignment("data_entity", ["ia@example.edu"], "ada")
    reviews.set_assignment("physical_application_component", ["ea-app-stewards"], "ada")
    b = _draft(repo, branches)
    with use_role("architect"):
        reviews.request(b.branch_id, "arjun")
        with pytest.raises(Forbidden):
            reviews.approve(b.branch_id, "arjun")  # an architect is not a reviewer
    with use_role("reviewer"):
        with pytest.raises(Forbidden):
            reviews.approve(b.branch_id, "arjun")  # the author never approves
        with pytest.raises(Forbidden):
            reviews.approve(b.branch_id, "stranger@example.edu")  # assigned to nobody's types
        out = reviews.approve(b.branch_id, "ia@example.edu", comment="information types fine")
        assert out["approved_types"] == ["data_entity"] and out["pending"] == [
            "physical_application_component"
        ]
        assert branches.get(b.branch_id).status == "in_review"
        out = reviews.approve(b.branch_id, "steward@example.edu", groups=["ea-app-stewards"])
        assert out["complete"] and out["pending"] == []
    assert branches.get(b.branch_id).status == "approved"
    reqs = {r["type_id"]: r for r in reviews.requirements(b.branch_id)}
    assert reqs["data_entity"]["approved_by"] == ["ia@example.edu"]
    assert reqs["physical_application_component"]["approved_by"] == ["steward@example.edu"]
    assert len(reviews.reviews(b.branch_id)) == 2


def test_unassigned_types_take_any_reviewer_and_send_back_reopens(stack):
    loaded, repo, branches, reviews = stack
    b = _draft(repo, branches)
    with use_role("architect"):
        reviews.request(b.branch_id, "arjun")
    with use_role("reviewer"):
        with pytest.raises(ConflictError):
            reviews.send_back(b.branch_id, "rae", "")  # a send-back needs a comment
        reviews.send_back(b.branch_id, "rae", "the description of the proposal record is too thin")
    assert branches.get(b.branch_id).status == "open"
    with use_role("architect"), use_branch(b.branch_id):
        e = repo.element("DE-CAW-PROP")
        repo.update_element(
            "DE-CAW-PROP",
            "arjun",
            e.version,
            description_md="A proposed unit record with its outline and outcomes.",
        )
        reviews.request(b.branch_id, "arjun")
    with use_role("reviewer"):
        out = reviews.approve(b.branch_id, "rae")  # nobody assigned: any reviewer covers every type
        assert out["complete"]
    assert branches.get(b.branch_id).status == "approved"


def test_merge_asks_the_review(stack):
    loaded, repo, branches, reviews = stack
    b = _draft(repo, branches)
    with use_role("architect"):
        ok, why = reviews.can_merge(b.branch_id, "arjun")
        assert not ok and "approved" in why
        with pytest.raises(Forbidden):
            branches.merge(b.branch_id, "arjun")
        reviews.request(b.branch_id, "arjun")
    with use_role("reviewer"):
        reviews.approve(b.branch_id, "rae")
    with use_role("architect"):
        assert reviews.can_merge(b.branch_id, "arjun") == (True, "")
        res = branches.merge(b.branch_id, "arjun")
        assert res.closed and loaded.get_element("DE-CAW-PROP") is not None
    # an admin may merge an unreviewed branch, and the log says so
    b2 = _draft(repo, branches, "wp-admin", entity="DE-CAW-PROP-2")
    ok, why = reviews.can_merge(b2.branch_id, "ada")
    assert ok and "without a review" in why
    branches.merge(b2.branch_id, "ada")
    ops = [h["op"] for h in loaded.history(b2.branch_id)]
    assert "merge_without_review" in ops and "merge" in ops
    with use_role("reader"):
        assert reviews.can_merge(b2.branch_id, "ren")[0] is False
