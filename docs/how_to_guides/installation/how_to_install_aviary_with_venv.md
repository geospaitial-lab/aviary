<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## How to install aviary with venv

Follow along this step-by-step guide to install aviary using a virtual environment.

### Step 1: Install Python

First, make sure you have Python installed.
Note that some operating systems come with Python pre-installed.
To verify this, launch your command-line interface and run the following command:

```
python --version
```

To use aviary, you need at least Python 3.10.

If you don't have Python installed or need to upgrade to a newer version,
you can download the latest version from the
[official Python website](https://www.python.org).
If you need help installing Python, you can refer to the
[official Python installation guide](https://wiki.python.org/moin/BeginnersGuide/Download).

### Step 2: Set up a virtual environment

It is considered best practice to use a virtual environment to install Python packages.
Note that this is not required, so you can skip this step if you prefer.
However, it is **strongly recommended** to use a virtual environment to avoid conflicts with other Python packages
and to keep your project dependencies isolated.

To create a virtual environment named *venv*, navigate to the directory where you want to install aviary
and run the command below:

```
python -m venv venv
```

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
(in this case, *venv*) in your command line prompt.

### Step 3: Install the package

Install the package using pip by running the command below:

```
pip install geospaitial-lab-aviary
```

### Step 4: Verify the installation

To verify that the package was installed successfully, you can run the following command:

```
aviary version
```
