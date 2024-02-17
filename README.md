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

## Formalities, features, benefits and drawbacks

This project basically consists of a simple module [`dataparsers.py`]() with a
few functions that allows to define typed arguments parsers in a single place,
based on `dataclasses`.

## Formalities

The main strategy of the module is based on the same approach of the
[package `datargs`](https://pypi.org/project/datargs/), which consists in using
the
[`metadata` attribute of the dataclass fields](https://docs.python.org/3/library/dataclasses.html#dataclasses.Field)
to store argument parameters. Some additional features of this project have
already been contributed back upstream.

There are a lot of alternative libraries out there that do similar things. The
[README file](https://github.com/roee30/datargs/blob/master/README.md) of the
[`datargs` repository](https://github.com/roee30/datargs) provides a great
[list for existing solutions and differences](https://github.com/roee30/datargs?tab=readme-ov-file#why-nots-and-design-choices).
I could also add to that list the libraries
[Python `fire`](https://github.com/google/python-fire) and
[`dargparser`](https://github.com/konstantinjdobler/dargparser), just to give
few examples.

## Features and benefits

Use this project if you want particular added features, such as:

- More control over the interface display
- More control over the argument flag creation
- Support for argument groups and mutually exclusive argument groups
- More simplicity

The simplicity is mentioned because it is just a simple module
[`dataparsers.py`]() that doesn't have additional dependencies (it is pure
Python) which can be downloaded directly and placed in your CLI scripts folder
to import from.

In deed, the module consists of a 200 lines
[IPython code cell region](https://docs.spyder-ide.org/current/panes/editor.html#code-cells)
(which starts and ends with a `#%%` line comment block), that can also be placed
on top of your "single file" CLI script to directly distribute. The used names
are just the few [provided functions](./2_available_functions.md), the stdlib
imports and `Class` (a `TypeVar`)

Additionally, this project also provides a stub file [`dataparsers.pyi`] that
can be used by type checkers but, moreover, may be used by some code editors to
give helper documentation including the related docs of `argparse` methods,
which are also provided in this current documentation for convenience. The stub
can be downloaded directly but it is installed with the module by default.

## Drawbacks

Unlike the `datargs` package, `dataparsers` doesn't support:

- The library `attrs` (only works with pure python `dataclasses`)
- Enums
- Complex types (Sequences, Optionals, and Literals)
- Sub Commands (subparsers)

If you want any of these features, use the `datargs` package. If you need the
added features of `dataparsers`, use this module instead.
