import os
import shutil
from pathlib import Path
from process_text import initial_docstring, remove_overloads, put_links_on_file
from replace_snippets import replace_snippets_and_notes

EXTERNAL_LINKS = {
    "`parse_args()`": "https://docs.python.org/3/library/argparse.html#the-parse-args-method",
    "`add_argument()`": "https://docs.python.org/3/library/argparse.html#the-add-argument-method",
    "`add_argument_group()`": "https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument_group",
    "`add_mutually_exclusive_group()`": "https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_mutually_exclusive_group",
    "`ArgumentParser`": "https://docs.python.org/3/library/argparse.html#argumentparser-objects",
    "`argparse`": "https://docs.python.org/3/library/argparse.html#module-argparse",
    "`dataclasses`": "https://docs.python.org/3/library/dataclasses.html#module-dataclasses",
    "`dataclass`": "https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass",
    "`ClassVar`": "https://docs.python.org/3/library/typing.html#typing.ClassVar",
    "`set_defaults()`": "https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.set_defaults",
    "`add_subparsers()`": "https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers",
    "`add_parser()`": "https://github.com/python/cpython/blob/fc4599800778f9b130d5e336deadbdeb5bd3e5ee/Lib/argparse.py#L1221",
    "`parse_known_args()`": "https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_known_args",
    '"Aliases"': "#aliases",
    '"Default for booleans"': "#default-for-booleans",
    '"main parser-level"': "#parser-level-defaults",
    '"Argument groups using ': "#argument-groups-using-classvar-v2-1",
    '"Subparsers"': "#subparsers-v2-1",
}

EMPHASIS = [
    "must be a series of flags",
    "must be passed only with flags",
    "This may be the most common case",
    "The dictionary keys must be defined previously",
]

INTERNAL_LINKS = [
    "`arg()`",
    "`parse()`",
    "`parse_known()`",
    "`dataparser()`",
    "`make_parser()`",
    "`write_help()`",
    "`group()`",
    "`mutually_exclusive_group()`",
    "`default()`",
    "`subparser()`",
    "`subparsers()`",
]

ARGUMENTS_LINKS = [
    "`name_or_flags`",
    "`group`",
    "`group_title`",
    "`title`",
    "`mutually_exclusive_group`",
    "`mutually_exclusive_group_id`",
    "`make_flag`",
    "`action`",
    "`nargs`",
    "`const`",
    "`default`",
    "`type`",
    "`choices`",
    "`required`",
    "`help`",
    "`metavar`",
    "`dest`",
    "`groups_descriptions`",
    "`required_mutually_exclusive_groups`",
    "`default_bool`",
    "`help_formatter`",
    "`prog`",
    "`usage`",
    "`description`",
    "`epilog`",
    "`parents`",
    "`formatter_class`",
    "`prefix_chars`",
    "`fromfile_prefix_chars`",
    "`argument_default`",
    "`conflict_handler`",
    "`add_help`",
    "`allow_abbrev`",
    "`exit_on_error`",
    "`parser`",
    "`subparser`",
    "`defaults`",
    "`aliases`",
]

THIS_FILE = Path(__file__)
THIS_DIR = THIS_FILE.parent.resolve()
DOCS_DIR = THIS_DIR.parent.resolve()
ROOT_DIR = DOCS_DIR.parent.resolve()

STUB_FILE = ROOT_DIR / "src/dataparsers/__init__.pyi"
MARK_FILE = ROOT_DIR / "src/dataparsers/__init__.md"

MODULE_FILENAME = "dataparsers.py"
MODULE_FILEPATH = THIS_DIR / MODULE_FILENAME
USER_MANUAL_FILE = THIS_DIR / "1_user_manual.md"
FUNCTIONS_MANUAL = THIS_DIR / "2_available_functions.md"
TABLES = THIS_DIR / "tables.md"
FUNCTIONS = THIS_DIR / "functions.md"


