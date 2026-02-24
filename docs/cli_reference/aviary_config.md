<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## `aviary config`

Show the configuration of a component.

### **USAGE**

```
aviary config [OPTIONS] COMPONENT
```

### **ARGUMENTS**

- `COMPONENT`: Component

### **OPTIONS**

- `-c, --copy`: Copy the configuration to the clipboard.
- `-l, --level INTEGER`: Indentation level - defaults to 0
- `-p, --package TEXT`: Package of the component - defaults to aviary
- `--plugins-dir-path PATH`: Path to the plugins directory
(env var: [`AVIARY_PLUGINS_DIR_PATH`][AVIARY_PLUGINS_DIR_PATH])
- `-t, --type tile_fetcher | tiles_processor | vector_loader | vector_processor`: Type of the component - defaults to None
- `--help`: Show this message and exit.

  [AVIARY_PLUGINS_DIR_PATH]: environment_variables.md#aviary_plugins_dir_path
