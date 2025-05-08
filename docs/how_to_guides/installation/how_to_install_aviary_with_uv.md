## How to install aviary with uv

<span class="aviary-skill-level">Skill level: Beginner</span>

!!! abstract "TL;DR"
    todo

The recommended way to install aviary is using uv – a Python package and project manager
that simplifies the installation and management of Python packages, their dependencies, and even Python itself.

### Install uv

First, make sure uv is installed on your system.

Download uv from the
[official uv website :material-arrow-top-right:][official uv website].
If you need help, you can refer to the
[official uv installation guide :material-arrow-top-right:][official uv installation guide].

  [official uv website]: https://docs.astral.sh/uv
  [official uv installation guide]: https://docs.astral.sh/uv/getting-started/installation

### Install aviary

With uv, you can install aviary in different ways depending on your needs and preferences.

#### Install aviary using uv pip

uv includes a drop-in replacement for pip - Python’s built-in package manager -
so you can use it to install aviary just like you would with pip.

##### Set up a virtual environment

It is considered best practice to use a virtual environment to install Python packages.
This keeps your project dependencies isolated.

Navigate to the directory where you want to install aviary and create a virtual environment.

```
uv venv venv --python 3.12
```

Next, activate the virtual environment.

=== "Linux and macOS"

    ```
    source venv/bin/activate
    ```

=== "Windows"

    ```
    venv\Scripts\activate
    ```

Once activated, you should see its name – in this case, `venv` – in your terminal prompt.

##### Install aviary

Install aviary using uv pip.

=== "Default"

    ```
    uv pip install geospaitial-lab-aviary
    ```

=== "+ CLI"

    ```
    uv pip install geospaitial-lab-aviary[cli]
    ```

=== "+ All"

    ```
    uv pip install geospaitial-lab-aviary[all]
    ```

Note that there are optional dependency groups:

- `cli`: Required for aviary’s CLI
- `all`: Includes optional dependencies, such as `cli`

---

#### Install aviary using uv tool

In case you only need the CLI, aviary can be installed globally as a tool.

```
uv tool install geospaitial-lab-aviary[cli]
```

For more information, you can refer to the
[official uv tool documentation :material-arrow-top-right:][official uv tool documentation].

  [official uv tool documentation]: https://docs.astral.sh/uv/guides/tools

---

#### Install aviary using uv add

If you already use an uv-managed project, you can simply add aviary.

=== "Default"

    ```
    uv add geospaitial-lab-aviary
    ```

=== "+ CLI"

    ```
    uv add geospaitial-lab-aviary[cli]
    ```

=== "+ All"

    ```
    uv add geospaitial-lab-aviary[all]
    ```

Note that there are optional dependency groups:

- `cli`: Required for aviary’s CLI
- `all`: Includes optional dependencies, such as `cli`

For more information, you can refer to the
[official uv projects documentation :material-arrow-top-right:][official uv projects documentation].

  [official uv projects documentation]: https://docs.astral.sh/uv/guides/projects/

### Verify the installation

To verify that aviary was installed successfully, you can check the version.

=== "Python API"

    ``` python
    import aviary

    print(aviary.__version__)
    ```

=== "CLI"

    ```
    aviary --version
    ```

This shows the version of aviary.
