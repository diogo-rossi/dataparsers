# dataparsers

A simple module to wrap around `argparse` to get command line argument parsers from `dataclasses`.

## Installation

```bash
pip install dataparsers
```
## Basic usage

Create a `dataclass` describing your command line interface, and call `parse()` with the class:

```python
# prog.py
from dataclasses import dataclass
from dataparsers import parse

@dataclass
class Args:
    foo: str
    bar: int = 42

args = parse(Args)
print("Printing `args`:")
print(args)
```

The `dataclass` fields that have a "default" value are turned into optional arguments, while the non default fields will
be positional arguments.

The script can then be used in the same way as used with `argparse`:

```sh
$ python prog.py -h
usage: prog.py [-h] [--bar BAR] foo

positional arguments:
  foo

options:
  -h, --help  show this help message and exit
  --bar BAR
```

And the resulting type of `args` is `Args` (recognized by type checkers and autocompletes):

```sh
$ python prog.py test --bar 12
Printing `args`:
Args(foo='test', bar=12)
```

## Argument specification

To specify detailed information about each argument, call the `arg()` function on the `dataclass` fields:

```python
# prog.py
from dataclasses import dataclass
from dataparsers import parse, arg

@dataclass
class Args:
    foo: str = arg(help="foo help")
    bar: int = arg(default=42, help="bar help")

args = parse(Args)
```

It allows to customize the interface:

```sh
$ python prog.py -h
usage: prog.py [-h] [--bar BAR] foo

positional arguments:
  foo         foo help

options:
  -h, --help  show this help message and exit
  --bar BAR   bar help
```

In general, the `arg()` function accepts all parameters that are used in the original `add_argument()` method (with few
exceptions) and some additional parameters. The `default` keyword argument used above makes the argument optional
(i.e., passed with flags like `--bar`) except in some specific situations.

For more information, see the [documentation](https://dataparsers.readthedocs.io/en/latest/index.html).

# Formalities, features, benefits and drawbacks

TODO
