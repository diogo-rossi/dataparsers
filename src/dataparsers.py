# %% ############################################### data parsers region ###############################################


from dataclasses import dataclass, field, fields
from argparse import ArgumentParser, _MutuallyExclusiveGroup
from typing import Any, TypeVar, Sequence, Callable, overload

SPECIALATTRIBUTE = "__data_parsers_params__"
Class = TypeVar("Class", covariant=True)


def arg(*name_or_flags: str, default=None, mutually_exclusive_group: str | int | None = None, **kwargs) -> Any:
    is_flag = False
    if name_or_flags:
        # Error if `name_or_flags` is given without flags
        if not all(n.startswith("-") for n in name_or_flags):
            raise ValueError(
                "The argument `name_or_flags` should be passed to function `arg` only if it is a flag (starts with `-`)"
            )
        is_flag = True

    if "dest" in kwargs:
        raise ValueError("The argument `dest` is not necessary")

    arg_dict = dict(name_or_flags=name_or_flags, mutually_exclusive_group=mutually_exclusive_group, is_flag=is_flag, **kwargs)

    # remove dict nones
    arg_dict = {key: value for key, value in arg_dict.items() if value is not None}

    return field(default=default, metadata=arg_dict)


@overload
def dataparser(cls: type[Class]) -> type[Class]:
    ...


@overload
def dataparser(
    *, required_mutually_exclusive_groups: dict[str | int, bool] | None = None, default_store_bool: bool = True, **kwargs
) -> Callable[[type[Class]], type[Class]]:
    ...


def dataparser(
    cls, *, required_mutually_exclusive_groups=None, default_store_bool=True, **kwargs
) -> type[Class] | Callable[[type[Class]], type[Class]]:
    if cls is not None:
        return dataclass(cls)

    if required_mutually_exclusive_groups is None:
        required_mutually_exclusive_groups = {}

    def wrap(cls: type[Class]) -> type[Class]:
        cls = dataclass(cls)
        setattr(cls, SPECIALATTRIBUTE, (kwargs, required_mutually_exclusive_groups, default_store_bool))
        return cls

    return wrap


def parse(cls: type[Class], args: Sequence[str] | None = None, *, parser: ArgumentParser | None = None) -> Class:
    kwargs, required_groups, default_bool = getattr(cls, SPECIALATTRIBUTE, ({}, {}, False))
    groups: dict[str | int, _MutuallyExclusiveGroup] = {}
    if parser is None:
        parser = ArgumentParser(**kwargs)

    for arg in fields(cls):  # type: ignore
        # Transform in dict because MappingProxyType is not subscriptable
        arg_metadata = dict(arg.metadata)

        arg_field_has_default = arg.default is not arg.default_factory

        if (arg_field_has_default and arg_metadata.pop("is_flag", True)) or (not arg_field_has_default and arg.type == bool):
            # `arg` is field with default value and is not a flag by `arg()` or `arg` is `bool` and has no default: make it flag
            if not arg_metadata.get("name_or_flags", False):
                arg_metadata["name_or_flags"] = ("--" + arg.name.replace("_", "-"),)
            if not arg_field_has_default:
                # arg is a `bool` and has no default (required): make it with default
                arg.default = default_bool

        # get name_or_flags argument
        if not arg_metadata.get("name_or_flags"):  # no flag arg
            arg_metadata["name_or_flags"] = (arg.name,)
        else:  # flag arg
            arg_metadata["dest"] = arg.name
        name_or_flags = arg_metadata.pop("name_or_flags")

        # infer type from field (if it is not `bool`)
        if "type" not in arg_metadata and arg.type != bool:
            arg_metadata["type"] = arg.type

        # for `bool` arg, the `default` defines `action`
        if "action" not in arg_metadata and arg.type == bool:
            arg_metadata["action"] = "store_false" if arg.default else "store_true"

        group_id: str | int | None = arg_metadata.pop("mutually_exclusive_group", None)
        if group_id is not None:
            if group_id not in groups:
                groups[group_id] = parser.add_mutually_exclusive_group(
                    required=required_groups.get(group_id, False),
                )
            groups[group_id].add_argument(*name_or_flags, default=arg.default, **arg_metadata)
        else:
            parser.add_argument(*name_or_flags, default=arg.default, **arg_metadata)

    return cls(**vars(parser.parse_args(args)))


# %% ###################################################################################################################
