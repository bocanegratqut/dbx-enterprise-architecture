# Metamodel packs

A pack is the whole definition of an architecture framework as data: element
types, their attributes and supertypes, relationship types with the endpoint
types they allow, domains, provenance. The engine loads a pack into the
`meta_*` tables and everything else — validation, forms, the type graph, the
agent's vocabulary — follows from it. Changing the metamodel is editing this
file (or the Metamodel page) and reloading; no code or DDL changes.

`higher_education/` is an anonymised university metamodel, the first configuration. Further packs
(`archimate-3.2`, a generic university pack) land beside it with the same
shape.

## File shape (`metamodel.yaml`)

```yaml
pack: {id, name, version, description, source, provenance_values: [..]}
domains:
  - {id, name, description}
common_attributes:            # every element may carry these
  - {name, label, type, required, enum, description, sensitivity}
element_types:
  - id: information_asset     # [a-z][a-z0-9_]*
    name: Information Asset
    plural: Information Assets
    supertype: business_information   # optional; relationships on the supertype apply
    active: true                       # false keeps the type importable but flagged
    deactivation_reason: ...
    domain: information
    provenance: LOCAL                  # one of pack.provenance_values
    prefix: IA                         # for minted ids
    description: ...
    examples: [...]
    source_of_record: ...              # informational: where instances come from
    type_owner: ...
    instance_owner: ...
    attributes: [{name, label, type, required, enum, description, sensitivity}]
relationship_types:
  - id: logical_data_component__encapsulates__data_entity
    name: encapsulates
    inverse: is encapsulated by
    source: logical_data_component     # type id or ANY
    target: data_entity                # type id or ANY
    provenance: CORE_EA
    qualifiers: [Owner, Data Steward]  # optional role qualifier values
    diagrams: [information]            # which domain diagrams show it
    description: ...
    src_max: 1                         # optional cardinality hints
    dst_max: null
```

Attribute types: `string`, `text` (Markdown), `integer`, `number`, `boolean`,
`date`, `json`. A relationship declared on a supertype is allowed for all its
sub-types; `ANY` allows any element type.

## Notation (`notation:` on a domain or an element type)

How a type is drawn when a view is generated from the model. A flat map of
strings; a type without one inherits its supertype's, then its domain's, then
the engine's defaults. Nothing in the engine knows the values, so a framework
brings its own convention.

| Key | Meaning | Example |
| --- | ------- | ------- |
| `layer` | The ArchiMate layer that colours the node and orders it top to bottom: `motivation`, `strategy`, `business`, `application`, `technology`, `physical`, `implementation`, `other` | `application` |
| `glyph` | One character shown before the stereotype, as the architecture documents do | `▤` |
| `stereotype` | The word in guillemets: `«Data Object»` | `Data Object` |
| `archimate` | The ArchiMate 3 element the draw.io export uses for its stencil | `DataObject` |
| `shape` | Mermaid node shape: `rect`, `round`, `stadium`, `hex`, `cyl`, `subroutine`, `diamond`, `asym` | `rect` |
| `colour` | On a domain: the palette name the app uses for badges and legends (`blue`, `pink`, `yellow`, `gray`, `teal`, `grape`, …) | `blue` |
| `hex` | On a domain: the fill colour the graphs use for its elements | `#4dabf7` |

```yaml
domains:
  - id: information
    notation: {layer: application, glyph: '▤', stereotype: Data Object, archimate: DataObject, shape: rect}
element_types:
  - id: information_asset
    domain: information
    notation: {layer: business, glyph: '▤', stereotype: Business Object, archimate: BusinessObject, shape: rect}
```
