<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## `aviary tile-pipeline run`

Run the tile pipeline.

### **USAGE**

=== "Default"

    ```
    aviary tile-pipeline run [OPTIONS] CONFIG_PATH
    ```

=== "Alias"

    ```
    aviary tile run [OPTIONS] CONFIG_PATH
    ```

### **ARGUMENTS**

- `CONFIG_PATH`: Path to the config file (env var: [`AVIARY_CONFIG_PATH`][AVIARY_CONFIG_PATH])

  [AVIARY_CONFIG_PATH]: ../environment_variables.md#aviary_config_path

### **OPTIONS**

- `-s, --set TEXT`: Configuration fields using key=value format
- `--help`: Show this message and exit.
