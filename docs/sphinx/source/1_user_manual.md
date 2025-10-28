

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

## Interactive parse, modify parsers and partial parsing

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

It is also possible to parse only a few of the command-line arguments, passing the remaining arguments on to another
script or program, using the {py:func}`~dataparsers.parse_known` function for this. It works much like {py:func}`~dataparsers.parse` except that it does not
produce an error when extra arguments are present. Instead, it returns a two item tuple containing the populated class
and the list of remaining argument strings:

```python
>>> @dataclass
... class Args:
...     foo: bool
...     bar: str
...
>>> parse_known(Args, ['--foo', '--badger', 'BAR', 'spam'])
(Args(foo=True, bar='BAR'), ['--badger', 'spam'])
```

All functions {py:func}`~dataparsers.parse`,  {py:func}`~dataparsers.make_parser` and {py:func}`~dataparsers.parse_known` accepts a `parser=...` keyword argument to modify an
existing parser:

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
exceptions) and some additional parameters. The [`default`](./2_available_functions.md#default) keyword argument used above makes the argument optional (i.e.,
passed with flags like `--bar`) except in some specific situations.

One parameter of [`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method) that are not possible to pass to {py:func}`~dataparsers.arg` is the [`dest`](./2_available_functions.md#dest) keyword argument. That's
because the name of the class attribute is determined by the [`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) field name. So, it is not allowed to pass the
[`dest`](./2_available_functions.md#dest) parameter.

The parameter [`type`](./2_available_functions.md#type) is one of the [`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method) parameters that is inferred from the [`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) field properties
when not present.

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
[`action`](./2_available_functions.md#action) parameter of the original [`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method) method. If the boolean field is created with no default value, the
flag is still automatically created and the default value of the parameter is set to `False` (this default value can be
modified by the keyword argument [`default_bool`](./2_available_functions.md#default-bool) of the {py:func}`~dataparsers.dataparser` decorator - see ["Default for booleans"](#default-for-booleans)):

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

```{note}
In v2.1, the introduction of 2 new keyword arguments for the {py:func}`~dataparsers.arg` function ([`group`](./2_available_functions.md#group) and
[`mutually_exclusive_group`](./2_available_functions.md#mutually-exclusive-group)) made it easier to specify groups and mutually exclusive groups at the class scope. See
["Argument groups using ](#argument-groups-using-classvar-v2-1)[`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar)".
```
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
the value is not passed as [`title`](./2_available_functions.md#title) to the original [`add_argument_group()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument_group) method (`None` is passed instead). This
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
Mutually exclusive argument groups do not support the [`title`](./2_available_functions.md#title) and [`description`](./2_available_functions.md#description) arguments of the
[`add_argument_group()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument_group) method. However, a mutually exclusive group can be added to an argument group that has a
[`title`](./2_available_functions.md#title) and [`description`](./2_available_functions.md#description). This is achieved by passing both [`group_title`](./2_available_functions.md#group-title) and [`mutually_exclusive_group_id`](./2_available_functions.md#mutually-exclusive-group-id)
parameters to the {py:func}`~dataparsers.arg` function. If there is a conflict (i.e., same mutually exclusive group and different group
titles), the mutually exclusive group takes precedence.
```
### Argument groups using [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar) (v2.1+)

Two new additional keyword arguments were introduced in v2.1 with functionality analogue to the previous parameters.

The [`group`](./2_available_functions.md#group) and [`mutually_exclusive_group`](./2_available_functions.md#mutually-exclusive-group) keyword arguments also accepts a predefined [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar), that can be
initialized using 2 new functions: {py:func}`~dataparsers.group` and {py:func}`~dataparsers.mutually_exclusive_group`:

```python
from typing import ClassVar
from dataclasses import dataclass
from dataparsers import arg, group

@dataclass
class Args:
    my_first_group: ClassVar = group()
    foo: str = arg(group=my_first_group)
    bar: str = arg(group=my_first_group)

    my_second_group: ClassVar = group()
    sam: str = arg(group=my_second_group)
    ham: str = arg(group=my_second_group)
```

Using [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar) names makes it even more easier to prevent typos when identifying groups inside the class. Moreover:
the functions {py:func}`~dataparsers.group` and {py:func}`~dataparsers.mutually_exclusive_group` accepts the keyword arguments [`title`](./2_available_functions.md#title), [`description`](./2_available_functions.md#description) and
[`required`](./2_available_functions.md#required), respectively, which helps to describe the groups without the need of the {py:func}`~dataparsers.dataparser` decorator:

```python
>>> @dataclass
... class Args:
...     my_first_group: ClassVar = group(title="Group1", description="First group description")
...     my_1st_exclusive_group: ClassVar = mutually_exclusive_group(required=False)
...     foo: str = arg(group=my_first_group, mutually_exclusive_group=my_1st_exclusive_group)
...     bar: str = arg(group=my_first_group, mutually_exclusive_group=my_1st_exclusive_group)
...     ...
...     my_second_group: ClassVar = group(title="Group2", description="Second group description")
...     my_2nd_exclusive_group: ClassVar = mutually_exclusive_group(required=True)
...     sam: str = arg(group=my_second_group, mutually_exclusive_group=my_2nd_exclusive_group)
...     ham: str = arg(group=my_second_group, mutually_exclusive_group=my_2nd_exclusive_group)
...
>>>
>>> make_parser(Args).print_help()
usage: [-h] [--foo FOO | --bar BAR] (--sam SAM | --ham HAM)

options:
  -h, --help  show this help message and exit

Group1:
  First group description

  --foo FOO
  --bar BAR

Group2:
  Second group description

  --sam SAM
  --ham HAM
```

OBS: The delimiter `( )` in the "usage" above indicates that the group is required, while the delimiter `[ ]` indicates
the optional status.

The [`group`](./2_available_functions.md#group) and [`mutually_exclusive_group`](./2_available_functions.md#mutually-exclusive-group) keyword arguments still accepts integers and strings, keeping the
functionality compatible with the previous version parameters. When strings are passed to the [`group`](./2_available_functions.md#group) keyword argument,
it is associated to the group title.

The [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar) defined with the functions {py:func}`~dataparsers.group` and {py:func}`~dataparsers.mutually_exclusive_group` are not populated at run time:

```python
>>> args = parse(Args, ['--sam', 'wise'])
>>> print(args)
Args(foo=None, bar=None, sam='wise', ham=None)
>>> args.my_first_group
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'Args' object has no attribute 'my_first_group'
```

### Parser-level defaults

Most of the time, the attributes of the object returned by {py:func}`~dataparsers.parse` will be fully determined by inspecting the
command-line arguments. However, there is the original [`argparse`](https://docs.python.org/3/library/argparse.html#module-argparse)'s [`set_defaults()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.set_defaults) method that allows some additional
attributes to be determined without any inspection of the command line to be added. This functionality can be reproduced
with the {py:func}`~dataparsers.default` function:

```python
>>> from dataparsers import parse, default
>>> @dataclass
... class Args:
...     foo: int
...     bar: int = default(42)
...     baz: str = default("badger")
...
>>> parse(Args, ["736"])
Args(foo=736, bar=42, baz='badger')
```

Parser-level defaults are the original
[recommended useful way to work with multiple sub-parsers](https://github.com/python/cpython/blob/main/Doc/library/argparse.rst#L1901-L1904).
See the {py:func}`~dataparsers.subparser` method in section ["Subparsers"](#subparsers-v2-1) for examples.

One obvious difference of using this {py:func}`~dataparsers.default` function in place of the original [`set_defaults()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.set_defaults) method is that this
function must be used for each argument separated.

## Parser specifications

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

```{note}
In v2.1, the introduction of 2 new functions ({py:func}`~dataparsers.group` and {py:func}`~dataparsers.mutually_exclusive_group`) and 2 new keyword
arguments for the {py:func}`~dataparsers.arg` function ([`group`](./2_available_functions.md#group) and [`mutually_exclusive_group`](./2_available_functions.md#mutually-exclusive-group)) made it easier to specify [`description`](./2_available_functions.md#description)
and [`required`](./2_available_functions.md#required) status of the groups at the class scope. These may be better than using the {py:func}`~dataparsers.dataparser` decorator.
See ["Argument groups using ](#argument-groups-using-classvar-v2-1)[`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar)".
```
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

A last additional parameter accepted by the {py:func}`~dataparsers.dataparser` decorator is the [`help_formatter`](./2_available_functions.md#help-formatter) function, which is used to
format the arguments help text, allowing the help formatting to be customized. This function must be defined accepting a
single `str` as first positional argument and returning the string formatted text, i.e., `(str) -> str`. When this
option is used, the [`formatter_class`](./2_available_functions.md#formatter-class) parameter passed to the [`ArgumentParser`](https://docs.python.org/3/library/argparse.html#argumentparser-objects) constructor is assumed to be
`RawDescriptionHelpFormatter`.

This project provides a built-in predefined function {py:func}`~dataparsers.write_help`, that can be used in the [`help_formatter`](./2_available_functions.md#help-formatter) option to
preserve new line breaks and add blank lines between parameters descriptions:

```python
>>> from dataparsers import arg, make_parser, dataparser, write_help
>>> @dataparser(help_formatter=write_help)
... class Args:
...     foo: str = arg(
...         default=12.5,
...         help='''This description is printed as written here.
...                 It preserves lines breaks.''',
...     )
...     bar: float = arg(
...         default=25.5,
...         help='''This description is also formatted by `write_help` and
...                 it is separated from the previous by a blank line.
...                 The parameter has default value of %(default)s.''',
...     )
...
>>>
>>> make_parser(Args).print_help()
usage: [-h] [--foo FOO] [--bar BAR]

options:
  -h, --help  show this help message and exit
  --foo FOO   This description is printed as written here.
              It preserves lines breaks.

  --bar BAR   This description is also formatted by `write_help` and
              it is separated from the previous by a blank line.
              The parameter has default value of 25.5.
```

## Subparsers (v2.1+)

To define subparsers (or [sub commands](https://docs.python.org/3/library/argparse.html#sub-commands)) use a [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar)
and initialize it with the function {py:func}`~dataparsers.subparser`. This function accepts all parameters of the original [`add_parser()`](https://github.com/python/cpython/blob/fc4599800778f9b130d5e336deadbdeb5bd3e5ee/Lib/argparse.py#L1221)
method, except for `name`: the name of the subparser will receive the [`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) field name.

To add an argument to the created subparser (instead of the main parser), use the [`subparser`](./2_available_functions.md#subparser) keyword argument of the
{py:func}`~dataparsers.arg` function and assign to it the previously created field:

```python
>>> from typing import ClassVar
>>> from dataparsers import dataparser, arg, subparser, parse
>>>
>>> @dataparser(prog="PROG")
... class Args:
...     foo: bool = arg(help="foo help")
...     ...
...     a: ClassVar = subparser(help="a help")
...     bar: int = arg(help="bar help", subparser=a)
...     ...
...     b: ClassVar = subparser(help="b help")
...     baz: str = arg(make_flag=True, choices="XYZ", help="baz help", subparser=b)
...
>>> parse(Args, ["a", "12"])
Args(foo=False, bar=12, baz=None)
>>> parse(Args, ["--foo", "b", "--baz", "Z"])
Args(foo=True, bar=None, baz='Z')
```

As in the original module, when a help message is requested from a subparser, only the help for that particular parser
will be printed. The help message will not include parent parser or sibling parser messages. A help message for each
subparser command, however, can be given by supplying the `help=...` argument to {py:func}`~dataparsers.subparser` as above:

```python
>>> parse(Args, ["--help"])
usage: PROG [-h] [--foo] {a,b} ...

positional arguments:
  {a,b}
    a         a help
    b         b help

options:
  -h, --help  show this help message and exit
  --foo       foo help

>>> parse(Args, ["a", "--help"])
usage: PROG a [-h] bar

positional arguments:
  bar         bar help

options:
  -h, --help  show this help message and exit

>>> parse(Args, ["b", "--help"])
usage: PROG b [-h] [--baz {X,Y,Z}]

options:
  -h, --help     show this help message and exit
  --baz {X,Y,Z}  baz help
```

The [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar) defined with the function {py:func}`~dataparsers.subparser` remains as a read-only class variable at run time (which is an
instance of type `SubParser`: a frozen [`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) with some fields):

```python
>>> args = parse(Args)
>>> args.a
SubParser(defaults=None, kwargs=mappingproxy({'help': 'a help'}))
>>> args.a.defaults="test"
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 4, in __setattr__
dataclasses.FrozenInstanceError: cannot assign to field 'defaults'
```

### Subparsers group

It is not necessary to create the "subparsers group" when creating subparsers: the group is automatically created.
However, if you want to explicitly pass information to the "subparsers group", then create a `str` field and initialize
it with the function {py:func}`~dataparsers.subparsers`. This function accepts all parameters of the original [`add_subparsers()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers) method
(except for [`dest`](./2_available_functions.md#dest), which automatically receives the [`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) field name):

```python
>>> @dataparser(prog="PROG")
... class Args:
...     foo: bool = arg(help="foo help")
...     subparsers_group: str = subparsers(help="sub-command help")
...     ...
...     a: ClassVar = subparser(help="a help")
...     bar: int = arg(help="bar help", subparser=a)
...     ...
...     b: ClassVar = subparser(help="b help")
...     baz: str = arg(make_flag=True, choices="XYZ", help="baz help", subparser=b)
```

Some possible keyword arguments highlighted in the original [`add_subparsers()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers) method are `title=...` and
`description=...`. When either is present, the subparser's commands will appear in their own group in the help output:

```python
>>> @dataclass
... class Args:
...     subparsers_group: str = subparsers(
...         title="subcommands",
...         description="valid subcommands",
...         help="additional help",
...     )
...     foo: ClassVar = subparser()
...     bar: ClassVar = subparser()
...
>>> parse(Args, ["-h"])
usage: [-h] {foo,bar} ...

options:
  -h, --help  show this help message and exit

subcommands:
  valid subcommands

  {foo,bar}   additional help
```

### Subparsers defaults

One additional keyword argument of the function {py:func}`~dataparsers.subparser` (i.e., beyond those of the the original [`add_parser()`](https://github.com/python/cpython/blob/fc4599800778f9b130d5e336deadbdeb5bd3e5ee/Lib/argparse.py#L1221)
method) is the [`defaults`](./2_available_functions.md#defaults) dictionary, which reproduce the functionality of the original [`set_defaults()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.set_defaults) method (or the
["main parser-level"](#parser-level-defaults) {py:func}`~dataparsers.default` function) for the created subparsers.

One caveat of using this functionality is that the function requires  the dictionary keys to be defined previously as a
main parser-level default field, with the {py:func}`~dataparsers.default` function:

```python
>>> @dataclass
... class Args:
...     foo: str = default()
...     bar: ClassVar = subparser(defaults=dict(foo="spam"))
...     baz: ClassVar = subparser(defaults=dict(foo="badger"))
...
>>> parse(Args, ['bar'])
Args(foo='spam')
>>> parse(Args, ['baz'])
Args(foo='badger')
```

Parser-level defaults with subparsers defaults are the original [`argparse`](https://docs.python.org/3/library/argparse.html#module-argparse)'s
[recommended way to handling multiple sub-parsers](https://github.com/python/cpython/blob/main/Doc/library/argparse.rst#L1901-L1904)
(see below).

### Handling sub-commands

Like in the original [`argparse`](https://docs.python.org/3/library/argparse.html#module-argparse) module, there are 2 possible ways to parse to subparsers: (1) Using parser-level
defaults and (2) using the subparser name.

#### 1. Using parser-level defaults

Parser-level defaults are the original effective way of handling sub-commands, combining the use of the {py:func}`~dataparsers.subparser`
function with the [`defaults`](./2_available_functions.md#defaults) keyword argument dictionary, so that each subparser knows which Python function it should
execute. For example:

```python
>>> from __future__ import annotations # necessary to annotate sub-command functions
>>> from typing import ClassVar, Callable
>>> from dataclasses import dataclass
>>> from dataparsers import arg, parse, subparser, default
>>>
>>> # sub-command functions
>>> def foo(args: Args):
...     print(args.x * args.y)
...
>>> def bar(args: Args):
...     print("((%s))" % args.z)
...
>>> @dataclass
... class Args:
...     func: Callable = default()
...     ...
...     # parser for the "foo" command
...     foo: ClassVar = subparser(defaults=dict(func=foo))
...     x: int = arg("-x", default=1, make_flag=False, subparser=foo)
...     y: float = arg(subparser=foo)
...     ...
...     # parser for the "bar" command
...     bar: ClassVar = subparser(defaults=dict(func=bar))
...     z: str = arg(subparser=bar)
...
>>> # parse the args and call whatever function was selected
>>> args = parse(Args, "foo 1 -x 2".split())
>>> args.func(args)
2.0
>>>
>>> # parse the args and call whatever function was selected
>>> args = parse(Args, "bar XYZYX".split())
>>> args.func(args)
((XYZYX))
```

This way, you can let {py:func}`~dataparsers.parse` do the job of calling the appropriate function after argument parsing is complete.
According to the [`argparse`](https://docs.python.org/3/library/argparse.html#module-argparse) documentation, [associating functions with actions like this is typically the easiest way to
handle the different actions for each of your subparsers](https://github.com/python/cpython/blob/main/Doc/library/argparse.rst#L1939-L1941).

#### 2. Using subparser name

If it is necessary to check the name of the subparser that was invoked, the `str` field "subparsers group" created with
the {py:func}`~dataparsers.subparsers` function will work:

```python
>>> from dataclasses import dataclass
>>> from dataparsers import arg, parse, subparser, subparsers
>>>
>>> @dataclass
... class Args:
...     ...
...     subparser_name: str = subparsers()
...     ...
...     s1: ClassVar = subparser()
...     x: str = arg("-x", make_flag=False, subparser=s1)
...     ...
...     s2: ClassVar = subparser()
...     y: str = arg(subparser=s2)
...
>>> parse(Args, ["s2", "frobble"])
Args(subparser_name='s2', x=None, y='frobble')
```

