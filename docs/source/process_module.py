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
    '"Aliases"': "#aliases",
    '"Default for booleans"': "#default-for-booleans",
}

EMPHASIS = [
    "must be a series of flags",
    "must be passed only with flags",
    "This may be the most common case",
]

INTERNAL_LINKS = ["`arg()`", "`parse()`", "`dataparser()`", "`make_parser()`", "`write_help()`"]

ARGUMENTS_LINKS = [
    "`name_or_flags`",
    "`group_title`",
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
    "`help_fmt`",
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
]

THIS_FILE = Path(__file__)
THIS_DIR = THIS_FILE.parent.resolve()
DOCS_DIR = THIS_DIR.parent.resolve()
ROOT_DIR = DOCS_DIR.parent.resolve()
MODULE_FILENAME = "dataparsers.py"
MODULE_FILEPATH = THIS_DIR / MODULE_FILENAME
USER_MANUAL_FILE = THIS_DIR / "1_user_manual.md"
FUNCTIONS_MANUAL = THIS_DIR / "2_available_functions.md"


def process_module():
    """Copy the stub file and process the module to use `autofunction` - replace links and format markdown"""

    # Copy stub file form `./src` folder to  `./docs/source` folder
    shutil.copy(os.path.abspath(f"{ROOT_DIR}/src/{MODULE_FILENAME}i"), os.path.abspath(MODULE_FILEPATH))

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
        module_docstring = module_docstring.replace(
            link, f"{{py:func}}`~dataparsers.{link.replace('`','').replace('()','')}`"
        )
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

    with open(FUNCTIONS_MANUAL, "r") as file:
        text = file.read()

    for link in INTERNAL_LINKS:
        text = text.replace(link, f"{{py:func}}`~dataparsers.{link.replace('`','').replace('()','')}`")
    for link in ARGUMENTS_LINKS:
        text = text.replace(link, f"[{link}](./2_available_functions.md#{link.replace('`','').replace('_','-')})")

    with open(FUNCTIONS_MANUAL, "w") as file:
        file.write(text)

    # %% ---- process the module file to use `autofunction`

    # remove overloads from the original stub file
    remove_overloads(MODULE_FILEPATH)

    # put links on file for sphinx reST file
    put_links_on_file(MODULE_FILEPATH, EXTERNAL_LINKS, INTERNAL_LINKS, ARGUMENTS_LINKS)

    with open(MODULE_FILEPATH, "r") as file:
        text = file.read()

    for emphasis in EMPHASIS:
        text = text.replace(emphasis, f"**{emphasis}**")

    with open(MODULE_FILEPATH, "w") as file:
        file.write(text)
