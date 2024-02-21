"""
# dataparsers

A wrapper around `argparse` to get command line argument parsers from `dataclasses`.

## Basic usage

Create a `dataclass` describing your command line interface, and call `parse()` with the class::

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

The `dataclass` fields that have a "default" value are turned into optional arguments, while the non default fields will
be positional arguments.

The script can then be used in the same way as used with `argparse`::

    $ python prog.py -h
    usage: prog.py [-h] [--bar BAR] foo
    
    positional arguments:
      foo
    
    options:
      -h, --help  show this help message and exit
      --bar BAR

And the resulting type of `args` is `Args` (recognized by type checkers and autocompletes)::

    $ python prog.py test --bar 12
    Printing `args`:
    Args(foo='test', bar=12)

## Interactive parse and modify existing parsers

It is possible to pass arguments in code, in the same way as the original `parse_args()` method::

    >>> parse(Args, ["newtest", "--bar", "32"])
    Args(foo='newtest', bar=32)

To create a argument parser and not immediately parse the arguments (i.e., save it for later), use the `make_parser()`
function::

    >>> parser = make_parser(Args)

Both functions `parse()` and `make_parser()` accepts a `parser=...` keyword argument to modify an existing parser::

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

## Argument specification

To specify detailed information about each argument, call the `arg()` function on the `dataclass` fields::

    # prog.py
    from dataclasses import dataclass
    from dataparsers import parse, arg

    @dataclass
    class Args:
        foo: str = arg(help="foo help")
        bar: int = arg(default=42, help="bar help")

    args = parse(Args)

It allows to customize the interface::

    $ python prog.py -h
    usage: prog.py [-h] [--bar BAR] foo
    
    positional arguments:
      foo         foo help
    
    options:
      -h, --help  show this help message and exit
      --bar BAR   bar help

In general, the `arg()` function accepts all parameters that are used in the original `add_argument()` method (with few
exceptions) and some additional parameters. The `default` keyword argument used above makes the argument optional
(i.e., passed with flags like `--bar`) except in some specific situations.

One parameter of `add_argument()` that are not possible to pass to `arg()` is the `dest` keyword argument. That's
because the name of the class attribute is determined by the `dataclass` field name. So, it is unnecessary to pass the
`dest` parameter, since it doesn't makes sense in this situation.

The parameter `type` is another `add_argument()` parameter that are inferred from the `dataclass` field when not
present.

### Aliases

The first parameter of the the original `add_argument()` method is `name_or_flags`, which is a series of flags, or a
simple argument name. This parameter can be passed to `arg()` function to define aliases for optional arguments::

    @dataclass
    class Args:
        foo: str = arg(help="foo help")
        bar: int = arg("-b", default=42, help="bar help")

    args = parse(Args)

In this case, it also creates automatically a `--` flag ::

    $ python prog.py -h
    usage: prog.py [-h] [-b BAR] foo
    
    positional arguments:
      foo                foo help
    
    options:
      -h, --help         show this help message and exit
      -b BAR, --bar BAR  bar help

However, the parameter `name_or_flags` must be passed only with flags (i.e., starting with `-` or `--`). That's because
doesn't make sense to pass a simple not flag name, since the simple name normally determines the class attribute's name,
which is already defined by the `dataclass` field name.

### Automatic flag creation

One situation where the `default` keyword argument does not automatically makes the argument optional (i.e., creating a
`--` flag) is when the parameter `nargs` is set equal to `?` or `*`. That's because this setting also allows that
positional arguments may use a `default` value in the original `add_argument()` method. So, the flags must be passed
explicitly to make the argument optional::

    @dataclass
    class Args:
        bar: int = arg("--bar", default=42, nargs="?", help="bar help")

An alternative way to force the creation of the `--` flag from the field name is by passing the additional keyword
argument `make_flag=True`::

    @dataclass
    class Args:
        bar: int = arg(default=42, nargs="?", help="bar help", make_flag=True)

Both formats above produces the same interface::

    $ python prog.py -h
    usage: prog.py [-h] [--bar [BAR]]
    
    options:
      -h, --help   show this help message and exit
      --bar [BAR]  bar help

#### Avoiding automatic flag creation

When only single `-` flags are passed to the `arg()` function, it also creates automatically a `--` flag from the
`dataclass` field name (as shown in the example of the "Aliases" section). To prevent that from happening, pass
`make_flag=False`::

    @dataclass
    class Args:
        bar: int = arg("-b", default=42, help="bar help", make_flag=False)

    args = parse(Args)

Then, only the single `-` flags will be sent to the interface::

    $ python prog.py -h
    usage: prog.py [-h] [-b BAR]

    options:
      -h, --help  show this help message and exit
      -b BAR      bar help

#### Booleans

Booleans attributes are always considered as flag arguments, using the `"store_true"` or `"store_false"` values for the
`action` parameter of the original `add_argument()` method. If the boolean `dataclass` field is created with no default
value, the flag is still automatically created and the default value for the parameter will be `False` (it's defaults
can be modified by the keyword argument `default_bool` of the `dataparser()` decorator - see "Default for booleans")::

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


#### Decoupling code from the command line interface

The automatic flag creation does not happen when `--` flags are already passed (unless it is forced by passing
`make_flag=True`)::

    @dataclass
    class Args:
        path: str = arg("-f", "--file-output", metavar="<filepath>", help="Text file to write output")

    args = parse(Args)
    print(args)

This may be the most common case when the intention is to decouple the command line interface from the class attribute
names::

    $ python prog.py -h
    usage: prog.py [-h] [-f <filepath>]

    options:
      -h, --help            show this help message and exit
      -f <filepath>, --file-output <filepath>
                            Text file to write output 

In this situation, the interface can be customized, and the flags are not related to the attribute names inside the
code::

    $ python prog.py --file-output myfile.txt
    Args(path='myfile.txt')

### Argument groups

Two important additional keyword arguments can be passed to the `arg()` function to specify "argument groups":
`group_title` and `mutually_exclusive_group_id`.

#### Conceptual grouping

The `group_title` defines the title (or the ID) of the argument group in which the argument may be included. The titled
group will be created later, by the method `add_argument_group()`, which is used just to separate the arguments in
simple more appropriate conceptual groups::

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

Argument groups may have a `description` in addition to the name. To define the `description` of the argument group, see
the `dataparser()` decorator, which allows to define options for the `ArgumentParser` object.

#### Mutual exclusion

The `mutually_exclusive_group_id` defines the name (or the ID) of the mutually exclusive argument group in which the
argument may be included. The identified group will be created later, by the method `add_mutually_exclusive_group()`,
which is used in `argparse` to create mutually exclusive arguments::

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

With that, `argparse` will make sure that only one of the arguments in the mutually exclusive group was present on the
command line::

    >>> parse(Args,['--foo','test','--bar','newtest'])
    usage: [-h] [--foo FOO | --bar BAR]
    : error: argument --bar: not allowed with argument --foo

Note:
    Mutually exclusive arguments are always optionals. If no flag is given, they will be created automatically from the
    `dataclass` field names, regardless of the value of `make_flag`.

Mutually exclusive groups also accepts a `required` argument, to indicate that at least one of the mutually exclusive
arguments is required. To define the `required` status of the mutually exclusive argument group, see the `dataparser()`
decorator.

#### Identifying argument groups

Both parameters `group_title` and `mutually_exclusive_group_id` may be integers. This makes easier to prevent typos when
identifying the groups. For the `group_title` parameter, if an integer is given, it is used to identify the group, but
the value is not passed as `title` to the original `add_argument_group()` method (`None` is passed instead). This
prevents the integer to be printed in the displayed help message::

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

Note:
    Mutually exclusive argument groups do not support the `title` and `description` arguments of the
    `add_argument_group()` method. However, a mutually exclusive group can be added to an argument group that has a
    `title` and `description`. This is achieved by passing both `group_title` and `mutually_exclusive_group_id`
    parameters to the `arg()` function. If there is a conflict (i.e., same mutually exclusive group and different group
    titles), the mutually exclusive group takes precedence.

##  Parser specifications

To specify detailed options to the created `ArgumentParser` object, use the `dataparser()` decorator::
    
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

In general, the `dataparser()` decorator accepts all parameters that are used in the original `ArgumentParser`
constructor, and some additional parameters. 

### Groups `description` and `required` status

Two important additional parameters accepted by the `dataparser()` decorator are the dictionaries `groups_descriptions`
and `required_mutually_exclusive_groups`, whose keys should match some value of the arguments `group_title` or
`mutually_exclusive_group_id` passed to `arg()` function (strings or integers) ::

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

OBS: The delimiter `( )` in the "usage" above indicates that the group is required, while the delimiter `[ ]` indicates
the optional status.

### Default for booleans

Booleans atributes with no default field value (or without `action` and `default` keyword arguments passed to `arg()`
function) will receive its default value determining `"store_const"` action defined by the additional parameter
`default_bool` (which is defaults to `False`, i.e., `action="store_true"`)::

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

### Help formatter function

TODO

"""

