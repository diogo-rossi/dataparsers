import os
import shutil
from process_text import initial_docstring, remove_overloads, put_links_on_file
from replace_snippets import process_file

MODULE_FILE = "dataparsers.py"
EXTERNAL_LINKS = {
    "`parse_args()`": "https://docs.python.org/3/library/argparse.html#the-parse-args-method",
    "`add_argument()`": "https://docs.python.org/3/library/argparse.html#the-add-argument-method",
    "`add_argument_group()`": "https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument_group",
    "`add_mutually_exclusive_group()`": "https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_mutually_exclusive_group",
    "`ArgumentParser`": "https://docs.python.org/3/library/argparse.html#argumentparser-objects",
    "`argparse`": "https://docs.python.org/3/library/argparse.html#module-argparse",
    "`dataclasses`": "https://docs.python.org/3/library/dataclasses.html#module-dataclasses",
    "`dataclass`": "https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass",
}
INTERNAL_LINKS = ["`dest`"]


def process_module():
    # Copy stub file to `source` file
    shutil.copy(os.path.abspath(f"../../src/{MODULE_FILE}i"), os.path.abspath(f"./{MODULE_FILE}"))

    module_docstring = initial_docstring(MODULE_FILE).replace(
        "# dataparsers\n\nA wrapper", "# User manual\n\n`dataparsers` is a simple module that wrappers"
    )

    # Put links for markdown version
    for link in EXTERNAL_LINKS:
        module_docstring = module_docstring.replace(link, f"[{link}]({EXTERNAL_LINKS[link]})")

    with open("1_user_manual.md", "w") as file:
        file.write(module_docstring)

    # format notes and snippets for MyST
    process_file("1_user_manual.md", replace_notes=True, replace_snippets=True)

    # remove overloads from the original stub file
    remove_overloads(MODULE_FILE)

    # put links on file for sphinx reST file
    put_links_on_file(MODULE_FILE, EXTERNAL_LINKS, INTERNAL_LINKS)
