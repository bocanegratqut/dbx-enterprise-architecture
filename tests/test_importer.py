from __future__ import annotations

from pathlib import Path

from ea.importer import Mapping, import_directory


def test_sample_loads_cleanly(loaded, registry):
    assert loaded.count_elements() == 45
    assert loaded.count_relationships() == 93
    assert loaded.get_element("LDC-CURR").attrs["level"] == 2
    assert loaded.get_element("DE-SRS-ENROLMENT").attrs["includes_pii"] is True
    assert [ln.url for ln in loaded.get_links("LDC-CURR")] == ["https://example.edu/bim/curriculum"]


def test_reimport_updates_not_duplicates(loaded, registry):
    report = import_directory(
        loaded, registry, Path(__file__).resolve().parents[1] / "data" / "sample", "sample"
    )
    assert report.ok
    assert loaded.count_elements() == 45 and loaded.count_relationships() == 93


def test_broken_files_are_reported(backend, registry, tmp_path):
    (tmp_path / "elements.csv").write_text(
        "id,type,name,description\n"
        "E1,Data Entity,Good entity,\n"
        "E2,Unknown Type,Bad type,\n"
        "E3,Data Entity,,\n"
        "E4,Attribute,An attribute,inactive type\n"
        "E5,Information Asset,Asset,\n"
    )
    (tmp_path / "relationships.csv").write_text(
        "src_id,rel_type,dst_id,qualifier\n"
        "E1,owns,E5,\n"  # no such relationship between these types
        "E1,processes,E9,\n"  # dangling
        "E5,is associated with,E1,\n"  # wrong target type for this name
    )
    report = import_directory(backend, registry, tmp_path, "test", dry_run=True)
    codes = {i.code for i in report.issues}
    assert {
        "unknown_type",
        "missing_name",
        "inactive_type",
        "unknown_relationship_type",
        "dangling_relationship",
    } <= codes
    assert not report.ok
    assert backend.count_elements() == 0  # dry run wrote nothing
    report = import_directory(backend, registry, tmp_path, "test")
    assert backend.count_elements() == 3  # E1, E4 (flagged), E5
    assert report.elements_skipped == 2


def test_mapping_renames_columns_and_types(backend, registry, tmp_path):
    (tmp_path / "objects.csv").write_text(
        "ID,Object Type,Name,Level of Logical Data Component\nDT007,Logical Data Component,Curriculum,2\n"
    )
    m = Mapping.from_dict(
        {
            "source_system": "ea-tool",
            "files": {"elements": ["objects.csv"]},
            "elements": {
                "columns": {
                    "ID": "id",
                    "Object Type": "type",
                    "Name": "name",
                    "Level of Logical Data Component": "level",
                }
            },
        }
    )
    report = import_directory(backend, registry, tmp_path, mapping=m)
    assert report.ok and report.source_system == "ea-tool"
    e = backend.get_element("DT007")
    assert e.type_id == "logical_data_component" and e.attrs["level"] == 2 and e.source_system == "ea-tool"
