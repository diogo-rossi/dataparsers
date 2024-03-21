# %% Setup

import sys, os
from pathlib import Path

THIS_DIR = Path(__file__).absolute().parent
ROOT_DIR = THIS_DIR.parent
SRC_DIR = Path(f"{ROOT_DIR}/src")
sys.path.insert(0, str(SRC_DIR))

# %% Imports

from dataclasses import dataclass
from dataparsers import arg, make_parser, dataparser, parse, write_help, default

# %% Example 1: Basic usage


@dataclass
class Args:
    foo: str
    bar: int = 42


args = parse(Args)
print("Printing `args`:")
print(args)


# %% Example 2: Argument specification


@dataclass
class Args:
    foo: str = arg(help="foo help")
    bar: int = arg(default=42, help="bar help")


args = parse(Args)


# %% Example 3: Aliases


@dataclass
class Args:
    foo: str = arg(help="foo help")
    bar: int = arg("-b", default=42, help="bar help")


args = parse(Args)


# %% Example 4: Automatic flag creation


@dataclass
class Args:
    bar: int = arg("--bar", default=42, nargs="?", help="bar help")


args = parse(Args)


# %% Example 5: Automatic flag creation


@dataclass
class Args:
    bar: int = arg(default=42, nargs="?", help="bar help", make_flag=True)


args = parse(Args)


# %% Example 6: Avoiding automatic flag creation


@dataclass
class Args:
    bar: int = arg("-b", default=42, help="bar help", make_flag=False)


args = parse(Args)


# %% Example 7: Booleans


@dataclass
class Args:
    bar: bool


make_parser(Args).print_help()
parse(Args, [])

# %% Example 8: Decoupling code from the command line interface


@dataclass
class Args:
    path: str = arg("-f", "--file-output", metavar="<filepath>", help="Text file to write output")


args = parse(Args)
print(args)

# %% Example 9: Argument groups


@dataclass
class Args:
    foo: str = arg(group_title="Group1")
    bar: str = arg(group_title="Group1")
    sam: str = arg(group_title="Group2")
    ham: str = arg(group_title="Group2")


parser = make_parser(Args)
parser.print_help()


# %% Example 10: Mutually exclusive argument group


@dataclass
class Args:
    foo: str = arg(mutually_exclusive_group_id="my_group")
    bar: str = arg(mutually_exclusive_group_id="my_group")


parser = make_parser(Args)
parser.print_help()

parse(Args, ["--foo", "test", "--bar", "newtest"])

# %% Example 11: Identifying argument groups


@dataclass
class Args:
    foo: str = arg(group_title=1)
    bar: str = arg(group_title=1)
    sam: str = arg(group_title=2)
    ham: str = arg(group_title=2)


parser = make_parser(Args)
parser.print_help()


# %% Example 12: Parser specifications


@dataparser(prog="MyProgram", description="A foo that bars")
class Args: ...


make_parser(Args).print_help()

# %% Example 13: Groups `description` and `required` status


@dataparser(
    groups_descriptions={"Group1": "1st group description", "Group2": "2nd group description"},
    required_mutually_exclusive_groups={0: True, 1: False},
    add_help=False,  # Disable automatic addition of `-h` or `--help` at the command line
)
class Args:
    foo: str = arg(group_title="Group1", mutually_exclusive_group_id=0)
    bar: int = arg(group_title="Group1", mutually_exclusive_group_id=0)
    sam: bool = arg(group_title="Group2", mutually_exclusive_group_id=1)
    ham: float = arg(group_title="Group2", mutually_exclusive_group_id=1)


make_parser(Args).print_help()


# %% Example 14: Default for booleans


@dataparser
class Args:
    foo: bool


parse(Args, ["--foo"])


@dataparser(default_bool=True)
class Args:
    foo: bool = arg(help="Boolean value")


parse(Args, ["--foo"])


# %% Example 15: Help formatter

from dataparsers import arg, make_parser, dataparser, write_help


@dataparser(help_formatter=write_help)
class Args:
    foo: str = arg(
        default=12.5,
        help="""This description is printed as written here.
                It preserves lines breaks.""",
    )
    bar: float = arg(
        default=25.5,
        help="""This description is also formatted by `write_help` and
                it is separated from the previous by a blank line.
                The parameter has default value of %(default)s.""",
    )


make_parser(Args).print_help()


# %% Example 16: Argument groups as ClassVars

from dataclasses import dataclass
from dataparsers import arg, make_parser, group, parse
from typing import ClassVar


@dataclass
class Args:
    my_first_group: ClassVar = group()
    foo: str = arg(group=my_first_group)
    bar: str = arg(group=my_first_group)
    ...
    my_second_group: ClassVar = group()
    sam: str = arg(group=my_second_group)
    ham: str = arg(group=my_second_group)


make_parser(Args).print_help()


