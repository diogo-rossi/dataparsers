from __future__ import annotations

import os
import sys
import pytest

# add `src` folder to the `sys.path`, relative to the CWD
sys.path.insert(0, os.path.abspath("./src"))

from dataclasses import dataclass, fields
from dataparsers import arg, dataparser, parse, make_parser
from dataparsers import group, mutually_exclusive_group
from resources import HelpDisplay, CapSys
from typing import ClassVar


def test_00_only_positionals(capsys: CapSys):
    @dataclass
    class Args:
        string: str
        integer: int

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    positionals = HelpDisplay(output).positionals
    assert all(name in positionals for name in [f.name for f in fields(Args)])


def test_01_with_one_flag(capsys: CapSys):
    @dataclass
    class Args:
        string: str
        integer: int
        foo: str = "test"

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    flags = HelpDisplay(output).flags
    assert "--foo" in flags


def test_02_with_defaults_and_helps(capsys: CapSys):
    @dataclass
    class Args:
        string: str = arg(help="This must be a string")
        integer: int = arg(default=1, help="This is a integer")

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    output = HelpDisplay(output)
    positionals = output.positionals
    flags = output.flags
    assert "string" in positionals
    assert "--integer" in flags


def test_03_automatic_make_flags(capsys: CapSys):
    @dataclass
    class Args:
        string: str = arg("-s")
        integer: int = arg("-i")

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    flags = HelpDisplay(output).flags
    assert all(name in flags for name in ["-s", "-i"])
    assert all(name in flags for name in ["--string", "--integer"])


def test_04_with_one_group(capsys: CapSys):
    @dataclass
    class Args:
        MyGroup: ClassVar = group("group1")
        string: str = arg(group=MyGroup)
        integer: int = arg(group=MyGroup)

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    g = HelpDisplay(output).group("group1")
    assert all(name in g for name in [f.name for f in fields(Args)])


def test_05_with_one_group_with_one_flag(capsys: CapSys):
    @dataclass
    class Args:
        MyGroup: ClassVar = group("group1")
        string: str = arg(group=MyGroup)
        integer: int = arg(group=MyGroup, make_flag=True)

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    g = HelpDisplay(output).group("group1")
    assert all(name in g for name in ["string", "--integer"])


def test_06_with_multually_exclusive_groups(capsys: CapSys):
    @dataclass
    class Args:
        string: str = arg(mutually_exclusive_group=1)
        integer: int = arg(mutually_exclusive_group=1)

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    flags = HelpDisplay(output).flags
    assert all(name in flags for name in ["--string", "--integer"])


def test_07_with_required_multually_exclusive_groups_and_no_given_flags(capsys: CapSys):
    @dataparser
    class Args:
        MyGroup: ClassVar = mutually_exclusive_group(required=True)
        string: str = arg(mutually_exclusive_group=MyGroup)
        integer: int = arg(mutually_exclusive_group=MyGroup)

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    flags = HelpDisplay(output).flags
    assert all(name in flags for name in ["--string", "--integer"])


def test_08_with_required_multually_exclusive_groups_and_given_single_flags(capsys: CapSys):
    @dataparser
    class Args:
        MyGroup: ClassVar = mutually_exclusive_group(required=True)
        string: str = arg("-s", mutually_exclusive_group=MyGroup)
        integer: int = arg("-i", mutually_exclusive_group=MyGroup)

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    flags = HelpDisplay(output).flags
    assert all(name in flags for name in ["--string", "--integer"])


def test_09_forced_make_flags(capsys: CapSys):
    @dataclass
    class Args:
        string: str = arg("-s", "--str", make_flag=True)
        integer: int = arg("-i", "--int", make_flag=True)

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    flags = HelpDisplay(output).flags
    assert all(name in flags for name in ["--string", "--integer"])


def test_10_mutually_exclusive_group_with_wrong_input(capsys: CapSys):
    @dataparser
    class Args:
        MyGroup: ClassVar = mutually_exclusive_group(required=True)
        string: str = arg("-s", mutually_exclusive_group=MyGroup)
        integer: int = arg("-i", mutually_exclusive_group=MyGroup)

    with pytest.raises(SystemExit) as excinfo:
        parse(Args, "-s name -i 36".split())
    assert excinfo.value.code == 2
    output = capsys.readouterr().err
    assert "not allowed with argument" in output
    assert "-i/--integer" in output
    assert "-s/--string" in output


def test_11_groupTitle_togetherWith_mutuallyExclusiveGroup(capsys: CapSys):
    @dataclass
    class Args:
        meg: ClassVar = mutually_exclusive_group()
        sam: str = arg(group_title="Group1", mutually_exclusive_group=meg)
        ham: str = arg(group_title="Group1", mutually_exclusive_group=meg)
        foo: str = arg(group_title="Group2", mutually_exclusive_group=meg)
        bar: str = arg(group_title="Group2", mutually_exclusive_group=meg)

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    g = HelpDisplay(output).group("Group1")
    assert all(name in g for name in ["--sam", "--ham", "--foo", "--bar"])


def test_12_groupTitle_togetherWith_mutuallyExclusiveGroupId(capsys: CapSys):
    @dataclass
    class Args:
        sam: str = arg(group_title="Group1", mutually_exclusive_group_id="meg")
        ham: str = arg(group_title="Group1", mutually_exclusive_group_id="meg")
        foo: str = arg(group_title="Group2", mutually_exclusive_group_id="meg")
        bar: str = arg(group_title="Group2", mutually_exclusive_group_id="meg")

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    g = HelpDisplay(output).group("Group1")
    assert all(name in g for name in ["--sam", "--ham", "--foo", "--bar"])


def test_13_group_togetherWith_mutuallyExclusiveGroup(capsys: CapSys):
    @dataclass
    class Args:
        g1: ClassVar = group("Group1")
        meg: ClassVar = mutually_exclusive_group()
        sam: str = arg(group=g1, mutually_exclusive_group=meg)
        ham: str = arg(group=g1, mutually_exclusive_group=meg)
        foo: str = arg(group=g1, mutually_exclusive_group=meg)
        bar: str = arg(group=g1, mutually_exclusive_group=meg)

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    g = HelpDisplay(output).group("Group1")
    assert all(name in g for name in ["--sam", "--ham", "--foo", "--bar"])


def test_14_group_togetherWith_mutuallyExclusiveGroupId(capsys: CapSys):
    @dataclass
    class Args:
        g1: ClassVar = group("Group1")
        sam: str = arg(group=g1, mutually_exclusive_group_id="meg")
        ham: str = arg(group=g1, mutually_exclusive_group_id="meg")
        foo: str = arg(group=g1, mutually_exclusive_group_id="meg")
        bar: str = arg(group=g1, mutually_exclusive_group_id="meg")

    parser = make_parser(Args)
    parser.print_help()
    output = capsys.readouterr().out
    g = HelpDisplay(output).group("Group1")
    assert all(name in g for name in ["--sam", "--ham", "--foo", "--bar"])
