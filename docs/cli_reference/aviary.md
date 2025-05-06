## `aviary`

Python Framework for tile-based processing of geospatial data

### **USAGE**

```
aviary [OPTIONS] COMMAND [ARGS]...
```

### **OPTIONS**

- `-q, --quiet`: Enable quiet mode. (env var: [`AVIARY_QUIET`][AVIARY_QUIET])
- `-v, --verbose`: Enable verbose mode. (env var: [`AVIARY_VERBOSE`][AVIARY_VERBOSE])
- `--version`: Show the version of the package and exit.
- `--help`: Show this message and exit.

  [AVIARY_QUIET]: environment_variables.md#aviary_quiet
  [AVIARY_VERBOSE]: environment_variables.md#aviary_verbose

### **GENERAL COMMANDS**

- [`components`][components]: Show the components.
- [`docs`][docs]: Open the documentation in a web browser.
- [`github`][github]: Open the GitHub repository in a web browser.
- [`plugins`][plugins]: Show the registered plugins.

  [components]: aviary_components.md
  [docs]: aviary_docs.md
  [github]: aviary_github.md
  [plugins]: aviary_plugins.md

### **PIPELINE COMMANDS**

- [`tile-pipeline`][tile-pipeline]: Subcommands for the tile pipeline (alias: [`tile`][tile-pipeline])
- [`tile`][tile-pipeline]: Subcommands for the tile pipeline

  [tile-pipeline]: aviary_tile_pipeline/tile_pipeline.md
