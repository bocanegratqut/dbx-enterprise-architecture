from __future__ import annotations

from ea.backend.base import DatabaseBackend
from ea.config import Settings


def backend_from_settings(settings: Settings) -> DatabaseBackend:
    if settings.backend == "duckdb":
        from ea.backend.duckdb_backend import DuckDBBackend

        return DuckDBBackend(settings.db_path)
    if settings.backend == "databricks":
        raise NotImplementedError("the Databricks backend lands in a later initiative; use EA_BACKEND=duckdb")
    raise ValueError(f"unknown backend {settings.backend!r}")
