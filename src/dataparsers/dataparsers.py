# %% ################################################# dataparsers region ######################################################
import gettext
import shutil
import sys
import textwrap
from argparse import _ArgumentGroup  # only for typing annotation
from argparse import ArgumentParser, RawTextHelpFormatter, _MutuallyExclusiveGroup, _SubParsersAction
from collections.abc import Mapping
from dataclasses import Field, dataclass, field, fields, is_dataclass
from types import MappingProxyType, UnionType
from typing import Any, Callable, ClassVar, Sequence, TypeVar, Union, cast, get_args, get_origin, get_type_hints, overload

Class = TypeVar("Class", covariant=True)

_ = gettext.gettext


def arg(
    *name_or_flags: str,
    group: Field[Any] | int | str | None = None,
    mutually_exclusive_group: Field[Any] | int | str | None = None,
    subparser: Field[Any] | None = None,
    group_title: str | int | None = None,
    mutually_exclusive_group_id: str | int | None = None,
    make_flag: bool | None = None,
    **kwargs,
) -> Any:
    is_flag = False

    if name_or_flags:
        if not all(n.startswith("-") for n in name_or_flags):
            raise ValueError(
                "The argument `name_or_flags` should be passed to function `arg` only if it is a flag (starts with `-`)"
            )
        if not any(n.startswith("--") for n in name_or_flags) and make_flag is None:
            make_flag = True
        is_flag = True

    if "dest" in kwargs:
        raise ValueError("The argument `dest` is not necessary")

    if "default" in kwargs and not kwargs.get("nargs", None) in ["?", "*"] and not is_flag:
        make_flag = True

    default = kwargs.pop("default", None)

    if not is_flag and mutually_exclusive_group_id is not None or mutually_exclusive_group is not None:
        make_flag = True

    make_flag = bool(make_flag)
    is_flag = is_flag or make_flag

    metadict = {
        "name_or_flags": name_or_flags,
        "group": group,
        "mutually_exclusive_group": mutually_exclusive_group,
        "subparser": subparser,
        "group_title": group_title,
        "mutually_exclusive_group_id": mutually_exclusive_group_id,
        "is_flag": is_flag,
        "make_flag": make_flag,
        "argument_kwargs": kwargs,
    }

    metadict = {key: value for key, value in metadict.items() if value is not None}

    return field(default=default, metadata=metadict)


def group(*args, **kwargs) -> Any:
    argument_group_kwargs = dict(**{k: v for k, v in zip(["title", "description"], args)}, **kwargs)
    return field(metadata={"argument_group_kwargs": argument_group_kwargs})


def mutually_exclusive_group(**kwargs) -> Any:
    return field(metadata={"mutually_exclusive_group_kwargs": kwargs})


def subparsers(**kwargs) -> Any:
    if "dest" in kwargs:
        raise ValueError("The argument `dest` is not necessary")
    return field(default=None, metadata={"is_subparsers_group": True, "subparsers_group_kwargs": kwargs})


@dataclass(frozen=True)
class SubParser:
    defaults: dict[str, Any] | None
    kwargs: Mapping[str, Any]


def subparser(*, defaults: dict[str, Any] | None = None, **kwargs) -> Any:
    return field(default=SubParser(defaults=defaults, kwargs=MappingProxyType(kwargs)))


def default(default=None):
    return field(default=default, metadata={"is_post_default": True})


@overload
def dataparser(cls: type[Class]) -> type[Class]: ...


@overload
def dataparser(
    *,
    groups_descriptions: dict[str | int, str] | None = None,
    required_mutually_exclusive_groups: dict[str | int, bool] | None = None,
    default_bool: bool = False,
    help_formatter: Callable[[str], str] | None = None,
    **kwargs,
) -> Callable[[type[Class]], type[Class]]: ...


