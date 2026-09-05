"""Portable DDL. One schema, two engines: DuckDB locally, Delta on Databricks.

Types are kept to the intersection both understand. JSON is stored as text and
parsed in Python, which keeps the DDL identical and the rows readable from any
SQL client.
"""

META_TABLES = ["meta_pack", "meta_domain", "meta_element_type", "meta_attribute", "meta_relationship_type"]
CONTENT_TABLES = ["element", "relationship", "element_link", "change_log"]

# Columns added after a table first shipped. A backend applies them to an existing
# store on start-up (ADD COLUMN IF NOT EXISTS on DuckDB), so an older file keeps
# working. New columns go at the end because the inserts are positional.
MIGRATIONS: list[tuple[str, str, str]] = [
    ("meta_domain", "notation", "VARCHAR"),
    ("meta_element_type", "notation", "VARCHAR"),
]

DDL: dict[str, str] = {
    "meta_pack": """
        CREATE TABLE IF NOT EXISTS meta_pack (
            pack_id VARCHAR NOT NULL,
            name VARCHAR,
            version VARCHAR,
            description VARCHAR,
            source VARCHAR,
            provenance_values VARCHAR,
            loaded_at TIMESTAMP
        )""",
    "meta_domain": """
        CREATE TABLE IF NOT EXISTS meta_domain (
            pack_id VARCHAR NOT NULL,
            domain_id VARCHAR NOT NULL,
            name VARCHAR,
            description VARCHAR,
            sort_order INTEGER,
            notation VARCHAR
        )""",
    "meta_element_type": """
        CREATE TABLE IF NOT EXISTS meta_element_type (
            pack_id VARCHAR NOT NULL,
            type_id VARCHAR NOT NULL,
            name VARCHAR,
            plural VARCHAR,
            supertype_id VARCHAR,
            active BOOLEAN,
            deactivation_reason VARCHAR,
            domain_id VARCHAR,
            provenance VARCHAR,
            prefix VARCHAR,
            description VARCHAR,
            examples VARCHAR,
            source_of_record VARCHAR,
            type_owner VARCHAR,
            instance_owner VARCHAR,
            sort_order INTEGER,
            notation VARCHAR
        )""",
    "meta_attribute": """
        CREATE TABLE IF NOT EXISTS meta_attribute (
            pack_id VARCHAR NOT NULL,
            type_id VARCHAR,
            name VARCHAR NOT NULL,
            label VARCHAR,
            datatype VARCHAR,
            required BOOLEAN,
            enum_values VARCHAR,
            description VARCHAR,
            sensitivity VARCHAR,
            sort_order INTEGER
        )""",
    "meta_relationship_type": """
        CREATE TABLE IF NOT EXISTS meta_relationship_type (
            pack_id VARCHAR NOT NULL,
            rel_type_id VARCHAR NOT NULL,
            name VARCHAR,
            inverse_name VARCHAR,
            source_type_id VARCHAR,
            target_type_id VARCHAR,
            provenance VARCHAR,
            qualifiers VARCHAR,
            diagrams VARCHAR,
            description VARCHAR,
            src_max INTEGER,
            dst_max INTEGER,
            sort_order INTEGER
        )""",
    "element": """
        CREATE TABLE IF NOT EXISTS element (
            element_id VARCHAR NOT NULL,
            type_id VARCHAR NOT NULL,
            key VARCHAR,
            name VARCHAR NOT NULL,
            description_md VARCHAR,
            status VARCHAR NOT NULL,
            lifecycle_status VARCHAR,
            source_system VARCHAR,
            source_ref VARCHAR,
            external_ids VARCHAR,
            attrs VARCHAR,
            origin VARCHAR,
            _version INTEGER NOT NULL,
            created_at TIMESTAMP,
            created_by VARCHAR,
            updated_at TIMESTAMP,
            updated_by VARCHAR
        )""",
    "relationship": """
        CREATE TABLE IF NOT EXISTS relationship (
            relationship_id VARCHAR NOT NULL,
            rel_type_id VARCHAR NOT NULL,
            src_id VARCHAR NOT NULL,
            dst_id VARCHAR NOT NULL,
            qualifier VARCHAR,
            attrs VARCHAR,
            status VARCHAR NOT NULL,
            origin VARCHAR,
            source_system VARCHAR,
            source_ref VARCHAR,
            _version INTEGER NOT NULL,
            created_at TIMESTAMP,
            created_by VARCHAR,
            updated_at TIMESTAMP,
            updated_by VARCHAR
        )""",
    "element_link": """
        CREATE TABLE IF NOT EXISTS element_link (
            link_id VARCHAR NOT NULL,
            element_id VARCHAR NOT NULL,
            url VARCHAR NOT NULL,
            label VARCHAR,
            sort_order INTEGER
        )""",
    "change_log": """
        CREATE TABLE IF NOT EXISTS change_log (
            change_id VARCHAR NOT NULL,
            entity_kind VARCHAR NOT NULL,
            entity_id VARCHAR NOT NULL,
            op VARCHAR NOT NULL,
            actor VARCHAR,
            changed_at TIMESTAMP,
            before_json VARCHAR,
            after_json VARCHAR,
            version INTEGER
        )""",
}

