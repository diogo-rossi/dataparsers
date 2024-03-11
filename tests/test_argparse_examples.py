from __future__ import annotations
import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent.resolve() / "src"
sys.path.insert(0, str(SRC_DIR))

import argparse
from dataclasses import dataclass
from dataparsers import parse, make_parser, dataparser, arg, subparsers, subparser, default, dataparser
from dataparsers import group, mutually_exclusive_group
from resources import HelpDisplay, CapSys
from typing import ClassVar, Any, TypeAlias, Callable


def parse_args_without_sysexit(cls: type, args: list[str]) -> None:
    try:
        parse(cls, args)
    except SystemExit:
        pass


# %% Example: https://docs.python.org/3/library/argparse.html#example


def test_example(capsys: CapSys):
    @dataparser(description="Process some integers.")
    @dataclass
    class Args:
        integers: list[int] = arg(metavar="N", nargs="+", help="an integer for the accumulator")
        accumulate: Callable = arg(
            "--sum", action="store_const", default=max, const=sum, help="sum the integers (default: find the max)"
        )

    make_parser(Args).print_help()
    output_display = HelpDisplay(capsys.readouterr().out)
    assert "N" in output_display.positionals
    assert "--sum" in output_display.flags
    args = parse(Args, "1 2 3 4".split())
    assert args.accumulate(args.integers) == 4
    args = parse(Args, "1 2 3 4 --sum".split())
    assert args.accumulate(args.integers) == 10
    args = parse(Args, ["--sum", "7", "-1", "42"])
    assert args == Args(accumulate=sum, integers=[7, -1, 42])


# %% Subcommands: https://docs.python.org/3/library/argparse.html#sub-commands


def test_subcommands_01(capsys: CapSys):
    @dataparser(prog="PROG")
    @dataclass
    class Args:
        foo: bool = arg(help="foo help")
        subparser_name: str = subparsers(help="sub-command help")
        a: ClassVar = subparser(help="a help")
        bar: int | None = arg(help="bar help", subparser=a)
        b: ClassVar = subparser(help="b help")
        baz: str | None = arg(make_flag=True, choices="XYZ", help="baz help", subparser=b)

    parse_args_without_sysexit(Args, ["-h"])
    output_display = HelpDisplay(capsys.readouterr().out)
    assert "PROG [-h]" in output_display.usage
    assert "a" in output_display.positionals
    assert "b" in output_display.positionals

    parse_args_without_sysexit(Args, ["a", "-h"])
    output_display = HelpDisplay(capsys.readouterr().out)
    assert "PROG a [-h] bar" in output_display.usage
    assert "bar" in output_display.positionals

    parse_args_without_sysexit(Args, ["b", "-h"])
    output_display = HelpDisplay(capsys.readouterr().out)
    assert "PROG b [-h] [--baz {X,Y,Z}]" in output_display.usage
    assert "--baz" in output_display.flags

    args = parse(Args, ["a", "12"])
    assert args.bar == 12
    assert args.foo == False
    assert args == Args(foo=False, subparser_name="a", bar=12, baz=None)

    args = parse(Args, ["--foo", "b", "--baz", "Z"])
    assert args.baz == "Z"
    assert args.foo == True
    assert args == Args(foo=True, subparser_name="b", bar=None, baz="Z")


def test_subcommands_02(capsys: CapSys):
    @dataclass
    class Args:
        subparser_name: str = subparsers(title="subcommands", description="valid subcommands", help="additional help")
        foo: ClassVar = subparser()
        bar: ClassVar = subparser()

    make_parser(Args).print_help()
    output_display = HelpDisplay(capsys.readouterr().out)
    subcommand_section = [s.strip() for s in output_display.get_section("subcommands")]
    assert "valid subcommands" in subcommand_section
    assert any(["additional help" in elem for elem in subcommand_section])


def foo(args):
    return args.x * args.y


def bar(args):
    return "((%s))" % args.z


def test_subcommands_03():

    @dataclass
    class Args:
        func: Callable = default()
        subparsers: str = subparsers(required=True)

        foo: ClassVar = subparser(defaults=dict(func=foo))
        x: int = arg("-x", default=1, make_flag=False, subparser=foo)
        y: float = arg(subparser=foo)

        bar: ClassVar = subparser(defaults=dict(func=bar))
        z: str = arg(subparser=bar)

    args = parse(Args, "foo 1 -x 2".split())
    assert args.func(args) == 2.0

    args = parse(Args, "bar XYZYX".split())
    assert args.func(args) == "((XYZYX))"


def test_subcommands_04():

    @dataclass
    class Args:

        subparser_name: str = subparsers()

        s1: ClassVar = subparser()
        x: str = arg("-x", make_flag=False, subparser=s1)

        s2: ClassVar = subparser()
        y: str = arg(subparser=s2)

    args = parse(Args, ["s2", "frobble"])
    assert args == Args(subparser_name="s2", y="frobble")


# %% Parser defaults: https://docs.python.org/3/library/argparse.html#parser-defaults


def test_parser_defaults_01():
    @dataclass
    class Args:
        foo: int
        bar: int = default(42)
        baz: str = default("badger")

    assert parse(Args, ["736"]) == Args(foo=736, bar=42, baz="badger")


def test_parser_defaults_02():  # this test does not make much sense
    @dataclass
    class Args:
        foo: str = arg(default="bar")
        foo: str = default("spam")

    assert parse(Args, []) == Args(foo="spam")


# %% Argument groups: https://docs.python.org/3/library/argparse.html#argument-groups


def test_argument_groups_01(capsys: CapSys):

    parser = argparse.ArgumentParser(prog="PROG", add_help=False)
    group = parser.add_argument_group("group")
    group.add_argument("--foo", help="foo help")
    group.add_argument("bar", help="bar help")
    parser.print_help()
    argparse_help = capsys.readouterr().out

    @dataparser(prog="PROG", add_help=False)
    class Args:
        group: ClassVar = group(title="group")
        foo: str = arg(make_flag=True, help="foo help", group=group)
        bar: str = arg(help="bar help", group=group)

    make_parser(Args).print_help()
    dataparsers_help = capsys.readouterr().out

    assert dataparsers_help == argparse_help

    output = HelpDisplay(dataparsers_help)
    assert "PROG [--foo FOO] bar" in output.usage
    assert any(["--foo" in a for a in output.get_section("group")])
    assert any(["bar" in a for a in output.get_section("group")])


def test_argument_group_02(capsys: CapSys):
    parser = argparse.ArgumentParser(prog="PROG", add_help=False)
    group1 = parser.add_argument_group("group1", "group1 description")
    group1.add_argument("foo", help="foo help")
    group2 = parser.add_argument_group("group2", "group2 description")
    group2.add_argument("--bar", help="bar help")
    parser.print_help()
    argparse_help = capsys.readouterr().out

    @dataparser(prog="PROG", add_help=False)
    class Args:
        group1: ClassVar = group("group1", "group1 description")
        group2: ClassVar = group("group2", "group2 description")
        foo: str = arg(help="foo help", group=group1)
        bar: str = arg(make_flag=True, help="bar help", group=group2)

    make_parser(Args).print_help()
    dataparsers_help = capsys.readouterr().out

    assert dataparsers_help == argparse_help
