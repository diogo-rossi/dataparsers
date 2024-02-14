# %% ############################################### data parsers region ###############################################


from dataclasses import dataclass, field, fields
from argparse import ArgumentParser, _MutuallyExclusiveGroup
from typing import Any, TypeVar, Sequence, Callable

SPECIALATTRIBUTE = "__data_parsers_params__"
Class = TypeVar("Class", covariant=True)


def arg(*name_or_flags: str, default=None, mutually_exclusive_group: str | int | None = None, **kwargs) -> Any:
    # Error if `name_or_flags` is given without flags
    if name_or_flags and not all(n.startswith("-") for n in name_or_flags):
        raise ValueError(
            "The argument `name_or_flags` should be passed to function `arg` only if it is a flag (starts with `-`)"
        )

    if "dest" in kwargs:
        raise ValueError("The argument `dest` is not necessary")

    arg_dict = dict(name_or_flags=name_or_flags, mutually_exclusive_group=mutually_exclusive_group, **kwargs)

    # remove dict nones
    arg_dict = {key: value for key, value in arg_dict.items() if value is not None}

    return field(default=default, metadata=arg_dict)


def dataparser(
    cls: type[Class] | None = None, *, required_mutually_exclusive_groups: dict[str | int, bool] | None = None, **kwargs
) -> type[Class] | Callable[[type[Class]], type[Class]]:
    if cls is not None:
        return dataclass(cls)

    if required_mutually_exclusive_groups is None:
        required_mutually_exclusive_groups = {}

    def wrap(cls: type[Class]) -> type[Class]:
        cls = dataclass(cls)
        setattr(cls, SPECIALATTRIBUTE, (kwargs, required_mutually_exclusive_groups))
        return cls

    return wrap


def parse(cls: type[Class], args: Sequence[str] | None = None, *, parser: ArgumentParser | None = None) -> Class:
    kwargs, required_groups = getattr(cls, SPECIALATTRIBUTE, ({}, {}))

    if parser is None:
        parser = ArgumentParser(**kwargs)

    groups: dict[str | int, _MutuallyExclusiveGroup] = {}

    for arg in fields(cls):  # type: ignore
        # Transform to dict because MappingProxyType is not subscriptable
        arg_metadata = dict(arg.metadata)

        # Get name_or_flags argument
        if not arg_metadata.get("name_or_flags"):  # no flagged arg
            arg_metadata["name_or_flags"] = (arg.name,)
        else:  # flagged arg
            arg_metadata["dest"] = arg.name
        name_or_flags = arg_metadata.pop("name_or_flags")

        if "type" not in arg_metadata and arg.type != bool:
            arg_metadata["type"] = arg.type

        if "action" not in arg_metadata and arg.type == bool:
            arg_metadata["action"] = "store_true" if arg.default else "store_false"

        group_id: str | int | None = arg_metadata.pop("mutually_exclusive_group", None)
        if group_id is not None:
            if group_id not in groups:
                groups[group_id] = parser.add_mutually_exclusive_group(
                    required=required_groups.get(group_id, False),
                )
            groups[group_id].add_argument(*name_or_flags, **arg_metadata)
        else:
            parser.add_argument(*name_or_flags, **arg_metadata)

    return parser.parse_args(args, namespace=cls())


# %% ###################################################################################################################
