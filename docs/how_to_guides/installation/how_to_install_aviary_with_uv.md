## How to install aviary with uv
uv is a Python package and project manager. It aims to replace `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`,
`twine`, `virtualenv`, and more. It can also install and manage Python versions. For more information visit the [official uv website]

The followind steps assume that uv is installed. 
If you don't have uv installed, you can download the latest version from the [official uv website].
If you need help installing uv, you can refer to the [official uv installation guide].

  [official uv website]: https://docs.astral.sh/uv
  [official uv installation guide]: https://docs.astral.sh/uv/getting-started/installation


### CLI only

If you just need the CLI aviary can be installed with the `uv tool` command 

#### Step 1: Install aviary

To install the aviary CLI run: 

```console
uv tool install geospatial-lab-aviary[cli]
```

You can also specify a version like:

```console
uv tool install 'geospaitial-lab-aviary>=1.0.0b1'
```

There may be a warning about an entry missing in PATH. You can fix this by running

```console
uv tool update-shell
```

#### Step 2: Verify the installation

To verify that the package was installed successfully, you can run the following command:

```sh
aviary --version
```

### Adding aviary to a uv managed project

When you already use `uv` for your project as described in the [uv project docs],
you can add uv to the project with the following command:

```console
uv add geospaitial-lab-aviary
```

You can also specify a version like:

```console
uv add 'geospaitial-lab-aviary>=1.0.0b1'
```

  [uv project docs]: https://docs.astral.sh/uv/concepts/projects/

### Virtual environment
Follow along this step-by-step guide to install aviary using uv and a virtual environment.


#### Step 1: Set up a virtual environment

To create a virtual environment named `venv`, navigate to the directory where you want to install aviary
and run the command below:

```
uv venv venv --python 3.12
```

Note that uv will automatically download the specified python version if it is not available on your system.<br />
To use aviary, you need at least Python 3.10.

Next, activate the virtual environment by running the following command:

=== "Linux and macOS"

    ```
    source venv/bin/activate
    ```

=== "Windows"

    ```
    venv\Scripts\activate
    ```

If the virtual environment is activated successfully, you should see its name
(in this case, `venv`) in your command-line prompt.

---

#### Step 2: Install the package

Install the package using uv by running the command below:

```
uv pip install geospaitial-lab-aviary
```

---

#### Step 3: Verify the installation

To verify that the package was installed successfully, you can run the following command:

```
aviary --version
```