from argparse import ArgumentParser, Action, FileType, HelpFormatter
from typing import Literal, TypeVar, Callable, Iterable, Sequence, Any, overload

T = TypeVar("T", covariant=True)

Class = TypeVar("Class", covariant=True)

def arg(
    *name_or_flags: str,
    group_title: str | int | None = None,
    mutually_exclusive_group_id: str | int | None = None,
    make_flag: bool | None = None,
    action: (
        Literal[
            "store",
            "store_const",
            "store_true",
            "store_false",
            "append",
            "append_const",
            "count",
            "help",
            "version",
            "extend",
        ]
        | type[Action]
    ) = "store",
    nargs: int | Literal["?", "*", "+"] | None = None,
    const: Any | None = None,
    default: Any = None,
    type: Callable[[str], T] | FileType | None = None,
    choices: Iterable[T] | None = None,
    required: bool | None = None,
    help: str | None = None,
    metavar: str | tuple[str, ...] | None = None,
) -> Any:
    """Helper function to create `dataclass` fields storing specification about arguments, used later in the method
    `add_argument()`.

    This function accepts all parameters of the original `add_argument()` method (except for `dest`). Three additional
    parameters may be supplied, namely `group_title`, `mutually_exclusive_group_id` and `make_flag`. The parameter
    `name_or_flags`, taken from the original `add_argument()` method, behaves a little different.

    Parameters
    ----------
        - `name_or_flags` (`str`):

            A list of option strings, e.g. `-f`, `--foo`, i.e., starting with `-`.

            The first arguments passed to `arg()` must be a series of flags, or empty (not pass). It is not possible
            to pass a simple argument name to identify positional arguments. In that case, that name is already taken
            from the dataclass field name. This is the only argument taken from the original `add_argument()` method
            which behavior differs from its original behavior.

            In some particular cases, flag name starting with `--` may be automatically created from the dataclass field
            name even when `name_or_flags` is not given. See the `make_flag` argument for details.

        - `group_title` (`str | int | None`, optional): Defaults to `None`.

            The `title` (or a simple id integer) of the argument group in which the argument may be added.

            This is quick way to use the functionality of the method `add_argument_group()` of the standard
            `argparse.ArgumentParser` class.

            By default, `argparse.ArgumentParser` groups command-line arguments into "positional arguments" and
            "options" when displaying help messages. When there is a better conceptual grouping of arguments than this
            default one, appropriate groups can be created using the `add_argument_group()` method, that accepts `title`
            and `description` parameters, which can be used to customize the help display.

            The `group_title` parameter identifies the `title` of the argument group to include the argument::

                >>> @dataclass
                ... class Args:
                ...     foo: str = arg(group_title="my group", help="foo help", make_flag=True)
                ...     bar: str = arg(group_title="my group", help="bar help")
                ...
                >>> parser = make_parser(Args)
                >>> parser.print_help()
                usage: [-h] [--foo FOO] bar

                options:
                  -h, --help  show this help message and exit

                my group:
                  --foo FOO   foo help
                  bar         bar help

            To define the `description` of the argument group, see the `dataparser()` decorator.

        - `mutually_exclusive_group_id` (`str | int | None`, optional): Defaults to `None`.

            The `name` (or a simple integer) that is used as an ID of the a mutually exclusive group in which the
            argument may be included.

            This parameter will make sure that only one of the arguments included in the mutually exclusive group ID is
            present on the command line::

                >>> @dataclass
                ... class Args10:
                ...     foo: bool = arg(action="store_true", mutually_exclusive_group_id="my_group")
                ...     bar: bool = arg(action="store_false", mutually_exclusive_group_id="my_group")
                ...
                >>> parse(Args10, ["--foo"])
                Args10(foo=True, bar=True)
                >>> parse(Args10, ["--bar"])
                Args10(foo=False, bar=False)
                >>> parse(Args10, ["--foo", "--bar"])
                usage: [-h] [--foo | --bar]
                : error: argument --bar: not allowed with argument --foo

            This is a way to use the functionality of the method `add_mutually_exclusive_group()` of the standard
            `argparse.ArgumentParser` class.

            The original `add_mutually_exclusive_group()` method also accepts a `required` parameter, to indicate that
            at least one of the mutually exclusive arguments is required. To define the `required` parameter of the
            mutually exclusive argument group, see the `dataparser()` decorator.

            Note:
                Mutually exclusive are always optionals. If no flag is given, it will be created automatically from the
                `dataclass` field name, regardless of the value of `make_flag`.

        - `make_flag` (`bool | None`, optional): Defaults to `None`.

            Wether to force the automatic creation of a flag starting with `--` from the field name.

            In general, the `default` keyword argument automatically makes the argument optional (i.e., creates a `--`
            flag), but there are some situation when that doesn't happen, e.g., when the parameter `nargs` is passed and
            set equal to `?` or `*`. To force the automatic `--` flag creation in theses cases, pass `make_flag=True`.

            I  general, flag name starting with `--` may be automatically created from the dataclass field name even
            when `name_or_flags` is not given:

                + If `default` value is given (with `nargs` not equal to `?` or `*`)::

                    >>> @dataclass
                    ... class Arg:
                    ...     foo: str = arg(default=42)
                    ...     bar: int = arg()
                    ...
                    >>>
                    >>> parser = make_parse(Arg)
                    >>> parser.print_help()
                    usage: [-h] [--foo FOO] bar

                    positional arguments:
                      bar

                    options:
                      -h, --help  show this help message and exit
                      --foo FOO

                + If only single flags are given (i.e., starting with `-` but none with `--`)::

                    >>> @dataclass
                    ... class Arg:
                    ...     foo: str = arg("-f")
                    ...     bar: str = arg("-b")
                    ...
                    >>>
                    >>> parser = make_parse(Arg)
                    >>> parser.print_help()
                    usage: [-h] [-f FOO] [-b BAR]

                    options:
                      -h, --help         show this help message and exit
                      -f FOO, --foo FOO
                      -b BAR, --bar BAR

                To prevent the automatic creation of the flag in these cases, pass `make_flag=False`.

    Parameters from the original `add_argument()` method
    ----------------------------------------------------
        - `action` (`Literal["store", "store_const", "store_true", "store_false", "append", "append_const", "count", "help", "version", "extend"] | type[Action]`,
          optional): Defaults to `"store"`.

            The basic type of action to be taken when this argument is encountered at the command line.

            `ArgumentParser` objects associate command-line arguments with actions. These actions can do just about
            anything with the command-line arguments associated with them, though most actions simply add an attribute
            to the object returned by `parse_args()`. The `action` keyword argument specifies how the command-line
            arguments should be handled. The supplied actions are

                + `"store"`:
                  This just stores the argument's value. This is the default action. For example::

                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument('--foo')
                    >>> parser.parse_args('--foo 1'.split())
                    Namespace(foo='1')

                + `"store_const"`:
                  This stores the value specified by the const keyword argument; note that the const keyword argument
                  defaults to `None`. The `store_const` action is most commonly used with optional arguments that
                  specify some sort of flag. For example::

                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument('--foo', action='store_const', const=42)
                    >>> parser.parse_args(['--foo'])
                    Namespace(foo=42)

                + `"store_true"` and `"store_false"`
                  - These are special cases of `"store_const"` used for storing the
                  values `True` and `False` respectively. In addition, they create default values of `False` and True
                  respectively. For example::

                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument('--foo', action='store_true')
                    >>> parser.add_argument('--bar', action='store_false')
                    >>> parser.add_argument('--baz', action='store_false')
                    >>> parser.parse_args('--foo --bar'.split())
                    Namespace(foo=True, bar=False, baz=True)

                + `"append"`
                  - This stores a list, and appends each argument value to the list. It is useful to allow an option to
                  be specified multiple times. If the default value is non-empty, the default elements will be present
                  in the parsed value for the option, with any values from the command line appended after those default
                  values. Example usage::

                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument('--foo', action='append')
                    >>> parser.parse_args('--foo 1 --foo 2'.split())
                    Namespace(foo=['1', '2'])

                + `"append_const"`
                  - This stores a list, and appends the value specified by the `const` keyword argument to the list;
                  note that the `const` keyword argument defaults to `None`. The `"append_const"` action is typically
                  useful when multiple arguments need to store constants to the same list. For example::

                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument('--str', dest='types', action='append_const', const=str)
                    >>> parser.add_argument('--int', dest='types', action='append_const', const=int)
                    >>> parser.parse_args('--str --int'.split())
                    Namespace(types=[<class 'str'>, <class 'int'>])

                + `"count"`
                  - This counts the number of times a keyword argument occurs. For example, this is useful for
                  increasing verbosity levels::

                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument('--verbose', '-v', action='count', default=0)
                    >>> parser.parse_args(['-vvv'])
                    Namespace(verbose=3)

                  Note, the default will be `None` unless explicitly set to 0.

                + `"help"`
                  - This prints a complete help message for all the options in the current parser and then exits. By
                  default a help action is automatically added to the parser. See `ArgumentParser` for details of how
                  the output is created.

                + `"version"`
                  - This expects a `version=` keyword argument in the `add_argument()` call, and prints version
                  information and exits when invoked::

                    >>> import argparse
                    >>> parser = argparse.ArgumentParser(prog='PROG')
                    >>> parser.add_argument('--version', action='version', version='%(prog)s 2.0')
                    >>> parser.parse_args(['--version'])
                    PROG 2.0

                + `"extend"`
                  - This stores a list, and extends each argument value to the list. Example usage::

                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument("--foo", action="extend", nargs="+", type=str)
                    >>> parser.parse_args(["--foo", "f1", "--foo", "f2", "f3", "f4"])
                    Namespace(foo=['f1', 'f2', 'f3', 'f4'])

                  You may also specify an arbitrary action by passing an Action subclass or other object that implements
                  the same interface. The `BooleanOptionalAction` is available in `argparse` and adds support for
                  boolean actions such as `--foo` and `--no-foo`::

                    >>> import argparse
                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument('--foo', action=argparse.BooleanOptionalAction)
                    >>> parser.parse_args(['--no-foo'])
                    Namespace(foo=False)

                  The recommended way to create a custom action is to extend Action, overriding the __call__ method and
                  optionally the `__init__` and `format_usage` methods. An example of a custom action::

                    >>> class FooAction(argparse.Action):
                    ...    def __init__(self, option_strings, dest, nargs=None, **kwargs):
                    ...        if nargs is not None:
                    ...            raise ValueError("nargs not allowed")
                    ...        super().__init__(option_strings, dest, **kwargs)
                    ...    def __call__(self, parser, namespace, values, option_string=None):
                    ...        print('%r %r %r' % (namespace, values, option_string))
                    ...        setattr(namespace, self.dest, values)
                    ...
                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument('--foo', action=FooAction)
                    >>> parser.add_argument('bar', action=FooAction)
                    >>> args = parser.parse_args('1 --foo 2'.split())
                    Namespace(bar=None, foo=None) '1' None
                    Namespace(bar='1', foo=None) '2' '--foo'
                    >>> args
                    Namespace(bar='1', foo='2')

                  For more details, see `Action`.

        - `nargs` (`int | Literal["?", "*", "+"]`, optional): Defaults to `None`.

            The number of command-line arguments that should be consumed.

            `ArgumentParser` objects usually associate a single command-line argument with a single action to be taken.
            The `nargs` keyword argument associates a different number of command-line arguments with a single action.
            See also "Specifying ambiguous arguments". The supported values are:

                + `N` (an integer)
                  - `N` arguments from the command line will be gathered together into a list. For example::

                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument('--foo', nargs=2)
                    >>> parser.add_argument('bar', nargs=1)
                    >>> parser.parse_args('c --foo a b'.split())
                    Namespace(bar=['c'], foo=['a', 'b'])

                  Note that `nargs=1` produces a list of one item. This is different from the default, in which the item
                  is produced by itself.

                + `"?"`
                  - One argument will be consumed from the command line if possible, and produced as a single item. If
                  no command-line argument is present, the value from `default` will be produced. Note that for optional
                  arguments, there is an additional case - the option string is present but not followed by a
                  command-line argument. In this case the value from `const` will be produced. Some examples to
                  illustrate this::

                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument('--foo', nargs='?', const='c', default='d')
                    >>> parser.add_argument('bar', nargs='?', default='d')
                    >>> parser.parse_args(['XX', '--foo', 'YY'])
                    Namespace(bar='XX', foo='YY')
                    >>> parser.parse_args(['XX', '--foo'])
                    Namespace(bar='XX', foo='c')
                    >>> parser.parse_args([])
                    Namespace(bar='d', foo='d')

                  One of the more common uses of `nargs="?"` is to allow optional input and output files::

                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
                    >>> parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
                    >>> parser.parse_args(['input.txt', 'output.txt'])
                    Namespace(infile=<_io.TextIOWrapper name='input.txt' encoding='UTF-8'>,
                            outfile=<_io.TextIOWrapper name='output.txt' encoding='UTF-8'>)
                    >>> parser.parse_args([])
                    Namespace(infile=<_io.TextIOWrapper name='<stdin>' encoding='UTF-8'>,
                            outfile=<_io.TextIOWrapper name='<stdout>' encoding='UTF-8'>)

                + `"*"`
                  - All command-line arguments present are gathered into a list. Note that it generally doesn't make
                  much sense to have more than one positional argument with `nargs="*"`, but multiple optional arguments
                  with `nargs="*"` is possible. For example::

                    >>> parser = argparse.ArgumentParser()
                    >>> parser.add_argument('--foo', nargs='*')
                    >>> parser.add_argument('--bar', nargs='*')
                    >>> parser.add_argument('baz', nargs='*')
                    >>> parser.parse_args('a b --foo x y --bar 1 2'.split())
                    Namespace(bar=['1', '2'], baz=['a', 'b'], foo=['x', 'y']

                + `"+"`
                  - Just like `"*"`, all command-line args present are gathered into a list. Additionally, an error
                  message will be generated if there wasn't at least one command-line argument present. For example::

                    >>> parser = argparse.ArgumentParser(prog='PROG')
                    >>> parser.add_argument('foo', nargs='+')
                    >>> parser.parse_args(['a', 'b'])
                    Namespace(foo=['a', 'b'])
                    >>> parser.parse_args([])
                    usage: PROG [-h] foo [foo ...]
                    PROG: error: the following arguments are required: foo

        - `const` (`Any | None`, optional): Defaults to `None`.

            A constant value required by some `action` and `nargs` selections.

            The const argument of `add_argument()` is used to hold constant values that are not read from the command
            line but are required for the various ArgumentParser actions. The two most common uses of it are:

                (1) When `add_argument()` is called with `action='store_const'` or `action='append_const'`. These
                actions add the const value to one of the attributes of the object returned by `parse_args()`. See
                the action description for examples. If const is not provided to `add_argument()`, it will receive a
                default value of `None`.

                (2) When `add_argument()` is called with option strings (like `-f` or `--foo`) and `nargs='?'`. This
                creates an optional argument that can be followed by zero or one command-line arguments. When
                parsing the command line, if the option string is encountered with no command-line argument
                following it, the value of const will be assumed to be `None` instead. See the `nargs` description
                for examples.

            Changed in version 3.11: `const=None` by default, including when `action='append_const'` or
            `action='store_const'`.

        - `default` (`Any`, optional): Defaults to `None`.

            The value produced if the argument is absent from the command line and if it is absent from the namespace
            object.

            All optional arguments and some positional arguments may be omitted at the command line. The `default`
            keyword argument of `add_argument()`, whose value defaults to `None`, specifies what value should be used if
            the command-line argument is not present. For optional arguments, the `default` value is used when the
            option string was not present at the command line::

                >>> parser = argparse.ArgumentParser()
                >>> parser.add_argument('--foo', default=42)
                >>> parser.parse_args(['--foo', '2'])
                Namespace(foo='2')
                >>> parser.parse_args([])
                Namespace(foo=42)

            If the target namespace already has an attribute set, the action default will not over write it::

                >>> parser = argparse.ArgumentParser()
                >>> parser.add_argument('--foo', default=42)
                >>> parser.parse_args([], namespace=argparse.Namespace(foo=101))
                Namespace(foo=101)

            If the `default` value is a string, the parser parses the value as if it were a command-line argument. In
            particular, the parser applies any `type` conversion argument, if provided, before setting the attribute on
            the `Namespace` return value. Otherwise, the parser uses the value as is::

                >>> parser = argparse.ArgumentParser()
                >>> parser.add_argument('--length', default='10', type=int)
                >>> parser.add_argument('--width', default=10.5, type=int)
                >>> parser.parse_args()
                Namespace(length=10, width=10.5)

            For positional arguments with `nargs` equal to `?` or `*`, the default value is used when no command-line
            argument was present::

                >>> parser = argparse.ArgumentParser()
                >>> parser.add_argument('foo', nargs='?', default=42)
                >>> parser.parse_args(['a'])
                Namespace(foo='a')
                >>> parser.parse_args([])
                Namespace(foo=42)

            Note:
                Giving some `default` value to the function `arg()` will force the argument to be optional if there is
                no flag present in the `name_or_flags` argument. That gives the same result as if `make_flag=True`. The
                only exception occurs when `nargs` is passed and it is equal to `?` or `*`. In those cases, passing a
                `default` value will not force the argument to be optional. To achieve that, a flag must be passed in
                `name_or_flags` argument or explicit passing `make_flag=True`.

            Providing `default=argparse.SUPPRESS` causes no attribute to be added if the command-line argument was not
            present::

                >>> parser = argparse.ArgumentParser()
                >>> parser.add_argument('--foo', default=argparse.SUPPRESS)
                >>> parser.parse_args([])
                Namespace()
                >>> parser.parse_args(['--foo', '1'])
                Namespace(foo='1')

        - `type` (`Callable[[str], T] | FileType | None`, optional): Defaults to `None`.

            Note:
                If not given in the `arg()` function, the `type` parameter is automatically inferred from the dataclass
                field type, except for the case when the field type is `bool` (following recommendation below).

            The type to which the command-line argument should be converted.

            By default, the parser reads command-line arguments in as simple strings. However, quite often the
            command-line string should instead be interpreted as another type, such as a `float` or `int`. The `type`
            keyword for `add_argument()` allows any necessary type-checking and type conversions to be performed.

            If the `type` keyword is used with the `default` keyword, the type converter is only applied if the default
            is a string.

            The argument to `type` can be any callable that accepts a single string. If the function raises
            `ArgumentTypeError`, `TypeError`, or `ValueError`, the exception is caught and a nicely formatted error
            message is displayed. No other exception types are handled.

            Common built-in types and functions can be used as type converters::

                import argparse
                import pathlib

                parser = argparse.ArgumentParser()
                parser.add_argument('count', type=int)
                parser.add_argument('distance', type=float)
                parser.add_argument('street', type=ascii)
                parser.add_argument('code_point', type=ord)
                parser.add_argument('source_file', type=open)
                parser.add_argument('dest_file', type=argparse.FileType('w', encoding='latin-1'))
                parser.add_argument('datapath', type=pathlib.Path)

            User defined functions can be used as well::

                >>> def hyphenated(string):
                ...    return '-'.join([word[:4] for word in string.casefold().split()])
                ...
                >>> parser = argparse.ArgumentParser()
                >>> _ = parser.add_argument('short_title', type=hyphenated)
                >>> parser.parse_args(['"The Tale of Two Cities"'])
                Namespace(short_title='"the-tale-of-two-citi')

            The `bool()` function is not recommended as a type converter. All it does is convert empty strings to False
            and non-empty strings to True. This is usually not what is desired.

            In general, the type keyword is a convenience that should only be used for simple conversions that can only
            raise one of the three supported exceptions. Anything with more interesting error-handling or resource
            management should be done downstream after the arguments are parsed.

            For example, JSON or YAML conversions have complex error cases that require better reporting than can be
            given by the `type` keyword. A `JSONDecodeError` would not be well formatted and a `FileNotFoundError`
            exception would not be handled at all.

            Even `FileType` has its limitations for use with the `type` keyword. If one argument uses `FileType` and
            then a subsequent argument fails, an error is reported but the file is not automatically closed. In this
            case, it would be better to wait until after the parser has run and then use the `with`-statement to manage
            the files.

            For type checkers that simply check against a fixed set of values, consider using the `choices` keyword
            instead.

        - `choices` (`Iterable[T] | None`, optional): Defaults to `None`.

            A sequence of the allowable values for the argument.

            Some command-line arguments should be selected from a restricted set of values. These can be handled by
            passing a sequence object as the choices keyword argument to `add_argument()`. When the command line is
            parsed, argument values will be checked, and an error message will be displayed if the argument was not one
            of the acceptable values::

                >>> parser = argparse.ArgumentParser(prog='game.py')
                >>> parser.add_argument('move', choices=['rock', 'paper', 'scissors'])
                >>> parser.parse_args(['rock'])
                Namespace(move='rock')
                >>> parser.parse_args(['fire'])
                usage: game.py [-h] {rock,paper,scissors}
                game.py: error: argument move: invalid choice: 'fire' (choose from 'rock',
                'paper', 'scissors')

            Note that inclusion in the choices sequence is checked after any `type` conversions have been performed, so
            the type of the objects in the choices sequence should match the `type` specified::

                >>> parser = argparse.ArgumentParser(prog='doors.py')
                >>> parser.add_argument('door', type=int, choices=range(1, 4))
                >>> print(parser.parse_args(['3']))
                Namespace(door=3)
                >>> parser.parse_args(['4'])
                usage: doors.py [-h] {1,2,3}
                doors.py: error: argument door: invalid choice: 4 (choose from 1, 2, 3)

            Any sequence can be passed as the choices value, so `list` objects, `tuple` objects, and custom sequences
            are all supported.

            Use of `enum.Enum` is not recommended because it is difficult to control its appearance in usage, help, and
            error messages.

            Formatted choices override the default `metavar` which is normally derived from `dest`. This is usually what
            you want because the user never sees the dest parameter. If this display isn't desirable (perhaps because
            there are many choices), just specify an explicit `metavar`.

        - `required` (`bool | None`, optional): Defaults to `None`.

            Whether or not the command-line option may be omitted (optionals only).

            In general, the `argparse` module assumes that flags like `-f` and `--bar` indicate optional arguments,
            which can always be omitted at the command line. To make an option required, `True` can be specified for the
            `required=` keyword argument to `add_argument()`::

                >>> parser = argparse.ArgumentParser()
                >>> parser.add_argument('--foo', required=True)
                >>> parser.parse_args(['--foo', 'BAR'])
                Namespace(foo='BAR')
                >>> parser.parse_args([])
                usage: [-h] --foo FOO
                : error: the following arguments are required: --foo

            As the example shows, if an option is marked as `required`, `parse_args()` will report an error if that
            option is not present at the command line.

            Note:
                Required options are generally considered bad form because users expect options to be optional, and thus
                they should be avoided when possible.

        - `help` (`str | None`, optional): Defaults to `None`.

            A brief description of what the argument does.

            The `help` value is a string containing a brief description of the argument. When a user requests help
            (usually by using `-h` or `--help` at the command line), these `help` descriptions will be displayed with
            each argument::

                >>> parser = argparse.ArgumentParser(prog='frobble')
                >>> parser.add_argument('--foo', action='store_true', help='foo the bars before frobbling')
                >>> parser.add_argument('bar', nargs='+', help='one of the bars to be frobbled')
                >>> parser.parse_args(['-h'])
                usage: frobble [-h] [--foo] bar [bar ...]

                positional arguments:
                bar     one of the bars to be frobbled

                options:
                  -h, --help  show this help message and exit
                  --foo   foo the bars before frobbling

            The help strings can include various format specifiers to avoid repetition of things like the program name
            or the argument `default`. The available specifiers include the program name, `%(prog)s` and most keyword
            arguments to `add_argument()`, e.g. `%(default)s`, `%(type)s`, etc.::

                >>> parser = argparse.ArgumentParser(prog='frobble')
                >>> parser.add_argument('bar', nargs='?', type=int, default=42,
                ...                 help='the bar to %(prog)s (default: %(default)s)')
                >>> parser.print_help()
                usage: frobble [-h] [bar]

                positional arguments:
                bar     the bar to frobble (default: 42)

                options:
                  -h, --help  show this help message and exit

            As the help string supports %-formatting, if you want a literal % to appear in the help string, you must
            escape it as `%%`.

            `argparse` supports silencing the help entry for certain options, by setting the `help` value to
            `argparse.SUPPRESS`::

                >>> parser = argparse.ArgumentParser(prog='frobble')
                >>> parser.add_argument('--foo', help=argparse.SUPPRESS)
                >>> parser.print_help()
                usage: frobble [-h]

                options:
                  -h, --help  show this help message and exit

        - `metavar` (`str | tuple[str, ...] | None`, optional): Defaults to `None`.

            A name for the argument in usage messages.

            When `ArgumentParser` generates help messages, it needs some way to refer to each expected argument. By
            default, ArgumentParser objects use the `dest` value as the "name" of each object. By default, for
            positional argument actions, the `dest` value is used directly, and for optional argument actions, the
            `dest` value is uppercased. So, a single positional argument with `dest='bar'` will be referred to as `bar`.
            A single optional argument `--foo` that should be followed by a single command-line argument will be
            referred to as `FOO`. An example::

                >>> parser = argparse.ArgumentParser()
                >>> parser.add_argument('--foo')
                >>> parser.add_argument('bar')
                >>> parser.parse_args('X --foo Y'.split())
                Namespace(bar='X', foo='Y')
                >>> parser.print_help()
                usage:  [-h] [--foo FOO] bar

                positional arguments:
                bar

                options:
                  -h, --help  show this help message and exit
                  --foo FOO

            An alternative name can be specified with `metavar`::

                >>> parser = argparse.ArgumentParser()
                >>> parser.add_argument('--foo', metavar='YYY')
                >>> parser.add_argument('bar', metavar='XXX')
                >>> parser.parse_args('X --foo Y'.split())
                Namespace(bar='X', foo='Y')
                >>> parser.print_help()
                usage:  [-h] [--foo YYY] XXX

                positional arguments:
                XXX

                options:
                  -h, --help  show this help message and exit
                  --foo YYY

            Note that `metavar` only changes the displayed name - the name of the attribute on the `parse_args()` object
            is still determined by the `dest` value.

            Different values of `nargs` may cause the metavar to be used multiple times. Providing a tuple to `metavar`
            specifies a different display for each of the arguments::

                >>> parser = argparse.ArgumentParser(prog='PROG')
                >>> parser.add_argument('-x', nargs=2)
                >>> parser.add_argument('--foo', nargs=2, metavar=('bar', 'baz'))
                >>> parser.print_help()
                usage: PROG [-h] [-x X X] [--foo bar baz]

                options:
                  -h, --help     show this help message and exit
                  -x X X
                  --foo bar baz

        - `dest` (`str | None`, optional): Defaults to `None`.

            Note:
                The parameter `dest` is described here just for documentation. It will raise an error if it is passed to
                the `arg()` function, because it is not necessary: the `dest` keyword argument of the `add_argument()`
                method is taken from the dataclass field name.

            The name of the attribute to be added to the object returned by `parse_args()`.

            Most `ArgumentParser` actions add some value as an attribute of the object returned by `parse_args()`. The
            name of this attribute is determined by the `dest` keyword argument of `add_argument()`. For positional
            argument actions, `dest` is normally supplied as the first argument to `add_argument()`::

                >>> parser = argparse.ArgumentParser()
                >>> parser.add_argument('bar')
                >>> parser.parse_args(['XXX'])
                Namespace(bar='XXX')

            For optional argument actions, the value of `dest` is normally inferred from the option strings.
            `ArgumentParser` generates the value of `dest` by taking the first long option string and stripping away the
            initial `--` string. If no long option strings were supplied, `dest` will be derived from the first short
            option string by stripping the initial `-` character. Any internal `-` characters will be converted to `_`
            characters to make sure the string is a valid attribute name. The examples below illustrate this behavior::

                >>> parser = argparse.ArgumentParser()
                >>> parser.add_argument('-f', '--foo-bar', '--foo')
                >>> parser.add_argument('-x', '-y')
                >>> parser.parse_args('-f 1 -x 2'.split())
                Namespace(foo_bar='1', x='2')
                >>> parser.parse_args('--foo 1 -y 2'.split())
                Namespace(foo_bar='1', x='2')

            `dest` allows a custom attribute name to be provided::

                >>> parser = argparse.ArgumentParser()
                >>> parser.add_argument('--foo', dest='bar')
                >>> parser.parse_args('--foo XXX'.split())
                Namespace(bar='XXX')

    Returns
    -------
        `default@arg | Field`: A `dataclass` field with given `default` value of the field and `metadata` dictionary
        filled with argument parameters.
    """
    ...

