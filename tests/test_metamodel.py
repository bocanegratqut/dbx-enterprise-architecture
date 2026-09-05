from __future__ import annotations

import pytest

from ea.metamodel import Registry, dump_pack, load_pack, pack_to_dict
from ea.metamodel.loader import pack_from_dict
from ea.models import ANY


def test_pack_loads_everything(pack):
    active = [t for t in pack.element_types if t.active]
    inactive = [t for t in pack.element_types if not t.active]
    assert len(active) == 27
    assert len(inactive) == 32
    assert len(pack.relationship_types) == 54
    assert {d.id for d in pack.domains} == {"information", "process", "integration", "enterprise"}
    assert all(t.deactivation_reason for t in inactive)


def test_supertypes_and_inheritance(registry: Registry):
    assert registry.ancestors("position") == ["position", "role"]
    assert registry.is_a("data_product", "product")
    assert registry.is_a("information_asset", ANY)
    # a relationship declared on the supertype applies to the sub-type
    ids = {r.id for r in registry.allowed_rel_types("organization_unit", "data_product")}
    assert "organization_unit__produces__product" in ids
    # ANY-targeted edges reach every type
    assert "business_definition__relates_to__any" in {
        r.id for r in registry.allowed_rel_types("business_definition", "process")
    }


def test_attributes_include_common_and_inherited(registry: Registry):
    names = [a.name for a in registry.attributes_for("information_asset")]
    assert "alias" in names  # common
    assert "confidentiality_risk_rating" in names  # own
    assert names.count("source") == 1


def test_resolve_type_by_name_plural_and_id(registry: Registry):
    assert registry.resolve_type("Logical Data Component").id == "logical_data_component"
    assert registry.resolve_type("logical data components").id == "logical_data_component"
    assert registry.resolve_type("logical_data_component").id == "logical_data_component"
    assert registry.resolve_type("Nope") is None


def test_resolve_relationship_by_name_and_inverse(registry: Registry):
    rt = registry.resolve_rel_type("owns", "position", "physical_application_component")
    assert rt.id == "position__owns__physical_application_component"
    rt = registry.resolve_rel_type("is encapsulated by", "logical_data_component", "data_entity")
    assert rt.id == "logical_data_component__encapsulates__data_entity"
    assert registry.resolve_rel_type("owns", "data_entity", "capability") is None


def test_validation_rules(registry: Registry):
    issues = registry.validate_element("attribute", {})
    assert any(i.code == "inactive_type" for i in issues)
    assert registry.validate_element("nope", {})[0].code == "unknown_type"
    issues = registry.validate_relationship(
        "position__is_steward_of__information_asset", "position", "information_asset", ""
    )
    assert any(i.code == "missing_qualifier" for i in issues)
    issues = registry.validate_relationship(
        "position__is_steward_of__information_asset", "position", "information_asset", "Chef"
    )
    assert any(i.code == "unknown_qualifier" for i in issues)
    issues = registry.validate_relationship(
        "logical_data_component__encapsulates__data_entity", "capability", "data_entity"
    )
    assert any(i.code == "disallowed_source" for i in issues)


def test_pack_round_trips_through_yaml(pack, tmp_path):
    out = tmp_path / "pack.yaml"
    dump_pack(pack, out)
    again = load_pack(out)
    assert pack_to_dict(again) == pack_to_dict(pack)


def test_pack_rejects_unknown_references():
    bad = {"pack": {"id": "x"}, "element_types": [{"id": "a", "supertype": "missing"}]}
    with pytest.raises(ValueError):
        Registry(pack_from_dict(bad))