def dataparser(
    cls: type[Class] | None = None,
    *,
    groups_descriptions: dict[str | int, str] | None = None,
    required_mutually_exclusive_groups: dict[str | int, bool] | None = None,
    default_bool: bool = False,
    help_formatter: Callable[[str], str] | None = None,
    **kwargs,
) -> type[Class] | Callable[[type[Class]], type[Class]]:
    if cls is not None:
        cls = cast(type[Class], cls)
        return dataclass(cls) if not is_dataclass(cls) else cls

    if groups_descriptions is None:
        groups_descriptions = {}

    if required_mutually_exclusive_groups is None:
        required_mutually_exclusive_groups = {}

    def wrap(cls: type[Class]) -> type[Class]:
        cls = dataclass(cls) if not is_dataclass(cls) else cls
        setattr(
            cls,
            "__dataparsers_params__",
            (kwargs, groups_descriptions, required_mutually_exclusive_groups, default_bool, help_formatter),
        )
        return cls

    return wrap


def make_parser(cls: type, *, parser: ArgumentParser | None = None) -> ArgumentParser:
    kwargs, groups_descriptions, required_groups_status, default_bool, help_formatter = getattr(
        cls, "__dataparsers_params__", ({}, {}, {}, False, None)
    )

    if parser is None:
        if help_formatter is not None and "formatter_class" not in kwargs:
            kwargs["formatter_class"] = RawTextHelpFormatter
        parser = ArgumentParser(**kwargs)

    help_formatter = help_formatter or str
    groups: dict[str | int, _ArgumentGroup] = {}
    mutually_exclusive_groups: dict[str | int, _MutuallyExclusiveGroup] = {}
    subparsers: dict[str, ArgumentParser] = {}
    subparsers_group: _SubParsersAction | None = None

    for fld in fields(cls):
        if fld.metadata.get("is_subparsers_group", False):
            subparsers_group_kwargs = fld.metadata.get("subparsers_group_kwargs", {})
            subparsers_group_kwargs.pop("dest", None)
            subparsers_group = parser.add_subparsers(dest=fld.name, **subparsers_group_kwargs)

    handler = parser
    classvars = {k: v for (k, v) in get_type_hints(cls).items() if v == ClassVar or get_origin(v) is ClassVar}
    for field_name in classvars:
        if hasattr(cls, field_name):
            attr = getattr(cls, field_name)
            if isinstance(attr, SubParser):
                subparsers_kwargs = attr.kwargs
                subparser_defaults = attr.defaults
                if subparsers_group is None:
                    subparsers_group = handler.add_subparsers()
                if field_name not in subparsers:
                    subparsers[field_name] = subparsers_group.add_parser(field_name, **subparsers_kwargs)
                    if subparser_defaults is not None:
                        subparsers[field_name].set_defaults(**subparser_defaults)

    for fld in fields(cls):
        if type(fld.type) == str:
            fld.type = eval(fld.type)
        if get_origin(fld.type) is list or (get_origin(fld.type) in [Union, UnionType] and type(None) in get_args(fld.type)):
            fld.type = [a for a in get_args(fld.type) if a is not type(None)][0]
        if get_origin(fld.type) is Callable or not callable(fld.type):
            fld.type = None

        if fld.metadata.get("is_subparsers_group", False):
            continue

        if fld.metadata.get("is_post_default", False):
            parser.set_defaults(**{fld.name: fld.default})
            continue

        argument_kwargs = fld.metadata.get("argument_kwargs", {})

        if "help" in argument_kwargs:
            argument_kwargs["help"] = help_formatter(argument_kwargs["help"])

        arg_field_has_default = fld.default is not fld.default_factory
        make_flag = fld.metadata.get("make_flag", True)
        name_or_flags = fld.metadata.get("name_or_flags", ())
        if (arg_field_has_default and fld.metadata.get("is_flag", True)) or fld.type == bool:
            if make_flag or (fld.type == bool and not name_or_flags):
                name_or_flags += (f'--{fld.name.replace("_", "-")}',)
            if fld.type == bool and (not arg_field_has_default or fld.default is None):
                fld.default = default_bool

        if not name_or_flags:  # no flag arg
            name_or_flags = (fld.name,)
        else:  # flag arg
            argument_kwargs["dest"] = fld.name

        if "type" not in argument_kwargs and fld.type != bool:
            argument_kwargs["type"] = fld.type

        if "action" not in argument_kwargs and fld.type == bool:
            argument_kwargs["action"] = "store_false" if fld.default else "store_true"

        if fld.type == bool:
            fld.default = argument_kwargs["action"] == "store_false"

        if argument_kwargs.get("action", None) in ["store_const", "store_true", "store_false", "help"]:
            argument_kwargs.pop("type", None)

        group_id: str | int | None = fld.metadata.get("group_title", None)
        exclusive_group_id: str | int | None = fld.metadata.get("mutually_exclusive_group_id", None)

        group: Field | int | str | None = fld.metadata.get("group", None)
        mutually_exclusive_group: Field | int | str | None = fld.metadata.get("mutually_exclusive_group", None)
        subparser: Field | None = fld.metadata.get("subparser", None)
        if any(id is not None for id in [group_id, exclusive_group_id, group, mutually_exclusive_group, subparser]):

            handler = parser

            if subparser is not None:
                handler = subparsers[subparser.name]

            if group is not None:
                group_kwargs = {}
                if type(group) is Field:
                    group_name = group.name
                    group_kwargs = group.metadata.get("argument_group_kwargs", {})
                if type(group) is str or type(group) is int:
                    group_name = group
                if type(group) is str:
                    group_kwargs = {"title": group}
                if group_name not in groups:
                    groups[group_name] = handler.add_argument_group(**group_kwargs)

                handler = groups[group_name]

            if mutually_exclusive_group is not None:
                group_kwargs = {}
                if type(mutually_exclusive_group) is Field:
                    group_name = mutually_exclusive_group.name
                    group_kwargs = mutually_exclusive_group.metadata.get("mutually_exclusive_group_kwargs", {})
                if type(mutually_exclusive_group) is str or type(mutually_exclusive_group) is int:
                    group_name = mutually_exclusive_group
                if group_name not in mutually_exclusive_groups:
                    mutually_exclusive_groups[group_name] = handler.add_mutually_exclusive_group(**group_kwargs)

                handler = mutually_exclusive_groups[group_name]

            if group_id is not None:
                if group_id not in groups:
                    groups[group_id] = parser.add_argument_group(
                        title=group_id if type(group_id) == str else None,
                        description=groups_descriptions.get(group_id, None),
                    )

                handler = groups[group_id]

            if exclusive_group_id is not None:

                if exclusive_group_id not in mutually_exclusive_groups:
                    mutually_exclusive_groups[exclusive_group_id] = handler.add_mutually_exclusive_group(
                        required=required_groups_status.get(exclusive_group_id, False),
                    )

                handler = mutually_exclusive_groups[exclusive_group_id]

            handler.add_argument(*name_or_flags, default=fld.default, **argument_kwargs)

        else:
            parser.add_argument(*name_or_flags, default=fld.default, **argument_kwargs)

    return parser


