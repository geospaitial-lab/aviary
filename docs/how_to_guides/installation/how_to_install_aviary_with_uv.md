## How to install aviary with uv

Follow along this step-by-step guide to install aviary using uv and a virtual environment.

### Step 1: Install uv

First, make sure you have uv installed.

If you don't have uv installed, you can download the latest version from the
[official uv website](https://docs.astral.sh/uv).
If you need help installing uv, you can refer to the
[official uv installation guide](https://docs.astral.sh/uv/getting-started/installation).

---

### Step 2: Set up a virtual environment

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

### Step 3: Install the package

Install the package using uv by running the command below:

```
uv pip install geospaitial-lab-aviary
```

---

### Step 4: Verify the installation

To verify that the package was installed successfully, you can run the following command:

```
aviary --version
```
