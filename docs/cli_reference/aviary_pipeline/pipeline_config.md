<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## `aviary pipeline config`

Show the configuration for a component.

### **USAGE**

```
aviary pipeline config [OPTIONS] COMPONENT
```

### **ARGUMENTS**

- `COMPONENT`: Component

### **OPTIONS**

- `-c, --copy`: Copy the configuration to the clipboard.
- `-l, --level INTEGER`: Indentation level - defaults to 0
- `-p, --package TEXT`: Package of the component - defaults to aviary
- `--plugins-dir-path PATH`: Path to the plugins directory
(env var: [`AVIARY_PLUGINS_DIR_PATH`][AVIARY_PLUGINS_DIR_PATH])
- `--help`: Show this message and exit.

  [AVIARY_PLUGINS_DIR_PATH]: ../environment_variables.md#aviary_plugins_dir_path
