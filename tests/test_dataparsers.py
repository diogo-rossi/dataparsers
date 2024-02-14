import os
import sys

# add `src` folder to the `sys.path`, relative to the CWD
sys.path.insert(0, os.path.abspath("./src"))

from pytest import fixture
from dataclasses import dataclass, fields
from argparse import ArgumentParser
from dataparsers import arg, dataparser, parse
from typing import Protocol, Literal


class OutErr(Protocol):
    out: str
    err: str


class CapSys(Protocol):
    def readouterr(self) -> OutErr: ...


def get_options(helptxt: str):
    txtlines = helptxt.splitlines()


@fixture
def parser():
    return ArgumentParser()


def test_only_positionals(capsys: CapSys, parser: ArgumentParser):
    @dataclass
    class Args:
        string: str
        integer: int

    parse(Args, ["test", "10"], parser=parser)
    parser.print_help()
    output = capsys.readouterr().out
    assert all(name in HelpOutput(output).positionals for name in [f.name for f in fields(Args)])


def test_with_one_flag(capsys: CapSys, parser: ArgumentParser):
    @dataclass
    class Args:
        string: str
        integer: int
        foo: str = "test"

    parse(Args, ["test", "10"], parser=parser)
    parser.print_help()
    output = capsys.readouterr().out
    assert "--foo" in HelpOutput(output).flags


def test_with_one_group(capsys: CapSys, parser: ArgumentParser):
    @dataclass
    class Args:
        string: str = arg(group=1)
        integer: int = arg(group=1)

    parse(Args, ["test", "10"], parser=parser)
    parser.print_help()
    output = capsys.readouterr().out
    group = HelpOutput(output).group("1")
    assert all(name in group for name in [f.name for f in fields(Args)])


def test_with_one_group_with_one_flag(capsys: CapSys, parser: ArgumentParser):
    @dataclass
    class Args:
        string: str = arg(group=1)
        integer: int = arg(group=1, make_flag=True)

    parse(Args, ["test"], parser=parser)
    parser.print_help()
    output = capsys.readouterr().out
    group = HelpOutput(output).group("1")
    assert all(name in group for name in ["string", "--integer"])


def test_with_multually_exclusive_groups(capsys: CapSys, parser: ArgumentParser):
    @dataclass
    class Args:
        string: str = arg(mutually_exclusive_group=1)
        integer: int = arg(mutually_exclusive_group=1)

    parse(Args, ["--string", "test"], parser=parser)
    parser.print_help()
    output = capsys.readouterr().out
    flags = HelpOutput(output).flags
    assert all(name in flags for name in ["--string", "--integer"])


def test_with_required_multually_exclusive_groups_and_no_given_flags(capsys: CapSys, parser: ArgumentParser):
    @dataparser(required_mutually_exclusive_groups={1: True})
    class Args:
        string: str = arg(mutually_exclusive_group=1)
        integer: int = arg(mutually_exclusive_group=1)

    parse(Args, ["--string", "test"], parser=parser)
    parser.print_help()
    output = capsys.readouterr().out
    flags = HelpOutput(output).flags
    assert all(name in flags for name in ["--string", "--integer"])


def test_with_required_multually_exclusive_groups_and_given_single_flags(capsys: CapSys, parser: ArgumentParser):
    @dataparser(required_mutually_exclusive_groups={1: True})
    class Args:
        string: str = arg("-s", mutually_exclusive_group=1)
        integer: int = arg("-i", mutually_exclusive_group=1)

    parse(Args, ["--string", "test"], parser=parser)
    parser.print_help()
    output = capsys.readouterr().out
    flags = HelpOutput(output).flags
    assert all(name in flags for name in ["--string", "--integer"])


def test_automatic_make_flags(capsys: CapSys, parser: ArgumentParser):
    @dataclass
    class Args:
        string: str = arg("-s")
        integer: int = arg("-i")

    parse(Args, ["--string", "test"], parser=parser)
    parser.print_help()
    output = capsys.readouterr().out
    flags = HelpOutput(output).flags
    assert all(name in flags for name in ["--string", "--integer"])


def test_forced_make_flags(capsys: CapSys, parser: ArgumentParser):
    @dataclass
    class Args:
        string: str = arg("-s", "--str", make_flag=True)
        integer: int = arg("-i", "--int", make_flag=True)

    parse(Args, ["--string", "test"], parser=parser)
    parser.print_help()
    output = capsys.readouterr().out
    flags = HelpOutput(output).flags
    assert all(name in flags for name in ["--string", "--integer"])


# %% Help output handler


@dataclass
class HelpOutput:
    help_text: str

    def __post_init__(self):
        self.text_lines = self.help_text.splitlines()
        self.usage = self.get_usage()
        self.positionals = self.get_positionals()
        self.flags = self.get_flags()

    def get_usage(self) -> str:
        try:
            return [line for line in self.text_lines if line.startswith("usage:")][0]
        except IndexError:
            return ""

    def get_section(self, title: str) -> list[str]:
        try:
            start = self.text_lines.index([line for line in self.text_lines if line.strip().startswith(title)][0]) + 1
            end = start + self.text_lines[start:].index("") if "" in self.text_lines[start:] else None
            lines = []
            for line in self.text_lines[start:]:
                if not (line.startswith(" ") or line == ""):
                    break
                lines.append(line)
            return lines
        except IndexError:
            return []

    def get_positionals(self) -> list[str]:
        return [arg.strip() for arg in self.get_section("positional arguments:")]

    def get_flags(self) -> list[str]:
        flags = []
        for line in self.get_section("options:"):
            if line:
                for part in line.split(","):
                    flags.append(part.strip().split()[0])
        return flags

    def group(self, group_id) -> list[str]:
        args = []
        for line in self.get_section(f"{group_id}:"):
            if line:
                for part in line.split(","):
                    args.append(part.strip().split()[0])
        return args
