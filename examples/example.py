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


# prog.py
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
    foo: str = arg(help="foo help")
    bar: int = arg("-b", "--bar", default=42, nargs="?", help="bar help")

args = parse(Args4)



# %% Example 5


@dataclass
class Args5:
    foo: str = arg(help="foo help")
    bar: int = arg("-b", default=42, help="bar help", make_flag=False)

args = parse(Args5)


# %% Example 5


@dataparser(groups_descriptions={"group1": "group1 description", "group2": "group2 description"})
class Arg5:
    foo: str = arg(group_title="group1", help="foo help")
    bar: str = arg(group_title="group2", help="bar help", make_flag=True)


parser = make_parser(Arg5)
parser.print_help()


# %% Example 6


@dataclass
class Args:
    foo: bool = arg(action="store_true", mutually_exclusive_group_id=1)
    bar: bool = arg(action="store_false", mutually_exclusive_group_id=1)


parse(Args, "--foo", "--bar")
# parser.print_help()
