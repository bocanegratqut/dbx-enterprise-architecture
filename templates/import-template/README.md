# EA import template

Use these files as a starter for the no-mapping CSV contract used by the Import page and `uv run ea import`.

## Files

- `elements.csv` holds one row per architecture element.
- `relationships.csv` links those elements together.
- `links.csv` adds external reference URLs to elements.

Keep the header row. Replace the example identifiers and values with your source data, then upload the CSV files on the Import page or import the folder from the command line.

The full contract is documented in `connectors/README.md`.