## `aviary tile-pipeline init`

Initialize a config file.

### **USAGE**

=== "Default"

    ```
    aviary tile-pipeline init [OPTIONS] CONFIG_PATH
    ```

=== "Alias"

    ```
    aviary tile init [OPTIONS] CONFIG_PATH
    ```

### **ARGUMENTS**

- `CONFIG_PATH`: Path to the config file (env var: `AVIARY_CONFIG_PATH`)

### **OPTIONS**

- `-f, --force`: Force overwrite the config file if it already exists.
- `-t, --template [base]`: Template for the config file - defaults to base
- `--help`: Show this message and exit.
