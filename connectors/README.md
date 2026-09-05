# Bringing content in — the CSV contract and source mappings

The importer reads plain CSV files. Any source that can export a spreadsheet
can feed the repository; the builder decides how (a one-off export, a
scheduled job, a dbt exposure) and the mapping file says what the columns mean.

## The contract (no mapping needed)

Three kinds of file, matched by name: `*element*.csv`, `*relationship*.csv`,
`*link*.csv`. UTF-8, header row, one entity per row.

**elements.csv**

| column | meaning |
| ------ | ------- |
| `id` | stable identifier of the element in the source (used by relationships); becomes the element id |
| `type` | element type — the pack type id, its name or its plural (`Logical Data Component`, `logical_data_component`) |
| `name` | display name (required) |
| `key` | optional human key (e.g. `DT007`) |
| `description` | Markdown |
| `status` | `draft`, `approved` (default) or `retired` |
| `lifecycle_status` | free text from the source (`Live`, `Planned`, …) |
| `links` | URLs separated by `|` |
| `source_ref`, `origin` | optional provenance overrides |
| anything else | an attribute; declared attributes are typed from the pack, others are kept as text |

**relationships.csv**

| column | meaning |
| ------ | ------- |
| `src_id`, `dst_id` | element ids (must exist in this import or already in the store) |
| `rel_type` | relationship type id or its name as written in the pack (`encapsulates`, `is source for`); resolved against the two endpoint types, supertypes and `ANY` included |
| `qualifier` | role qualifier where the type declares one (`Data Steward`) |
| `status`, `source_ref` | optional |
| anything else | an attribute of the relationship |

**links.csv**: `element_id`, `url`, `label`.

## What validation does

Every row is checked against the loaded metamodel before anything is written:
unknown type (error, skipped), inactive type (warning, imported), missing name
or id (error), unknown or disallowed relationship (error, skipped — the message
lists what *is* allowed between the two types), qualifier issues (warning),
endpoints that do not exist (error, skipped). `ea validate DIR` runs the check
without loading; `ea import DIR` loads and prints the same report.

Re-importing the same files is safe: elements are matched by id and
relationships by (source, type, endpoints, qualifier), so a reload updates
rather than duplicates.

## Mappings

A mapping YAML adapts a source's headers and vocabulary to the contract; see
`connectors/tool-export/mapping.yaml`. Keys:

```yaml
source_system: ea-tool
files: {elements: ["*.csv"], relationships: ["*relationship*.csv"], links: []}
elements:
  type_from_filename: false        # true = one file per type, type = file name
  columns: {ID: id, Name: name}    # source header -> contract column
  type_names: {Definition: business_definition}   # source type label -> pack type id
  defaults: {status: approved}
  ignore_columns: [Categories]
relationships:
  columns: {Source ID: src_id, Relationship: rel_type, Target ID: dst_id, Role: qualifier}
  rel_names: {"is owner of": position__is_steward_of__information_asset}
```

Headers not listed under `columns` are normalised (`Lifecycle Status` ->
`lifecycle_status`) and treated as attributes.
