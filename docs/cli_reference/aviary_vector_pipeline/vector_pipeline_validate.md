<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## `aviary vector-pipeline validate`

Validate the config file.

### **USAGE**

=== "Default"

    ```
    aviary vector-pipeline validate [OPTIONS] CONFIG_PATH
    ```

=== "Alias"

    ```
    aviary vector validate [OPTIONS] CONFIG_PATH
    ```

### **ARGUMENTS**

- `CONFIG_PATH`: Path to the config file (env var: [`AVIARY_CONFIG_PATH`][AVIARY_CONFIG_PATH])

  [AVIARY_CONFIG_PATH]: ../environment_variables.md#aviary_config_path

### **OPTIONS**

- `-s, --set TEXT`: Configuration fields using key=value format
- `--help`: Show this message and exit.
