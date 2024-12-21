# Getting Started

## Installation

It is reccomended to install the package in a virtual environment.

```bash
python -m venv venv
source venv/bin/activate
```

Alternatively, you can also use [`conda`] or [`mamba`] to create a new environment.

```bash
conda create -n sunflare python=3.12
conda activate sunflare
```

The package is currently not available on PyPI. You'll have to install it from source by cloning the [repository]

```bash
git clone https://github.com/redsun-acquisition/sunflare.git
cd sunflare
pip install -e .
```

## Usage

### Building the documentation

You can build the documentation by running the following command:

```bash
cd docs
make html

# for windows
make.bat html
```

[conda]: https://docs.conda.io/en/latest/
[mamba]: https://mamba.readthedocs.io/en/latest/
[repository]: https://github.com/redsun-acquisition/sunflare
