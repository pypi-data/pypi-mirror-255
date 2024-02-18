# **jldc**

Simplify using [JSON Lines](https://jsonlines.org/) files alongside 
[python dataclass](https://docs.python.org/3/library/dataclasses.html) ([PEP-557](https://peps.python.org/pep-0557/)) 
objects, with convenient one-line reads/writes.

![check code workflow](https://github.com/itsluketwist/jldc/actions/workflows/check.yaml/badge.svg)
![release workflow](https://github.com/itsluketwist/jldc/actions/workflows/release.yaml/badge.svg)

<div>
    <!-- badges from : https://shields.io/ -->
    <!-- logos available : https://simpleicons.org/ -->
    <a href="https://opensource.org/licenses/MIT">
        <img alt="MIT License" src="https://img.shields.io/badge/Licence-MIT-yellow?style=for-the-badge&logo=docs&logoColor=white" />
    </a>
    <a href="https://www.python.org/">
        <img alt="Python 3.10+" src="https://img.shields.io/badge/Python_3.10+-blue?style=for-the-badge&logo=python&logoColor=white" />
    </a>
    <a href="https://jsonlines.org/">
        <img alt="JSON Lines" src="https://img.shields.io/badge/JSON Lines-black?style=for-the-badge&logo=JSON&logoColor=white" />
    </a>
</div>

## *usage*

Import the library and save/load lists of dataclasses or dictionaries with a single line.

```python
from jldc.core import load_jsonl, save_jsonl
from dataclasses import dataclass


@dataclass
class Person:
    name: str
    age: int


save_jsonl("people.jsonl", [Person("Alice", 24), Person("Bob", 32)])

data = load_jsonl("people.jsonl", [Person])

print(data)
```

## *installation*

Install directly from GitHub, using pip:

```shell
pip install jldc
```

Use the `ml` extra to encode/decode the `numpy.ndarray` type:

```shell
pip install jldc[ml]
```

## *development*

Fork and clone the repository code:

```shell
git clone https://github.com/itsluketwist/jldc.git
```

Once cloned, install the package locally in a virtual environment:

```shell
python -m venv venv

. venv/bin/activate

pip install -e ".[dev,ml]"
```

Install and use pre-commit to ensure code is in a good state:

```shell
pre-commit install

pre-commit autoupdate

pre-commit run --all-files
```

## *testing*

Run the test suite using:

```shell
pytest .
```
