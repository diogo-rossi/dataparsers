# %% Setup

import sys, os
from pathlib import Path

THIS_DIR = Path(__file__).absolute().parent
ROOT_DIR = THIS_DIR.parent
SRC_DIR = Path(f"{ROOT_DIR}/src")
sys.path.insert(0, str(SRC_DIR))

# %% Imports

from dataclasses import dataclass
from dataparsers import arg, make_parser, dataparser

# %% Example 1


@dataclass
class Arg1:
    foo: str = arg(default=42)
    bar: int = arg()


parser = make_parser(Arg1)
parser.print_help()


# %% Example 2


@dataclass
class Arg2:
    foo: str = arg("-f")
    bar: str = arg("-b")


parser = make_parser(Arg2)
parser.print_help()


# %% Example 3


@dataclass
class Arg3:
    foo: str = arg(default=42)
    bar: int = arg()


parser = make_parser(Arg3)
parser.print_help()


# %% Example 4


@dataclass
class Arg4:
    foo: str = arg(group_title="group", help="foo help", make_flag=True)
    bar: str = arg(group_title="group", help="bar help")


parser = make_parser(Arg4)
parser.print_help()


# %% Example 5


@dataparser(groups_descriptions={"group1": "group1 description", "group2": "group2 description"})
class Arg5:
    foo: str = arg(group_title="group1", help="foo help")
    bar: str = arg(group_title="group2", help="bar help", make_flag=True)


parser = make_parser(Arg5)
parser.print_help()