# %% Example 17: Argument groups as ClassVars with options

from dataclasses import dataclass
from dataparsers import arg, make_parser, group, mutually_exclusive_group, group
from typing import ClassVar


@dataclass
class Args:
    my_first_group: ClassVar = group(title="Group1", description="First group description")
    my_1st_exclusive_group: ClassVar = mutually_exclusive_group(required=False)
    foo: str = arg(group=my_first_group, mutually_exclusive_group=my_1st_exclusive_group)
    bar: str = arg(group=my_first_group, mutually_exclusive_group=my_1st_exclusive_group)
    ...
    my_second_group: ClassVar = group(title="Group2", description="Second group description")
    my_2nd_exclusive_group: ClassVar = mutually_exclusive_group(required=True)
    sam: str = arg(group=my_second_group, mutually_exclusive_group=my_2nd_exclusive_group)
    ham: str = arg(group=my_second_group, mutually_exclusive_group=my_2nd_exclusive_group)


make_parser(Args).print_help()


# %% Example 18: Parser defaults https://docs.python.org/3/library/argparse.html#parser-defaults

from dataparsers import parse, default
@dataclass
class Args:
    foo: int
    bar: int = default(42)
    baz: str = default("badger")

parse(Args, ["736"])


# %% Example 19: Subcommands https://docs.python.org/3/library/argparse.html#sub-commands

from typing import ClassVar
from dataparsers import dataparser, arg, subparser, parse


@dataparser(prog="PROG")
class Args:
    foo: bool = arg(help="foo help")
    ...
    a: ClassVar = subparser(help="a help")
    bar: int | None = arg(help="bar help", subparser=a)
    ...
    b: ClassVar = subparser(help="b help")
    baz: str | None = arg(make_flag=True, choices="XYZ", help="baz help", subparser=b)


parse(Args, ["a", "12"])
parse(Args, ["--foo", "b", "--baz", "Z"])

# %% Example 20: Subcommands https://docs.python.org/3/library/argparse.html#sub-commands

from typing import ClassVar
from dataparsers import dataparser, arg, subparser, parse, subparsers


@dataparser(prog="PROG")
class Args:
    foo: bool = arg(help="foo help")
    subparsers_group: str = subparsers(help="sub-command help")
    ...
    a: ClassVar = subparser(help="a help")
    bar: int | None = arg(help="bar help", subparser=a)
    ...
    b: ClassVar = subparser(help="b help")
    baz: str | None = arg(make_flag=True, choices="XYZ", help="baz help", subparser=b)


parse(Args, ["--help"])
# parse(Args, ["a", "--help"])
# parse(Args, ["b", "--help"])

# %% Example 21: Subcommands https://docs.python.org/3/library/argparse.html#sub-commands

from typing import ClassVar
from dataclasses import dataclass
from dataparsers import dataparser, arg, subparser, parse, subparsers, make_parser


@dataclass
class Args:
    subparsers_group: str = subparsers(
        title="subcommands",
        description="valid subcommands",
        help="additional help",
    )
    foo: ClassVar = subparser()
    bar: ClassVar = subparser()


parse(Args, ["-h"])


# %% Example 22: sub-parsers defaults

from typing import ClassVar
from dataclasses import dataclass
from dataparsers import default, subparser, parse


@dataclass
class Args:
    foo: str = default()
    bar: ClassVar = subparser(defaults=dict(foo="spam"))
    baz: ClassVar = subparser(defaults=dict(foo="badger"))


parse(Args, ["bar"])
parse(Args, ["baz"])


# %% Example 23: Using subparser name https://docs.python.org/3/library/argparse.html#sub-commands


from dataclasses import dataclass
from dataparsers import arg, parse, subparser, subparsers

@dataclass
class Args:
    ...
    subparser_name: str = subparsers()
    ...
    s1: ClassVar = subparser()
    x: str = arg("-x", make_flag=False, subparser=s1)
    ...
    s2: ClassVar = subparser()
    y: str = arg(subparser=s2)

parse(Args, ["s2", "frobble"])


# %% Example 24: Partial parsing https://docs.python.org/3/library/argparse.html#partial-parsing


from dataclasses import dataclass
from dataparsers import arg, parse, parse_known, subparser, subparsers


@dataclass
class Args:
    foo: bool
    bar: str


parse_known(Args, ["--foo", "--badger", "BAR", "spam"])


# %% Example 25: Mutually exclusive argument group as ClassVars

from dataclasses import dataclass
from dataparsers import arg, mutually_exclusive_group, make_parser, parse
from typing import ClassVar


@dataclass
class Args:
    my_group: ClassVar = mutually_exclusive_group()
    foo: str = arg(mutually_exclusive_group=my_group)
    bar: str = arg(mutually_exclusive_group=my_group)


make_parser(Args).print_help()

parse(Args, ["--foo", "test", "--bar", "newtest"])
