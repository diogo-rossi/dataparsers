import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent.resolve() / "src"
sys.path.insert(0, str(SRC_DIR))

from dataclasses import dataclass
from dataparsers import parse, make_parser, dataparser
from dataparsers import arg, subparsers, subparser
from resources import HelpDisplay, CapSys
from typing import ClassVar, Any, TypeAlias


def parse_args_without_sysexit(cls: type, args: list[str]) -> None:
    try:
        parse(cls, args)
    except SystemExit:
        pass


def test_subcommands_01(capsys: CapSys):
    @dataparser(prog="PROG")
    @dataclass
    class Args:
        foo: bool = arg(help="foo help")
        subparser_name: str = subparsers(help="sub-command help")
        a: ClassVar = subparser(help="a help")
        bar: int = arg(help="bar help", subparser=a)
        b: ClassVar = subparser(help="b help")
        baz: str = arg(make_flag=True, choices="XYZ", help="baz help", subparser=b)

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
    # assert "additional help" in subcommand_section
