## How to install aviary with pip

<span class="aviary-skill-level">Skill level: Beginner</span>

!!! abstract "TL;DR"
    Use `pip install geospaitial-lab-aviary` to install aviary.<br>
    To include the CLI, use `pip install geospaitial-lab-aviary[cli]`.

The most common and convenient way to install aviary is using pip – Python’s built-in package manager.

### Install Python

First, make sure Python 3.10, 3.11, or 3.12 is installed on your system.

Download Python from the
[official Python website :material-arrow-top-right:][official Python website].
If you need help, you can refer to the
[official Python installation guide :material-arrow-top-right:][official Python installation guide].

  [official Python website]: https://www.python.org
  [official Python installation guide]: https://wiki.python.org/moin/BeginnersGuide/Download

### Set up a virtual environment

It is considered best practice to use a virtual environment to install Python packages.
This keeps your project dependencies isolated.

Navigate to the directory where you want to install aviary and create a virtual environment.

```
python -m venv venv
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

### Install aviary

Install aviary using pip.

!!! warning
    aviary is currently released as a pre-release version.<br>
    To install the latest version, you need to explicitly specify its [version]:

    ```
    pip install geospaitial-lab-aviary==VERSION
    ```

  [version]: https://github.com/geospaitial-lab/aviary/releases

=== "Default"

    ```
    pip install geospaitial-lab-aviary
    ```

=== "+ CLI"

    ```
    pip install geospaitial-lab-aviary[cli]
    ```

=== "+ All"

    ```
    pip install geospaitial-lab-aviary[all]
    ```

Note that there are optional dependency groups:

- `cli`: Required for aviary’s CLI
- `all`: Includes optional dependencies, such as `cli`

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
