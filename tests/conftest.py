from __future__ import annotations

from pathlib import Path

import pytest

from ea.backend.duckdb_backend import DuckDBBackend
from ea.importer import import_directory
from ea.metamodel import Registry, load_pack
from ea.services import GraphService, RepositoryService

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "higher_education" / "metamodel.yaml"
SAMPLE = ROOT / "data" / "sample"


@pytest.fixture(scope="session")
def pack():
    return load_pack(PACK)


@pytest.fixture(scope="session")
def registry(pack):
    return Registry(pack)


@pytest.fixture
def backend(pack):
    b = DuckDBBackend(":memory:")
    b.save_pack(pack)
    yield b
    b.close()


@pytest.fixture
def loaded(backend, registry):
    report = import_directory(backend, registry, SAMPLE, "sample")
    assert report.ok, report.summary()
    return backend


@pytest.fixture
def repo(loaded, registry):
    return RepositoryService(loaded, registry)


@pytest.fixture
def graph(loaded, registry):
    return GraphService(loaded, registry)
