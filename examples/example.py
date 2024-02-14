# %% Setup

import sys, os
from pathlib import Path

THIS_DIR = Path(__file__).absolute().parent
ROOT_DIR = THIS_DIR.parent
SRC_DIR = Path(f"{ROOT_DIR}/src")
sys.path.insert(0, str(SRC_DIR))

# %% Imports

from dataclasses import dataclass
from dataparsers import arg, make_parser, dataparser, parse

# %% Example 1: Basic usage


@dataclass
class Args1:
    foo: str
    bar: int = 42


args = parse(Args1)
print("Printing `args`:")
print(args)


# %% Example 2: Argument specification


@dataclass
class Args2:
    foo: str = arg(help="foo help")
    bar: int = arg(default=42, help="bar help")


args = parse(Args2)


# %% Example 3: Aliases


@dataclass
class Args3:
    foo: str = arg(help="foo help")
    bar: int = arg("-b", default=42, help="bar help")


args = parse(Args3)


# %% Example 4: Automatic flag creation


@dataclass
class Args4:
    bar: int = arg("--bar", default=42, nargs="?", help="bar help")


args = parse(Args4)


# %% Example 5: Automatic flag creation


@dataclass
class Args5:
    bar: int = arg(default=42, nargs="?", help="bar help", make_flag=True)


args = parse(Args5)


# %% Example 6: Avoiding automatic flag creation


@dataclass
class Args6:
    bar: int = arg("-b", default=42, help="bar help", make_flag=False)


args = parse(Args6)


# %% Example 7: Booleans


@dataclass
class Args7:
    bar: bool


make_parser(Args7).print_help()
parse(Args7, [])

# %% Example 8: Decoupling code from the command line interface


@dataclass
class Args8:
    path: str = arg("-f", "--file-output", metavar="<filepath>", help="Text file to write output")


args = parse(Args8)
print(args)

# %% Example 9: Argument groups


@dataclass
class Args9:
    foo: str = arg(group_title="The 1st group")
    bar: str = arg(group_title="The 1st group")
    sam: str = arg(group_title="The 2nd group")
    ham: str = arg(group_title="The 2nd group")


parser = make_parser(Args9)
parser.print_help()


# %% Example 10: Mutually exclusive argument group


@dataclass
class Args10:
    foo: str = arg(mutually_exclusive_group_id="my_group")
    bar: str = arg(mutually_exclusive_group_id="my_group")


parser = make_parser(Args10)
parser.print_help()

# %% Example 11: Parser specifications


@dataparser(prog="MyProgram", description="A foo that bars")
class Args11: ...


make_parser(Args11).print_help()

# %% Example 12: Groups `description` and `required` status


@dataparser(
    groups_descriptions={"Group1": "Description for 1st group", "Group2": "Description for 2nd group"},
    required_mutually_exclusive_groups={0: True, 1: False},
    add_help=False,  # Disable automatic addition of `-h` or `--help` at the command line
)
class Args12:
    foo: str = arg(group_title="Group1", mutually_exclusive_group_id=0)
    bar: int = arg(group_title="Group1", mutually_exclusive_group_id=0)
    sam: bool = arg(group_title="Group2", mutually_exclusive_group_id=1)
    ham: float = arg(group_title="Group2", mutually_exclusive_group_id=1)


make_parser(Args12).print_help()


# %% Example 13: Default for booleans


@dataparser(default_bool=False)
class Args13:
    foo: bool


parse(Args13, ["--foo"])


@dataparser(default_bool=True)
class Args:
    foo: bool = arg(help="Boolean value")


parse(Args, ["--foo"])
