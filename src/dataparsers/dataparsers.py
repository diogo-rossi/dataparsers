# %% ################################################# dataparsers region ######################################################
import os, textwrap
from dataclasses import dataclass, field, fields
from argparse import ArgumentParser, RawTextHelpFormatter
from argparse import _MutuallyExclusiveGroup, _ArgumentGroup  # only for typing annotation
from typing import Any, TypeVar, Sequence, Callable, overload

Class = TypeVar("Class", covariant=True)


def arg(
    *name_or_flags: str,
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

    if not is_flag and mutually_exclusive_group_id is not None:
        make_flag = True

    make_flag = bool(make_flag)
    is_flag = is_flag or make_flag

    metadict = dict(
        name_or_flags=name_or_flags,
        group_title=group_title,
        mutually_exclusive_group_id=mutually_exclusive_group_id,
        is_flag=is_flag,
        make_flag=make_flag,
        **kwargs,
    )

    metadict = {key: value for key, value in metadict.items() if value is not None}

    return field(default=default, metadata=metadict)


@overload
def dataparser(cls: type[Class]) -> type[Class]: ...


@overload
def dataparser(
    *,
    groups_descriptions: dict[str | int, str] | None = None,
    required_mutually_exclusive_groups: dict[str | int, bool] | None = None,
    default_bool: bool = False,
    **kwargs,
) -> Callable[[type[Class]], type[Class]]: ...


def dataparser(
    cls: type[Class] | None = None,
    *,
    groups_descriptions: dict[str | int, str] | None = None,
    required_mutually_exclusive_groups: dict[str | int, bool] | None = None,
    default_bool: bool = False,
    help_fmt: Callable[[str], str] | None = None,
    **kwargs,
) -> type[Class] | Callable[[type[Class]], type[Class]]:
    if cls is not None:
        return dataclass(cls)

    if groups_descriptions is None:
        groups_descriptions = {}

    if required_mutually_exclusive_groups is None:
        required_mutually_exclusive_groups = {}

    def wrap(cls: type[Class]) -> type[Class]:
        cls = dataclass(cls)
        setattr(
            cls,
            "__dataparsers_params__",
            (kwargs, groups_descriptions, required_mutually_exclusive_groups, default_bool, help_fmt),
        )
        return cls

    return wrap


def make_parser(cls: type, *, parser: ArgumentParser | None = None) -> ArgumentParser:
    kwargs, groups_descriptions, required_groups_status, default_bool, help_fmt = getattr(
        cls, "__dataparsers_params__", ({}, {}, {}, False, None)
    )

    if parser is None:
        if help_fmt is not None and "formatter_class" not in kwargs:
            kwargs["formatter_class"] = RawTextHelpFormatter
        parser = ArgumentParser(**kwargs)

    help_fmt = help_fmt or str
    groups: dict[str | int, _ArgumentGroup] = {}
    mutually_exclusive_groups: dict[str | int, _MutuallyExclusiveGroup] = {}

    for arg in fields(cls):  # type: ignore
        arg_metadata = dict(arg.metadata)

        if "help" in arg_metadata:
            arg_metadata["help"] = help_fmt(arg_metadata["help"])

        arg_field_has_default = arg.default is not arg.default_factory
        make_flag = arg_metadata.pop("make_flag", True)
        if (arg_field_has_default and arg_metadata.pop("is_flag", True)) or arg.type == bool:
            if "name_or_flags" not in arg_metadata:
                arg_metadata["name_or_flags"] = ()
            if make_flag or (arg.type == bool and not arg_metadata["name_or_flags"]):
                arg_metadata["name_or_flags"] += (f'--{arg.name.replace("_", "-")}',)
            if arg.type == bool and (not arg_field_has_default or arg.default is None):
                arg.default = default_bool

        if not arg_metadata.get("name_or_flags"):  # no flag arg
            arg_metadata["name_or_flags"] = (arg.name,)
        else:  # flag arg
            arg_metadata["dest"] = arg.name

        name_or_flags = arg_metadata.pop("name_or_flags")

        if "type" not in arg_metadata and arg.type != bool:
            arg_metadata["type"] = arg.type

        if "action" not in arg_metadata and arg.type == bool:
            arg_metadata["action"] = "store_false" if arg.default else "store_true"

        if arg.type == bool:
            arg.default = arg_metadata["action"] == "store_false"

        group_id: str | int | None = arg_metadata.pop("group_title", None)
        exclusive_group_id: str | int | None = arg_metadata.pop("mutually_exclusive_group_id", None)
        if any(id is not None for id in [group_id, exclusive_group_id]):

            handler = parser

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

            handler.add_argument(*name_or_flags, default=arg.default, **arg_metadata)

        else:
            parser.add_argument(*name_or_flags, default=arg.default, **arg_metadata)

    return parser


def parse(cls: type[Class], args: Sequence[str] | None = None, *, parser: ArgumentParser | None = None) -> Class:
    return cls(**vars(make_parser(cls, parser=parser).parse_args(args)))


def write_help(
    text: str,
    width: int | None = None,
    space: int = 24,
    dedent: bool = True,
    final_newlines: bool = True,
) -> str:
    width = width or os.get_terminal_size().columns
    lines = []
    for line in text.splitlines():
        line = textwrap.dedent(line) if dedent else line
        lines.append(textwrap.fill(text=line, width=width - space, replace_whitespace=False))

    return "\n".join(lines) + ("\n\n" if final_newlines else "")


# %% ###########################################################################################################################
