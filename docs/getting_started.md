# Getting Started

## Installation

It is reccomended to install the package in a virtual environment.


::::{tab-set}
:::{tab-item} uv (reccomended)
```{code-block} shell
uv venv --python 3.10
venv\Scripts\activate

# for Windows...
# ... command prompt
venv\Scripts\activate.bat

# ... powershell
venv\Scripts\Activate.ps1
```
:::

:::{tab-item} venv
```{code-block} shell
# python version depends
# on the globally installed python
python -m venv sunflare-env

venv\Scripts\activate

# for Windows...
# ... command prompt
venv\Scripts\activate.bat

# ... powershell
venv\Scripts\Activate.ps1
```
:::
:::{tab-item} conda
```{code-block} shell
conda create -n sunflare-env python=3.10
conda activate sunflare-env
```
:::
:::{tab-item} mamba
```{code-block} shell
mamba create -n sunflare-env python=3.10
mamba activate sunflare-env
```
:::
::::

You can install the package from [PyPI] or directly from the GitHub [repository].

::::{tab-set}
:::{tab-item} PyPI
```{code-block} shell
pip install -U sunflare

# ... or if you're using uv
uv pip install sunflare
```
:::
:::{tab-item} GitHub
```{code-block} shell
git clone https://github.com/redsun-acquisition/sunflare.git
cd sunflare
pip install -e .
```
:::
::::

## Usage from source

### Installing development dependencies

You can install the required development dependencies via [PEP-735](https://peps.python.org/pep-0735/) dependency groups.

::::{tab-set}
:::{tab-item} uv (reccomended)
```{code-block} shell
# dev dependencies 
# are automatically
# synchronized
uv sync
```
:::
:::{tab-item} pip
```{code-block} shell
pip install -e . --group dev
```
:::
::::

### Building the documentation

You can build the documentation by running the following command:

```bash
cd docs
make html

# for windows
make.bat html
```

And then open the `_build/html/index.html` file in your browser.

### Running tests

You can run the tests by running the following command:

```bash
pytest
```

You can also obtain a test coverage report by running the following command:

```bash
pytest --cov=sunflare --cov-report=html
```

`sunflare` provides a `noxfile.py` to run tests with `nox` on all the supported python versions; if you use `uv` you can run tests as follows:

```bash
# install nox globally...
uv tool install nox
# ... then run it in the project
nox -s tests
```

This will generate a `htmlcov` directory with the test coverage report, which you can open in your browser by opening the `index.html` file.

[conda]: https://docs.conda.io/en/latest/
[mamba]: https://mamba.readthedocs.io/en/latest/
[repository]: https://github.com/redsun-acquisition/sunflare
[pypi]: https://pypi.org/project/sunflare/