def make_parser(cls: type, *, parser: ArgumentParser | None = None) -> ArgumentParser:
    """Creates a `ArgumentParser` with command-line arguments according to the fields of `cls`.

    Use this to create a `ArgumentParser` and not immediately parse the arguments (i.e., save it for later).
    If you do want to parse immediately, use `parse()`.

    Parameters
    ----------
        - `cls` (`type`):

            A `dataclass` according to which argument parser is created.

        - `parser` (`ArgumentParser | None`, optional): Defaults to `None`.

            Existing parser to add arguments to. By default creates a new parser.

    Returns
    -------
        `ArgumentParser`: The new `ArgumentParser` object or the existing parser with added arguments.
    """
    ...

def parse(cls: type[Class], args: Sequence[str] | None = None, *, parser: ArgumentParser | None = None) -> Class:
    """Parse command line arguments according to the fields of `cls` and populate it.

    Accepts classes decorated with `dataclass`.

    Parameters
    ----------
        - `cls` (`type[Class]`):

            A `dataclass` used as object to take the attributes to parse the command-line arguments.

        - `args` (`Sequence[str] | None`, optional): Defaults to `None`.

            List of strings to parse. The default is taken from `sys.argv`, like the original `parse_args()` method.

        - `parser` (`ArgumentParser | None`, optional): Defaults to `None`.

            Existing parser to add arguments to and parse from.

    Returns
    -------
        `Class`: The populated `dataclass` with argument values.
    """
    ...

