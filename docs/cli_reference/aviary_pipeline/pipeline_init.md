<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## `aviary pipeline init`

Initialize a config file.

### **USAGE**

```
aviary pipeline init [OPTIONS] CONFIG_PATH
```

### **ARGUMENTS**

- `PIPELINE`: Pipeline
- `CONFIG_PATH`: Path to the config file (env var: [`AVIARY_CONFIG_PATH`][AVIARY_CONFIG_PATH])

  [AVIARY_CONFIG_PATH]: ../environment_variables.md#aviary_config_path

### **OPTIONS**

- `-f, --force`: Force overwrite the config file if it already exists.
- `-t, --template base`: Template for the config file - defaults to base
- `--help`: Show this message and exit.
