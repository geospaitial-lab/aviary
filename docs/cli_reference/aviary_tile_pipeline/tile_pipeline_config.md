## `aviary tile-pipeline config`

Show the configuration for a component.

### Usage

=== "Default"

    ```
    aviary tile-pipeline config [OPTIONS] COMPONENT
    ```

=== "Alias"

    ```
    aviary tile config [OPTIONS] COMPONENT
    ```

### Arguments

- `COMPONENT`: Component

### Options

- `-c, --copy`: Copy the configuration to the clipboard.
- `-l, --level INTEGER`: Indentation level - defaults to 0
- `-p, --package TEXT`: Package of the component - defaults to aviary
- `--plugins-dir-path PATH`: Path to the plugins directory (env var: `AVIARY_PLUGINS_DIR_PATH`)
- `--help`: Show this message and exit.