@overload
def dataparser(cls: type[Class]) -> type[Class]: ...
@overload
def dataparser(
    *,
    groups_descriptions: dict[str | int, str] | None = None,
    required_mutually_exclusive_groups: dict[str | int, bool] | None = None,
    default_bool: bool = False,
    help_fmt: Callable[[str], str] | None = None,
    prog: str | None = None,
    usage: str | None = None,
    description: str | None = None,
    epilog: str | None = None,
    parents: Sequence[ArgumentParser] = [],
    formatter_class: HelpFormatter = ...,
    prefix_chars: str = "-",
    fromfile_prefix_chars: str | None = None,
    argument_default: Any = None,
    conflict_handler: str = "error",
    add_help: bool = True,
    allow_abbrev: bool = True,
    exit_on_error: bool = True,
) -> Callable[[type[Class]], type[Class]]:
    """A wrapper around `dataclass` for passing parameters to the `ArgumentParser` constructor.

    This function accepts all parameters of the original `ArgumentParser` constructor. Four additional parameters may be
    supplied, namely `groups_descriptions`, `required_mutually_exclusive_groups`, `default_bool` and `help_fmt`.

    Parameters
    ----------
        - `groups_descriptions` (`dict[str | int, str] | None`, optional): Defaults to `None`.

            A dictionary with argument groups descriptions (used to customize the CLI display) whose keys should match
            some value of the argument `group_title` passed to the `arg()` function.

        - `required_mutually_exclusive_groups` (`dict[str | int, bool] | None`, optional): Defaults to `None`.

            A dictionary with booleans indicating the required status of mutually exclusive groups arguments. The
            dictionary keys should match some value of the argument `mutually_exclusive_group_id` passed to the `arg()`
            function. The value `True` indicates that at least one of the mutually exclusive arguments in the matching
            group is required.

        - `default_bool` (`bool`, optional): Defaults to `False`.

            The default boolean value used in in boolean fields when there is no `default` value passed.

        - `help_fmt` (`Callable[[str], str] | None`, optional): Defaults to `None`.

            A formatter function used to format the help text in argument descriptions. When it is passed, the
            `formatter_class` parameter passed to the `ArgumentParser` constructor is assumed to be
            `RawDescriptionHelpFormatter`.

    Parameters from the original `ArgumentParser` class
    ---------------------------------------------------
        - `prog` (`str | None`, optional): Defaults to `None`.

            The name of the program (default: `os.path.basename(sys.argv[0])`)

            By default, `ArgumentParser` objects use `sys.argv[0]` to determine how to display the name of the program
            in help messages. This default is almost always desirable because it will make the help messages match how
            the program was invoked on the command line. For example, consider a file named `myprogram.py` with the
            following code::

                import argparse parser = argparse.ArgumentParser() parser.add_argument('--foo', help='foo help') args =
                parser.parse_args()

            The help for this program will display `myprogram.py` as the program name (regardless of where the program
            was invoked from)::

                $ python myprogram.py --help
                usage: myprogram.py [-h] [--foo FOO]

                options:
                  -h, --help  show this help message and exit --foo FOO   foo help
                $ cd .. $ python subdir/myprogram.py --help usage: myprogram.py [-h] [--foo FOO]

                options:
                  -h, --help  show this help message and exit --foo FOO   foo help

            To change this default behavior, another value can be supplied using the `prog=` argument to
            `ArgumentParser`::

                >>> parser = argparse.ArgumentParser(prog='myprogram')
                >>> parser.print_help()
                usage: myprogram [-h]

                options:
                  -h, --help  show this help message and exit

            Note that the program name, whether determined from `sys.argv[0]` or from the `prog=` argument, is available
            to help messages using the `%(prog)s` format specifier::

                >>> parser = argparse.ArgumentParser(prog='myprogram')
                >>> parser.add_argument('--foo', help='foo of the %(prog)s program')
                >>> parser.print_help()
                usage: myprogram [-h] [--foo FOO]

                options:
                  -h, --help  show this help message and exit --foo FOO   foo of the myprogram program

        - `usage` (`str | None`, optional): Defaults to `None`.

            The string describing the program usage (default: generated from arguments added to parser).

            By default, `ArgumentParser` calculates the usage message from the arguments it contains::

                >>> parser = argparse.ArgumentParser(prog='PROG')
                >>> parser.add_argument('--foo', nargs='?', help='foo help')
                >>> parser.add_argument('bar', nargs='+', help='bar help')
                >>> parser.print_help()
                usage: PROG [-h] [--foo [FOO]] bar [bar ...]

                positional arguments: bar          bar help

                options:
                  -h, --help   show this help message and exit --foo [FOO]  foo help

            The default message can be overridden with the `usage=` keyword argument::

                >>> parser = argparse.ArgumentParser(prog='PROG', usage='%(prog)s [options]')
                >>> parser.add_argument('--foo', nargs='?', help='foo help')
                >>> parser.add_argument('bar', nargs='+', help='bar help')
                >>> parser.print_help()
                usage: PROG [options]

                positional arguments: bar          bar help

                options:
                  -h, --help   show this help message and exit --foo [FOO]  foo help

            The `%(prog)s` format specifier is available to fill in the program name in your usage messages.

        - `description` (`str | None`, optional): Defaults to `None`.

            Text to display before the argument help (by default, no text).

            Most calls to the `ArgumentParser` constructor will use the `description=` keyword argument. This argument
            gives a brief description of what the program does and how it works. In help messages, the description is
            displayed between the command-line usage string and the help messages for the various arguments::

                >>> parser = argparse.ArgumentParser(description='A foo that bars')
                >>> parser.print_help()
                usage: argparse.py [-h]

                A foo that bars

                options:
                  -h, --help  show this help message and exit

            By default, the description will be line-wrapped so that it fits within the given space. To change this
            behavior, see the `formatter_class` argument.

        - `epilog` (`str | None`, optional): Defaults to `None`.

            Text to display after the argument help (by default, no text).

            Some programs like to display additional description of the program after the description of the arguments.
            Such text can be specified using the `epilog=` argument to `ArgumentParser`::

                >>> parser = argparse.ArgumentParser(
                ...                             description='A foo that bars', ... epilog="And that's how you'd foo a
                bar") >>> parser.print_help() usage: argparse.py [-h]

                A foo that bars

                options:
                  -h, --help  show this help message and exit

                And that's how you'd foo a bar

            As with the `description` argument, the `epilog=` text is by default line-wrapped, but this behavior can be
            adjusted with the `formatter_class` argument to `ArgumentParser`.

        - `parents` (`Sequence[ArgumentParser]`, optional): Defaults to `[]`.

            A list of `ArgumentParser` objects whose arguments should also be included.

            Sometimes, several parsers share a common set of arguments. Rather than repeating the definitions of these
            arguments, a single parser with all the shared arguments and passed to `parents=` argument to
            `ArgumentParser` can be used. The `parents=` argument takes a list of `ArgumentParser` objects, collects all
            the positional and optional actions from them, and adds these actions to the `ArgumentParser` object being
            constructed::

                >>> parent_parser = argparse.ArgumentParser(add_help=False)
                >>> parent_parser.add_argument('--parent', type=int)

                >>> foo_parser = argparse.ArgumentParser(parents=[parent_parser])
                >>> foo_parser.add_argument('foo')
                >>> foo_parser.parse_args(['--parent', '2', 'XXX'])
                Namespace(foo='XXX', parent=2)

                >>> bar_parser = argparse.ArgumentParser(parents=[parent_parser])
                >>> bar_parser.add_argument('--bar')
                >>> bar_parser.parse_args(['--bar', 'YYY'])
                Namespace(bar='YYY', parent=None)

            Note that most parent parsers will specify `add_help=False`. Otherwise, the `ArgumentParser` will see two
            `-h/--help` options (one in the parent and one in the child) and raise an error.

            Note:
                You must fully initialize the parsers before passing them via `parents=`. If you change the parent
                parsers after the child parser, those changes will not be reflected in the child.

        - `formatter_class` (`_FormatterClass`, optional):

            A class for customizing the help output.

            `ArgumentParser` objects allow the help formatting to be customized by specifying an alternate formatting
            class. Currently, there are four such classes::

                class argparse.RawDescriptionHelpFormatter
                class argparse.RawTextHelpFormatter
                class argparse.ArgumentDefaultsHelpFormatter
                class argparse.MetavarTypeHelpFormatter

            `RawDescriptionHelpFormatter` and `RawTextHelpFormatter` give more control over how textual descriptions are
            displayed. By default, `ArgumentParser` objects line-wrap the `description` and `epilog` texts in
            command-line help messages::

                >>> parser = argparse.ArgumentParser(
                ...    prog='PROG',
                ...    description='''this description
                ...        was indented weird
                ...            but that is okay''',
                ...    epilog='''
                ...            likewise for this epilog whose whitespace will
                ...        be cleaned up and whose words will be wrapped
                ...        across a couple lines''')
                >>> parser.print_help()
                usage: PROG [-h]
                
                this description was indented weird but that is okay
                
                options:
                 -h, --help  show this help message and exit
                
                likewise for this epilog whose whitespace will be cleaned up and whose words
                will be wrapped across a couple lines

            Passing `RawDescriptionHelpFormatter` as `formatter_class=` indicates that `description` and `epilog` are
            already correctly formatted and should not be line-wrapped::

                >>> parser = argparse.ArgumentParser(
                ...    prog='PROG',
                ...    formatter_class=argparse.RawDescriptionHelpFormatter,
                ...    description=textwrap.dedent('''\
                ...        Please do not mess up this text!
                ...        --------------------------------
                ...            I have indented it
                ...            exactly the way
                ...            I want it
                ...        '''))
                >>> parser.print_help()
                usage: PROG [-h]
                
                Please do not mess up this text!
                --------------------------------
                   I have indented it
                   exactly the way
                   I want it
                
                options:
                 -h, --help  show this help message and exit

            `RawTextHelpFormatter` maintains whitespace for all sorts of help text, including argument descriptions.
            However, multiple new lines are replaced with one. If you wish to preserve multiple blank lines, add spaces
            between the newlines.

            `ArgumentDefaultsHelpFormatter` automatically adds information about default values to each of the argument
            help messages::

                >>> parser = argparse.ArgumentParser(
                ...    prog='PROG',
                ...    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
                >>> parser.add_argument('--foo', type=int, default=42, help='FOO!')
                >>> parser.add_argument('bar', nargs='*', default=[1, 2, 3], help='BAR!')
                >>> parser.print_help()
                usage: PROG [-h] [--foo FOO] [bar ...]
                
                positional arguments:
                 bar         BAR! (default: [1, 2, 3])
                
                options:
                 -h, --help  show this help message and exit
                 --foo FOO   FOO! (default: 42)

            `MetavarTypeHelpFormatter` uses the name of the `type` argument for each argument as the display name for
            its values (rather than using the `dest` as the regular formatter does)::

                >>> parser = argparse.ArgumentParser(
                ...     prog='PROG',
                ...     formatter_class=argparse.MetavarTypeHelpFormatter)
                >>> parser.add_argument('--foo', type=int)
                >>> parser.add_argument('bar', type=float)
                >>> parser.print_help()
                usage: PROG [-h] [--foo int] float
                
                positional arguments:
                  float
                
                options:
                  -h, --help  show this help message and exit
                  --foo int

        - `prefix_chars` (`str`, optional): Defaults to `"-"`.

            The set of characters that prefix optional arguments (default: '-').

            Most command-line options will use `-` as the prefix, e.g. `-f/--foo`. Parsers that need to support
            different or additional prefix characters, e.g. for options like `+f` or `/foo`, may specify them using the
            `prefix_chars=` argument to the ArgumentParser constructor::

                >>> parser = argparse.ArgumentParser(prog='PROG', prefix_chars='-+')
                >>> parser.add_argument('+f')
                >>> parser.add_argument('++bar')
                parser.parse_args('+f X ++bar Y'.split())
                Namespace(bar='Y', f='X')

            The `prefix_chars=` argument defaults to `'-'`. Supplying a set of characters that does not include `-` will
            cause `-f/--foo` options to be disallowed.

        - `fromfile_prefix_chars` (`str | None`, optional): Defaults to `None`.

            The set of characters that prefix files from which additional arguments should be read (default: `None`).

            Sometimes, when dealing with a particularly long argument list, it may make sense to keep the list of
            arguments in a file rather than typing it out at the command line. If the `fromfile_prefix_chars=` argument
            is given to the `ArgumentParser` constructor, then arguments that start with any of the specified characters
            will be treated as files, and will be replaced by the arguments they contain. For example::

                >>> with open('args.txt', 'w', encoding=sys.getfilesystemencoding()) as fp:
                ...    fp.write('-f\\nbar') 
                ... 
                >>> parser = argparse.ArgumentParser(fromfile_prefix_chars='@') 
                >>> parser.add_argument('-f') 
                >>> parser.parse_args(['-f', 'foo', '@args.txt']) 
                Namespace(f='bar')

            Arguments read from a file must by default be one per line (but see also `convert_arg_line_to_args()`) and
            are treated as if they were in the same place as the original file referencing argument on the command line.
            So in the example above, the expression `['-f', 'foo', '@args.txt']` is considered equivalent to the
            expression `['-f', 'foo', '-f', 'bar']`.

            `ArgumentParser` uses filesystem encoding and error handler to read the file containing arguments.

            The `fromfile_prefix_chars=` argument defaults to `None`, meaning that arguments will never be treated as
            file references.

            Changed in version 3.12: `ArgumentParser` changed encoding and errors to read arguments files from default
            (e.g. `locale.getpreferredencoding(False)` and `"strict"`) to filesystem encoding and error handler.
            Arguments file should be encoded in UTF-8 instead of ANSI Codepage on Windows.

        - `argument_default` (`Any`, optional): Defaults to `None`.

            The global default value for arguments (default: `None`).

            Generally, argument defaults are specified either by passing a default to `add_argument()` or by calling the
            `set_defaults()` methods with a specific set of name-value pairs. Sometimes however, it may be useful to
            specify a single parser-wide default for arguments. This can be accomplished by passing the
            `argument_default=` keyword argument to `ArgumentParser`. For example, to globally suppress attribute
            creation on `parse_args()` calls, we supply `argument_default=SUPPRESS`::

                >>> parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
                >>> parser.add_argument('--foo')
                >>> parser.add_argument('bar', nargs='?')
                >>> parser.parse_args(['--foo', '1', 'BAR'])
                Namespace(bar='BAR', foo='1')
                >>> parser.parse_args([])
                Namespace()

        - `conflict_handler` (`str`, optional): Defaults to `"error"`.

            The strategy for resolving conflicting optionals (usually unnecessary).

            `ArgumentParser` objects do not allow two actions with the same option string. By default, `ArgumentParser`
            objects raise an exception if an attempt is made to create an argument with an option string that is already
            in use::

                >>> parser = argparse.ArgumentParser(prog='PROG')
                >>> parser.add_argument('-f', '--foo', help='old foo help')
                >>> parser.add_argument('--foo', help='new foo help')
                Traceback (most recent call last):
                ..
                ArgumentError: argument --foo: conflicting option string(s): --foo

            Sometimes (e.g. when using `parents`) it may be useful to simply override any older arguments with the same
            option string. To get this behavior, the value `'resolve'` can be supplied to the `conflict_handler=`
            argument of `ArgumentParser`::

                >>> parser = argparse.ArgumentParser(prog='PROG', conflict_handler='resolve')
                >>> parser.add_argument('-f', '--foo', help='old foo help')
                >>> parser.add_argument('--foo', help='new foo help')
                >>> parser.print_help()
                usage: PROG [-h] [-f FOO] [--foo FOO]

                options:
                  -h, --help  show this help message and exit -f FOO      old foo help --foo FOO   new foo help

            Note that `ArgumentParser` objects only remove an action if all of its option strings are overridden. So, in
            the example above, the old `-f/--foo` action is retained as the `-f` action, because only the `--foo` option
            string was overridden.

        - `add_help` (`bool`, optional): Defaults to `True`.

            Add a `-h/--help` option to the parser (default: `True`).

            By default, ArgumentParser objects add an option which simply displays the parser's help message. For
            example, consider a file named myprogram.py containing the following code::

                import argparse parser = argparse.ArgumentParser()
                parser.add_argument('--foo', help='foo help')
                args = parser.parse_args()

            If `-h` or `--help` is supplied at the command line, the ArgumentParser help will be printed::

                $ python myprogram.py --help
                usage: myprogram.py [-h] [--foo FOO]

                options:
                  -h, --help  show this help message and exit
                  --foo FOO   foo help

            Occasionally, it may be useful to disable the addition of this help option. This can be achieved by passing
            `False` as the `add_help=` argument to `ArgumentParser`::

                >>> parser = argparse.ArgumentParser(prog='PROG', add_help=False)
                >>> parser.add_argument('--foo', help='foo help')
                >>> parser.print_help()
                usage: PROG [--foo FOO]

                options: --foo FOO  foo help

            The help option is typically `-h/--help`. The exception to this is if the `prefix_chars=` is specified and
            does not include `-`, in which case `-h` and `--help` are not valid options. In this case, the first
            character in `prefix_chars` is used to prefix the help options::

                >>> parser = argparse.ArgumentParser(prog='PROG', prefix_chars='+/')
                >>> parser.print_help()
                usage: PROG [+h]

                options: +h, ++help  show this help message and exit

        - `allow_abbrev` (`bool`, optional): Defaults to `True`.

            Normally, when you pass an argument list to the `parse_args()` method of an `ArgumentParser`, it recognizes
            abbreviations of long options.

            This feature can be disabled by setting `allow_abbrev` to `False`::

                >>> parser = argparse.ArgumentParser(prog='PROG', allow_abbrev=False)
                >>> parser.add_argument('--foobar', action='store_true')
                >>> parser.add_argument('--foonley', action='store_false')
                >>> parser.parse_args(['--foon'])
                usage: PROG [-h] [--foobar] [--foonley]
                PROG: error: unrecognized arguments: --foon

            New in version 3.5.

        - `exit_on_error` (`bool`, optional): Defaults to `True`.

            Normally, when you pass an invalid argument list to the `parse_args()` method of an `ArgumentParser`, it
            will exit with error info.

            If the user would like to catch errors manually, the feature can be enabled by setting `exit_on_error` to
            `False`::

                >>> parser = argparse.ArgumentParser(exit_on_error=False)
                >>> parser.add_argument('--integers', type=int)
                _StoreAction(option_strings=['--integers'], dest='integers', nargs=None, const=None, default=None, type=<class 'int'>, choices=None, help=None, metavar=None)
                >>> try:
                ...     parser.parse_args('--integers a'.split())
                ... except argparse.ArgumentError:
                ...     print('Catching an argumentError')
                ...
                Catching an argumentError

            New in version 3.9.

    Returns
    -------
        `Callable[[type[Class]], type[Class]]`: The decorator used to wrap around `dataclass` decorator passing
        parameters to the `ArgumentParser` constructor. When it is used with no parameters, just returns the class
        decorated with `dataclass`.
    """
    ...

def write_help(
    text: str,
    width: int | None = None,
    space: int = 24,
    dedent: bool = True,
    final_newlines: bool = True,
) -> str:
    """Writes formatted help text (wrapped) preserving 'new lines'.
    This is supplied as an option to use in the `help_fmt` argument.

    Parameters
    ----------
        - `text` (`str`):

            The help text.

        - `width` (`int`, optional): Defaults to `None`.

            The width of the help text to wrap (if `None`, use terminal `COLUMNS`).

        - `space` (`int`, optional): Defaults to `24`.

            The indentation space used in in CLI helps.

        - `dedent` (`bool`, optional): Defaults to `True`.

            Whether to remove blank spaces at start and end of lines.

        - `final_newlines` (`bool`, optional): Defaults to `True`.

            Whether to add a final empty line.

    Returns
    -------
        `str`: The help text formatted (wrapped and preserving new lines)
    """
    ...
