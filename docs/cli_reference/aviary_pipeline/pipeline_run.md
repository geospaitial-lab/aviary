<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## `aviary pipeline run`

Run the pipeline.

### **USAGE**

```
aviary pipeline run [OPTIONS] CONFIG_PATH
```

### **ARGUMENTS**

- `CONFIG_PATH`: Path to the config file (env var: [`AVIARY_CONFIG_PATH`][AVIARY_CONFIG_PATH])

  [AVIARY_CONFIG_PATH]: ../environment_variables.md#aviary_config_path

### **OPTIONS**

- `-s, --set [TEXT]`: Configuration fields using key=value format
- `--log-path PATH`: Path to the log file (env var: [`AVIARY_LOG_PATH`][AVIARY_LOG_PATH])
- `--log-level TEXT`: Log level (env var: [`AVIARY_LOG_LEVEL`][AVIARY_LOG_LEVEL])
- `--help`: Show this message and exit.

  [AVIARY_LOG_PATH]: ../environment_variables.md#aviary_log_path
  [AVIARY_LOG_LEVEL]: ../environment_variables.md#aviary_log_level
