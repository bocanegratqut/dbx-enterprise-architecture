from __future__ import annotations

import zipfile
from io import BytesIO

from ea.importer import import_directory
from ea.ui.pages.import_page import TEMPLATE_FILES, import_template_archive


def test_import_template_archive_contains_guidance_and_contract_files():
    with zipfile.ZipFile(BytesIO(import_template_archive())) as archive:
        assert archive.namelist() == list(TEMPLATE_FILES)
        assert archive.read("README.md").decode("utf-8").startswith("# EA import template")
        assert archive.read("elements.csv").decode("utf-8").splitlines()[0].startswith("id,type,name")
        assert (
            archive.read("relationships.csv")
            .decode("utf-8")
            .splitlines()[0]
            .startswith("src_id,rel_type,dst_id")
        )
        assert archive.read("links.csv").decode("utf-8").splitlines()[0] == "element_id,url,label"


def test_import_template_rows_validate_against_loaded_metamodel(backend, registry, tmp_path):
    with zipfile.ZipFile(BytesIO(import_template_archive())) as archive:
        archive.extractall(tmp_path)

    report = import_directory(backend, registry, tmp_path, "import-template", dry_run=True)

    assert report.ok
    assert report.elements_read == 2
    assert report.relationships_read == 1
    assert report.links_read == 2
    assert report.issues == []
