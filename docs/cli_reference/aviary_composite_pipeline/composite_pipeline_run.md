<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## `aviary composite-pipeline run`

Run the composite pipeline.

### **USAGE**

=== "Default"

    ```
    aviary composite-pipeline run [OPTIONS] CONFIG_PATH
    ```

=== "Alias"

    ```
    aviary composite run [OPTIONS] CONFIG_PATH
    ```

### **ARGUMENTS**

- `CONFIG_PATH`: Path to the config file (env var: [`AVIARY_CONFIG_PATH`][AVIARY_CONFIG_PATH])

  [AVIARY_CONFIG_PATH]: ../environment_variables.md#aviary_config_path

### **OPTIONS**

- `-s, --set TEXT`: Configuration fields using key=value format
- `--log-path PATH`: Path to the log file (env var: [`AVIARY_LOG_PATH`][AVIARY_LOG_PATH])
- `--help`: Show this message and exit.

  [AVIARY_LOG_PATH]: ../environment_variables.md#aviary_log_path
