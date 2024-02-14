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

# %% Example 1


@dataclass
class Args1:
    foo: str
    bar: int = 42


args = parse(Args1)
print("Printing `args`:")
print(args)


# %% Example 2


@dataclass
class Args2:
    foo: str = arg(help="foo help")
    bar: int = arg(default=42, help="bar help")


args = parse(Args2)


# %% Example 3


@dataclass
class Args3:
    foo: str = arg(help="foo help")
    bar: int = arg("-b", default=42, help="bar help")


args = parse(Args3)


# %% Example 4


@dataclass
class Args4:
    bar: int = arg("--bar", default=42, nargs="?", help="bar help")


args = parse(Args4)


# %% Example 5


@dataclass
class Args5:
    bar: int = arg(default=42, nargs="?", help="bar help", make_flag=True)


args = parse(Args5)


# %% Example 6


@dataclass
class Args6:
    bar: int = arg("-b", default=42, help="bar help", make_flag=False)


args = parse(Args6)


# %% Example 7


@dataclass
class Args7:
    path: str = arg("-f", "--file-output", metavar="<filepath>", help="Text file to write output")


args = parse(Args7)
print(args)

# %% Example 8


@dataclass
class Args8:
    foo: str = arg(group_title="The 1st group")
    bar: str = arg(group_title="The 1st group")
    sam: str = arg(group_title="The 2nd group")
    ham: str = arg(group_title="The 2nd group")


parser = make_parser(Args8)
parser.print_help()


# %% Example 9


@dataclass
class Args9:
    foo: str = arg(mutually_exclusive_group_id="my_group")
    bar: str = arg(mutually_exclusive_group_id="my_group")


parser = make_parser(Args9)
parser.print_help()

# %% Example 10


@dataclass
class Args10:
    foo: bool = arg(action="store_true", mutually_exclusive_group_id="my_group")
    bar: bool = arg(action="store_false", mutually_exclusive_group_id="my_group")


parse(Args10, ["--foo"])
parse(Args10, ["--bar"])
parse(Args10, ["--foo", "--bar"])
