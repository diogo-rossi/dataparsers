# Formalities, features, benefits and drawbacks

This project basically consists of a simple module `dataparsers.py` with few
functions that allows to define typed arguments parsers in a single place, based
on `dataclasses`.

## Formalities

The main strategy of the module is based on the same approach of the
[package `datargs`](https://pypi.org/project/datargs/), which consists in using
the
[`metadata` attribute of the dataclass fields](https://docs.python.org/3/library/dataclasses.html#dataclasses.Field)
to store argument parameters. Some additional features of this project have
already been contributed back upstream.

There are a lot of alternative libraries out there that do similar things. The
[README file](https://github.com/roee30/datargs/blob/master/README.md) of the
[`datargs` repository](https://github.com/roee30/datargs) provides a good
[list for existing solutions and differences](https://github.com/roee30/datargs?tab=readme-ov-file#why-nots-and-design-choices).
I could also add to that list the libraries
[Python `fire`](https://github.com/google/python-fire) and the
[package `dargparser`](https://github.com/konstantinjdobler/dargparser), just to
give few examples.

## Features and benefits

Use this project if you want particular added features, such as:

- Support for argument groups and mutually exclusive argument groups
- Define all interface in one single place
- More control over the interface display
- More control over the argument flag `--` creation
- More similarity with `argparse` module
- More simplicity

The simplicity is mentioned because it is just a simple module
[`dataparsers.py`](https://github.com/Diogo-Rossi/dataparsers/blob/main/src/dataparsers/dataparsers.py)
that doesn't have any additional dependencies (it is pure Python) which can be
downloaded directly and placed in your CLI scripts folder to import from.

In deed, the module consists of a 320 lines
[IPython code cell region](https://docs.spyder-ide.org/current/panes/editor.html#code-cells)
(i.e., starts and ends with a `#%%` line comment block), that can also be placed
on top of your "single file" CLI script to directly distribute. The used names
are just the few
[provided functions](https://dataparsers.readthedocs.io/en/latest/2_available_functions.html),
the _stdlib_ imports, `Class` (a `TypeVar`) and `SubParser` (a frozen `dataclass`).

Additionally, this project also provides a
[stub file (`.pyi`)](https://github.com/Diogo-Rossi/dataparsers/blob/main/src/dataparsers/__init__.pyi)
that can be used by type checkers but, moreover, may be used by some code
editors to give helper documentation including the related docs of `argparse`
methods, which are also provided in this project's documentation, for
convenience. The stub file can be downloaded directly but it is installed with
the module by default.

## Drawbacks

Unlike the `datargs` package, `dataparsers` doesn't support:

- The library `attrs` (only works with pure python `dataclasses`)
- `Enum`s classes
- Complex types (Sequences, Optionals, and Literals)

If you want any of these features, use the
[package `datargs`](https://pypi.org/project/datargs/). If you need the added
features of `dataparsers`, use this module instead.
