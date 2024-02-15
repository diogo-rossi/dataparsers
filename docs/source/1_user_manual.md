
# User manual

`dataparsers` is a simple module that wrappers around [`argparse`](https://docs.python.org/3/library/argparse.html#module-argparse) to get command line argument
        parsers from [`dataclasses`](https://docs.python.org/3/library/dataclasses.html#module-dataclasses). It can create type checkable command line argument parsers using [`dataclasses`](https://docs.python.org/3/library/dataclasses.html#module-dataclasses), which are
        recognized by type checkers and can be used by autocomplete tools.

## Basic usage

Create a [`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) describing your command line interface, and call {py:func}`~dataparsers.parse` with the class:

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

The [`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) fields that have a "default" value are turned into optional arguments, while the non default fields will
be positional arguments.

The script can then be used in the same way as used with [`argparse`](https://docs.python.org/3/library/argparse.html#module-argparse):

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

## Interactive parse and modify existing parsers

It is possible to pass arguments in code, in the same way as the original [`parse_args()`](https://docs.python.org/3/library/argparse.html#the-parse-args-method) method:

```python
>>> parse(Args, ["newtest", "--bar", "32"])
Args(foo='newtest', bar=32)
```

To create a argument parser and not immediately parse the arguments (i.e., save it for later), use the {py:func}`~dataparsers.make_parser`
function:

```python
>>> parser = make_parser(Args)
```

Both functions {py:func}`~dataparsers.parse` and {py:func}`~dataparsers.make_parser` accepts a `parser=...` keyword argument to modify an existing parser:

```python
>>> from argparse import ArgumentParser
>>> prev_parser = ArgumentParser(description="Existing parser")
>>> parse(Args, ["-h"], parser=prev_parser)
usage: [-h] [--bar BAR] foo

Existing parser

positional arguments:
  foo

options:
  -h, --help  show this help message and exit
  --bar BAR
```

## Argument specification

To specify detailed information about each argument, call the {py:func}`~dataparsers.arg` function on the [`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) fields:

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

In general, the {py:func}`~dataparsers.arg` function accepts all parameters that are used in the original [`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method) method (with few
exceptions) and some additional parameters. The [`default`](./2_available_functions.md#default) keyword argument used above makes the argument optional
(i.e., passed with flags like `--bar`) except in some specific situations.

One parameter of [`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method) that are not possible to pass to {py:func}`~dataparsers.arg` is the [`dest`](./2_available_functions.md#dest) keyword argument. That's
because the name of the class attribute is determined by the [`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) field name. So, it is unnecessary to pass the
[`dest`](./2_available_functions.md#dest) parameter, since it doesn't makes sense in this situation.

The parameter [`type`](./2_available_functions.md#type) is another [`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method) parameter that are inferred from the [`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) field when not
present.

### Aliases

The first parameter of the the original [`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method) method is [`name_or_flags`](./2_available_functions.md#name-or-flags), which is a series of flags, or a
simple argument name. This parameter can be passed to {py:func}`~dataparsers.arg` function to define aliases for optional arguments:

```python
@dataclass
class Args:
    foo: str = arg(help="foo help")
    bar: int = arg("-b", default=42, help="bar help")

args = parse(Args)
```

In this case, it also creates automatically a `--` flag :

```sh
$ python prog.py -h
usage: prog.py [-h] [-b BAR] foo

positional arguments:
  foo                foo help

options:
  -h, --help         show this help message and exit
  -b BAR, --bar BAR  bar help
```

However, the parameter [`name_or_flags`](./2_available_functions.md#name-or-flags) **must be passed only with flags** (i.e., starting with `-` or `--`). That's because
doesn't make sense to pass a simple not flag name, since the simple name normally determines the class attribute's name,
which is already defined by the [`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) field name.

### Automatic flag creation

One situation where the [`default`](./2_available_functions.md#default) keyword argument does not automatically makes the argument optional (i.e., creating a
`--` flag) is when the parameter [`nargs`](./2_available_functions.md#nargs) is set equal to `?` or `*`. That's because this setting also allows that
positional arguments may use a [`default`](./2_available_functions.md#default) value in the original [`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method) method. So, the flags must be passed
explicitly to make the argument optional:

```python
@dataclass
class Args:
    bar: int = arg("--bar", default=42, nargs="?", help="bar help")
```

An alternative way to force the creation of the `--` flag from the field name is by passing the additional keyword
argument `make_flag=True`:

```python
@dataclass
class Args:
    bar: int = arg(default=42, nargs="?", help="bar help", make_flag=True)
```

Both formats above produces the same interface:

```sh
$ python prog.py -h
usage: prog.py [-h] [--bar [BAR]]

options:
  -h, --help   show this help message and exit
  --bar [BAR]  bar help
```

#### Avoiding automatic flag creation

When only single `-` flags are passed to the {py:func}`~dataparsers.arg` function, it also creates automatically a `--` flag from the
[`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) field name (as shown in the example of the ["Aliases"](#aliases) section). To prevent that from happening, pass
`make_flag=False`:

```python
@dataclass
class Args:
    bar: int = arg("-b", default=42, help="bar help", make_flag=False)

args = parse(Args)
```

Then, only the single `-` flags will be sent to the interface:

```sh
$ python prog.py -h
usage: prog.py [-h] [-b BAR]

options:
  -h, --help  show this help message and exit
  -b BAR      bar help
```

#### Booleans

Booleans attributes are always considered as flag arguments, using the `"store_true"` or `"store_false"` values for the
[`action`](./2_available_functions.md#action) parameter of the original [`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method) method. If the boolean [`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) field is created with no default
value, the flag is still automatically created and the default value for the parameter will be `False` (it's defaults
can be modified by the keyword argument [`default_bool`](./2_available_functions.md#default-bool) of the {py:func}`~dataparsers.dataparser` decorator - see ["Default for booleans"](#default-for-booleans)):

```python
>>> @dataclass
... class Args:
...     bar: bool
...
>>> make_parser(Args).print_help()
usage: [-h] [--bar]

options:
  -h, --help  show this help message and exit
  --bar
>>> parse(Args, [])
Args(bar=False)

```

#### Decoupling code from the command line interface

The automatic flag creation does not happen when `--` flags are already passed (unless it is forced by passing
`make_flag=True`):

```python
@dataclass
class Args:
    path: str = arg("-f", "--file-output", metavar="<filepath>", help="Text file to write output")

args = parse(Args)
print(args)
```

**This may be the most common case** when the intention is to decouple the command line interface from the class attribute
names:

```sh
$ python prog.py -h
usage: prog.py [-h] [-f <filepath>]

options:
  -h, --help            show this help message and exit
  -f <filepath>, --file-output <filepath>
                        Text file to write output
```

In this situation, the interface can be customized, and the flags are not related to the attribute names inside the
code:

```sh
$ python prog.py --file-output myfile.txt
Args(path='myfile.txt')
```

### Argument groups

Two important additional keyword arguments can be passed to the {py:func}`~dataparsers.arg` function to specify "argument groups":
[`group_title`](./2_available_functions.md#group-title) and [`mutually_exclusive_group_id`](./2_available_functions.md#mutually-exclusive-group-id).

#### Conceptual grouping

The [`group_title`](./2_available_functions.md#group-title) defines the title (or the ID) of the argument group in which the argument may be included. The titled
group will be created later, by the method [`add_argument_group()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument_group), which is used just to separate the arguments in
simple more appropriate conceptual groups:

```python
>>> @dataclass
... class Args:
...     foo: str = arg(group_title="Group1")
...     bar: str = arg(group_title="Group1")
...     sam: str = arg(group_title="Group2")
...     ham: str = arg(group_title="Group2")
...
>>> parser = make_parser(Args)
>>> parser.print_help()
usage: [-h] foo bar sam ham

options:
  -h, --help  show this help message and exit

Group1:
  foo
  bar

Group2:
  sam
  ham
```

Argument groups may have a [`description`](./2_available_functions.md#description) in addition to the name. To define the [`description`](./2_available_functions.md#description) of the argument group, see
the {py:func}`~dataparsers.dataparser` decorator, which allows to define options for the [`ArgumentParser`](https://docs.python.org/3/library/argparse.html#argumentparser-objects) object.

#### Mutual exclusion

The [`mutually_exclusive_group_id`](./2_available_functions.md#mutually-exclusive-group-id) defines the name (or the ID) of the mutually exclusive argument group in which the
argument may be included. The identified group will be created later, by the method [`add_mutually_exclusive_group()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_mutually_exclusive_group),
which is used in [`argparse`](https://docs.python.org/3/library/argparse.html#module-argparse) to create mutually exclusive arguments:

```python
>>> @dataclass
... class Args:
...     foo: str = arg(mutually_exclusive_group_id="my_group")
...     bar: str = arg(mutually_exclusive_group_id="my_group")
...
>>> parser = make_parser(Args)
>>> parser.print_help()
usage: [-h] [--foo FOO | --bar BAR]

options:
  -h, --help  show this help message and exit
  --foo FOO
  --bar BAR
```

With that, [`argparse`](https://docs.python.org/3/library/argparse.html#module-argparse) will make sure that only one of the arguments in the mutually exclusive group was present on the
command line:

```python
>>> parse(Args,['--foo','test','--bar','newtest'])
usage: [-h] [--foo FOO | --bar BAR]
: error: argument --bar: not allowed with argument --foo
```

```{note}
Mutually exclusive arguments are always optionals. If no flag is given, they will be created automatically from the
[`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) field names, regardless of the value of [`make_flag`](./2_available_functions.md#make-flag).
```
Mutually exclusive groups also accepts a [`required`](./2_available_functions.md#required) argument, to indicate that at least one of the mutually exclusive
arguments is required. To define the [`required`](./2_available_functions.md#required) status of the mutually exclusive argument group, see the {py:func}`~dataparsers.dataparser`
decorator.

#### Identifying argument groups

Both parameters [`group_title`](./2_available_functions.md#group-title) and [`mutually_exclusive_group_id`](./2_available_functions.md#mutually-exclusive-group-id) may be integers. This makes easier to prevent typos when
identifying the groups. For the [`group_title`](./2_available_functions.md#group-title) parameter, if an integer is given, it is used to identify the group, but
the value is not passed as `title` to the original [`add_argument_group()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument_group) method (`None` is passed instead). This
prevents the integer to be printed in the displayed help message:

```python
>>> @dataclass
... class Args:
...     foo: str = arg(group_title=1)
...     bar: str = arg(group_title=1)
...     sam: str = arg(group_title=2)
...     ham: str = arg(group_title=2)
...
>>>
>>> parser = make_parser(Args)
>>> parser.print_help()
usage: [-h] foo bar sam ham

options:
  -h, --help  show this help message and exit

  foo
  bar

  sam
  ham
```

```{note}
Mutually exclusive argument groups do not support the `title` and [`description`](./2_available_functions.md#description) arguments of the
[`add_argument_group()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument_group) method. However, a mutually exclusive group can be added to an argument group that has a
`title` and [`description`](./2_available_functions.md#description). This is achieved by passing both [`group_title`](./2_available_functions.md#group-title) and [`mutually_exclusive_group_id`](./2_available_functions.md#mutually-exclusive-group-id)
parameters to the {py:func}`~dataparsers.arg` function. If there is a conflict (i.e., same mutually exclusive group and different group
titles), the mutually exclusive group takes precedence.
```
##  Parser specifications

To specify detailed options to the created [`ArgumentParser`](https://docs.python.org/3/library/argparse.html#argumentparser-objects) object, use the {py:func}`~dataparsers.dataparser` decorator:
    
```python
>>> from dataparsers import dataparser, make_parser
>>> @dataparser(prog='MyProgram', description='A foo that bars')
... class Args:
...     ...
...
>>> make_parser(Args).print_help()
usage: MyProgram [-h]

A foo that bars

options:
  -h, --help  show this help message and exit
```

In general, the {py:func}`~dataparsers.dataparser` decorator accepts all parameters that are used in the original [`ArgumentParser`](https://docs.python.org/3/library/argparse.html#argumentparser-objects)
constructor, and some additional parameters. 

### Groups [`description`](./2_available_functions.md#description) and [`required`](./2_available_functions.md#required) status

Two important additional parameters accepted by the {py:func}`~dataparsers.dataparser` decorator are the dictionaries [`groups_descriptions`](./2_available_functions.md#groups-descriptions)
and [`required_mutually_exclusive_groups`](./2_available_functions.md#required-mutually-exclusive-groups), whose keys should match some value of the arguments [`group_title`](./2_available_functions.md#group-title) or
[`mutually_exclusive_group_id`](./2_available_functions.md#mutually-exclusive-group-id) passed to {py:func}`~dataparsers.arg` function (strings or integers) :

```python
>>> @dataparser(
...     groups_descriptions={"Group1": "1st group description", "Group2": "2nd group description"},
...     required_mutually_exclusive_groups={0: True, 1: False},
...     add_help=False,  # Disable automatic addition of `-h` or `--help` at the command line
... )
... class Args:
...     foo: str = arg(group_title="Group1", mutually_exclusive_group_id=0)
...     bar: int = arg(group_title="Group1", mutually_exclusive_group_id=0)
...     sam: bool = arg(group_title="Group2", mutually_exclusive_group_id=1)
...     ham: float = arg(group_title="Group2", mutually_exclusive_group_id=1)
...
>>> make_parser(Args).print_help()
usage: (--foo FOO | --bar BAR) [--sam | --ham HAM]

Group1:
  1st group description

  --foo FOO
  --bar BAR

Group2:
  2nd group description

  --sam
  --ham HAM
```

OBS: The delimiter `( )` in the "usage" above indicates that the group is required, while the delimiter `[ ]` indicates
the optional status.

### Default for booleans

Booleans atributes with no default field value (or without [`action`](./2_available_functions.md#action) and [`default`](./2_available_functions.md#default) keyword arguments passed to {py:func}`~dataparsers.arg`
function) will receive its default value determining `"store_const"` action defined by the additional parameter
[`default_bool`](./2_available_functions.md#default-bool) (which is defaults to `False`, i.e., `action="store_true"`):

```python
>>> @dataparser
... class Args:
...     foo: bool
...
>>> parse(Args, ["--foo"])
Args(foo=True)
>>>
>>> @dataparser(default_bool=True)
... class Args:
...     foo: bool = arg(help="Boolean value")
...
>>> parse(Args, ["--foo"])
Args(foo=False)
```

### Help formatter function

TODO