def process_module():
    """Copy the stub file and process the module to use `autofunction` - replace links and format markdown"""

    with open(MARK_FILE, "r") as file:
        txt = file.read()

    with open(STUB_FILE, "r") as file:
        stub = file.read()

    stub = txt + "\n" + stub[stub.index('"""', 10) :]

    with open(STUB_FILE, "w") as file:
        file.write(stub)

    # Copy stub file form `./src` folder to  `./docs/source` folder
    shutil.copy(os.path.abspath(f"{ROOT_DIR}/src/dataparsers/__init__.pyi"), os.path.abspath(MODULE_FILEPATH))

    # %% ---- process the module docstring to write manual

    # Gets module docstring to write the user manual
    module_docstring = initial_docstring(MODULE_FILEPATH).replace(
        "# dataparsers\n\nA wrapper around `argparse` to get command line argument parsers from `dataclasses`.",
        """# User manual\n\n`dataparsers` is a simple module that wrappers around `argparse` to get command line argument
        parsers from `dataclasses`. It can create type checkable command line argument parsers using `dataclasses`, which are
        recognized by type checkers and can be used by autocomplete tools.""",
    )

    # Put links in markdown version of user manual
    for link in EXTERNAL_LINKS:
        module_docstring = module_docstring.replace(link, f"[{link}]({EXTERNAL_LINKS[link]})")
    for link in INTERNAL_LINKS:
        module_docstring = module_docstring.replace(link, f"{{py:func}}`~dataparsers.{link.replace('`','').replace('()','')}`")
    for link in ARGUMENTS_LINKS:
        module_docstring = module_docstring.replace(
            link, f"[{link}](./2_available_functions.md#{link.replace('`','').replace('_','-')})"
        )

    for emphasis in EMPHASIS:
        module_docstring = module_docstring.replace(emphasis, f"**{emphasis}**")

    # Writes the user manual
    with open(USER_MANUAL_FILE, "w") as file:
        file.write(module_docstring)

    # format notes and snippets for MyST
    replace_snippets_and_notes(USER_MANUAL_FILE, replace_notes=True, replace_snippets=True)

    # %% ---- process the function manual

    with open(TABLES, "r") as file:
        tables = file.read()

    for link in INTERNAL_LINKS:
        tables = tables.replace(link, f"{{py:func}}`~dataparsers.{link.replace('`','').replace('()','')}`")
    for link in ARGUMENTS_LINKS:
        tables = tables.replace(link, f"[{link}](./2_available_functions.md#{link.replace('`','').replace('_','-')})")

    functions_toc = """
```{eval-rst}
.. autofunction:: dataparsers.arg
```
---
```{eval-rst}
.. autofunction:: dataparsers.group
```
---
```{eval-rst}
.. autofunction:: dataparsers.mutually_exclusive_group
```
---
```{eval-rst}
.. autofunction:: dataparsers.default
```
---
```{eval-rst}
.. autofunction:: dataparsers.dataparser
```
---
```{eval-rst}
.. autofunction:: dataparsers.parse
```
---
```{eval-rst}
.. autofunction:: dataparsers.parse_known
```
---
```{eval-rst}
.. autofunction:: dataparsers.make_parser
```
---
```{eval-rst}
.. autofunction:: dataparsers.subparser
```
---
```{eval-rst}
.. autofunction:: dataparsers.subparsers
```
---
```{eval-rst}
.. autofunction:: dataparsers.write_help
```
---
"""

    with open(FUNCTIONS_MANUAL, "w") as file:
        file.write(f"{tables}\n\n")
        file.write(functions_toc)

    # %% ---- process the module file to use `autofunction`

    # remove overloads from the original stub file
    remove_overloads(MODULE_FILEPATH)

    # put links on file for sphinx reST file
    put_links_on_file(MODULE_FILEPATH, EXTERNAL_LINKS, INTERNAL_LINKS, ARGUMENTS_LINKS)

    with open(MODULE_FILEPATH, "r") as file:
        tables = file.read()

    for emphasis in EMPHASIS:
        tables = tables.replace(emphasis, f"**{emphasis}**")

    with open(MODULE_FILEPATH, "w") as file:
        file.write(tables)


if __name__ == "__main__":
    process_module()
