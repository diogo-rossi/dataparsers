# %%
from __future__ import annotations  # necessary to annotate functions

import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent.resolve() / "src"
sys.path.insert(0, str(SRC_DIR))


from typing import ClassVar, Callable
from dataclasses import dataclass
from dataparsers import arg, parse, subparser, default, subparsers


# sub-command functions
def foo(args: Args):
    print(args.x * args.y)


def bar(args: Args):
    print("((%s))" % args.z)


@dataclass
class Args:
    func: Callable = default()
    ...
    # parser for the "foo" command
    foo: ClassVar = subparser(defaults=dict(func=foo))
    x: int = arg("-x", default=1, make_flag=False, subparser=foo)
    y: float = arg(subparser=foo)
    ...
    # parser for the "bar" command
    bar: ClassVar = subparser(defaults=dict(func=bar))
    z: str = arg(subparser=bar)


# parse the args and call whatever function was selected
args = parse(Args, "foo 1 -x 2".split())
args.func(args)

# parse the args and call whatever function was selected
args = parse(Args, "bar XYZYX".split())
args.func(args)