ELEMENT_COLUMNS = [
    "element_id",
    "type_id",
    "key",
    "name",
    "description_md",
    "status",
    "lifecycle_status",
    "source_system",
    "source_ref",
    "external_ids",
    "attrs",
    "origin",
    "_version",
    "created_at",
    "created_by",
    "updated_at",
    "updated_by",
]
RELATIONSHIP_COLUMNS = [
    "relationship_id",
    "rel_type_id",
    "src_id",
    "dst_id",
    "qualifier",
    "attrs",
    "status",
    "origin",
    "source_system",
    "source_ref",
    "_version",
    "created_at",
    "created_by",
    "updated_at",
    "updated_by",
]

# Recursive traversal over the relationship table. Parameters: start id, max depth.
# `direction` is substituted by the backend: out = follow src->dst, in = dst->src.
TRACE_OUT_SQL = """
WITH RECURSIVE walk(start_id, node_id, depth, path, rel_path) AS (
    SELECT ?, ?, 0, CAST(? AS VARCHAR), CAST('' AS VARCHAR)
    UNION ALL
    SELECT w.start_id, r.dst_id, w.depth + 1,
           w.path || '>' || r.dst_id,
           CASE WHEN w.rel_path = '' THEN r.rel_type_id ELSE w.rel_path || '>' || r.rel_type_id END
    FROM walk w JOIN relationship r ON r.src_id = w.node_id
    WHERE w.depth < ? AND r.status <> 'retired' AND POSITION('>' || r.dst_id || '>' IN '>' || w.path || '>') = 0
)
SELECT node_id, MIN(depth) AS depth, MIN_BY(path, depth) AS path, MIN_BY(rel_path, depth) AS rel_path
FROM walk WHERE depth > 0 GROUP BY node_id ORDER BY depth, node_id
"""

TRACE_IN_SQL = """
WITH RECURSIVE walk(start_id, node_id, depth, path, rel_path) AS (
    SELECT ?, ?, 0, CAST(? AS VARCHAR), CAST('' AS VARCHAR)
    UNION ALL
    SELECT w.start_id, r.src_id, w.depth + 1,
           w.path || '<' || r.src_id,
           CASE WHEN w.rel_path = '' THEN r.rel_type_id ELSE w.rel_path || '<' || r.rel_type_id END
    FROM walk w JOIN relationship r ON r.dst_id = w.node_id
    WHERE w.depth < ? AND r.status <> 'retired' AND POSITION('<' || r.src_id || '<' IN '<' || w.path || '<') = 0
)
SELECT node_id, MIN(depth) AS depth, MIN_BY(path, depth) AS path, MIN_BY(rel_path, depth) AS rel_path
FROM walk WHERE depth > 0 GROUP BY node_id ORDER BY depth, node_id
"""
