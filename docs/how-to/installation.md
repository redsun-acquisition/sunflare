# Installation

This guide shows you how to install Sunflare in different environments.

## Create a Virtual Environment

It is recommended to install the package in a virtual environment.

=== "uv (recommended)"

    ```bash
    uv venv --python 3.10

    # For Linux/macOS
    source .venv/bin/activate

    # For Windows Command Prompt
    .venv\Scripts\activate.bat

    # For Windows PowerShell
    .venv\Scripts\Activate.ps1
    ```

=== "venv"

    ```bash
    # Python version depends on the globally installed Python
    python -m venv sunflare-env

    # For Linux/macOS
    source sunflare-env/bin/activate

    # For Windows Command Prompt
    sunflare-env\Scripts\activate.bat

    # For Windows PowerShell
    sunflare-env\Scripts\Activate.ps1
    ```

=== "conda"

    ```bash
    conda create -n sunflare-env python=3.10
    conda activate sunflare-env
    ```

=== "mamba"

    ```bash
    mamba create -n sunflare-env python=3.10
    mamba activate sunflare-env
    ```

## Install `sunflare`

You can install the package from [PyPI](https://pypi.org/project/sunflare/) or directly from the GitHub [repository](https://github.com/redsun-acquisition/sunflare).

=== "PyPI"

    ```bash
    uv pip install sunflare

    # ... or without uv
    pip install -U sunflare
    ```

=== "GitHub (Development)"

    ```bash
    git clone https://github.com/redsun-acquisition/sunflare.git
    cd sunflare

    uv sync

    # ... or without uv
    pip install -e .[dev]
    ```

## Install development dependencies

If you're contributing to Sunflare or want to run tests locally, install the development dependencies via [PEP-735](https://peps.python.org/pep-0735/) dependency groups.

=== "uv (recommended)"

    ```bash
    # Dev dependencies are automatically synchronized
    uv sync
    ```

=== "pip"

    ```bash
    pip install -e .[dev]
    ```

## Next steps

- [Build the documentation](build-docs.md)
- [Run tests](run-tests.md)
- [Check the tutorials](../tutorials/index.md) to get started with Sunflare
