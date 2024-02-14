# %% ################################################# dataparsers region ######################################################
import os, textwrap
from dataclasses import dataclass, field, fields
from argparse import ArgumentParser, _MutuallyExclusiveGroup, _ArgumentGroup
from typing import Any, TypeVar, Sequence, Callable, overload

Class = TypeVar("Class", covariant=True)


def arg(
    *name_or_flags: str,
    group: str | int | None = None,
    mutually_exclusive_group: str | int | None = None,
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

    if group is not None and mutually_exclusive_group is not None:
        raise ValueError("Can't pass both `group` and `mutually_exclusive_group`")

    if "default" in kwargs and not kwargs.get("nargs", None) in ["?", "*"]:
        make_flag = True

    default = kwargs.pop("default", None)

    if not is_flag and mutually_exclusive_group is not None:
        make_flag = True

    make_flag = bool(make_flag)
    is_flag = is_flag or make_flag

    metadict = dict(
        name_or_flags=name_or_flags,
        group=group,
        mutually_exclusive_group=mutually_exclusive_group,
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
    groups: dict[str | int, bool] | None = None,
    required_mutually_exclusive_groups: dict[str | int, bool] | None = None,
    default_store_bool: bool = True,
    **kwargs,
) -> Callable[[type[Class]], type[Class]]: ...


def dataparser(
    cls: type[Class] | None = None,
    *,
    groups: dict[str | int, bool] | None = None,
    required_mutually_exclusive_groups=None,
    default_store_bool=True,
    **kwargs,
) -> type[Class] | Callable[[type[Class]], type[Class]]:
    if cls is not None:
        return dataclass(cls)

    if groups is None:
        groups = {}

    if required_mutually_exclusive_groups is None:
        required_mutually_exclusive_groups = {}

    def wrap(cls: type[Class]) -> type[Class]:
        cls = dataclass(cls)
        setattr(cls, "__dataparsers_params__", (kwargs, groups, required_mutually_exclusive_groups, default_store_bool))
        return cls

    return wrap


def parse(cls: type[Class], args: Sequence[str] | None = None, *, parser: ArgumentParser | None = None) -> Class:
    kwargs, groups, required_groups, default_bool = getattr(cls, "__dataparsers_params__", ({}, {}, {}, False))
    if parser is None:
        parser = ArgumentParser(**kwargs)

    arg_groups: dict[str | int, _ArgumentGroup] = {}
    mutually_exclusive_groups: dict[str | int, _MutuallyExclusiveGroup] = {}

    for arg in fields(cls):  # type: ignore
        arg_metadata = dict(arg.metadata)

        arg_field_has_default = arg.default is not arg.default_factory
        make_flag = arg_metadata.pop("make_flag", True)
        if (arg_field_has_default and arg_metadata.pop("is_flag", True)) or (not arg_field_has_default and arg.type == bool):
            if "name_or_flags" not in arg_metadata:
                arg_metadata["name_or_flags"] = ()
            if make_flag:
                arg_metadata["name_or_flags"] += (f'--{arg.name.replace("_", "-")}',)
            if not arg_field_has_default:
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

        group_id: str | int | None = arg_metadata.pop("group", None)
        exclusive_group_id: str | int | None = arg_metadata.pop("mutually_exclusive_group", None)
        if group_id is not None:
            if group_id not in arg_groups:
                arg_groups[group_id] = parser.add_argument_group(title=str(group_id), description=groups.get(group_id, None))
            arg_groups[group_id].add_argument(*name_or_flags, default=arg.default, **arg_metadata)
        elif exclusive_group_id is not None:
            if exclusive_group_id not in mutually_exclusive_groups:
                mutually_exclusive_groups[exclusive_group_id] = parser.add_mutually_exclusive_group(
                    required=required_groups.get(exclusive_group_id, False),
                )
            mutually_exclusive_groups[exclusive_group_id].add_argument(*name_or_flags, default=arg.default, **arg_metadata)
        else:
            parser.add_argument(*name_or_flags, default=arg.default, **arg_metadata)

    return cls(**vars(parser.parse_args(args)))


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