def parse(cls: type[Class], args: Sequence[str] | None = None, *, parser: ArgumentParser | None = None) -> Class:
    return cls(**vars(make_parser(cls, parser=parser).parse_args(args)))


def parse_known(
    cls: type[Class], args: Sequence[str] | None = None, *, parser: ArgumentParser | None = None, metavar: str | None = None
) -> tuple[Class, list[str]]:
    parser = make_parser(cls, parser=parser)
    if metavar is not None:
        parser.usage = f"{parser.format_usage().strip().replace('usage: ','')} [{metavar}]\n"
        if parser.epilog is None:
            parser.epilog = ""
        parser.formatter_class = RawTextHelpFormatter
        parser.epilog = _(f"  {metavar.ljust(19)}Extra remaining unknown arguments.") + parser.epilog
    arguments, remaining_arguments = parser.parse_known_args(args)
    return cls(**vars(arguments)), remaining_arguments


def write_help(
    text: str,
    width: int | None = None,
    space: int = 24,
    dedent: bool = True,
    final_newlines: bool = True,
) -> str:
    width = width or shutil.get_terminal_size().columns
    lines = []
    for line in text.splitlines():
        line = textwrap.dedent(line) if dedent else line
        lines.append(textwrap.fill(text=line, width=width - space, replace_whitespace=False))

    return "\n".join(lines) + ("\n\n" if final_newlines else "")


# %% ###########################################################################################################################
