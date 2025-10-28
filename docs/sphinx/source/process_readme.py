import os
import shutil
from pathlib import Path
from process_text import initial_docstring, markdown_subsection
from replace_snippets import replace_snippets_and_notes


THIS_FILE = Path(__file__)
THIS_DIR = THIS_FILE.parent.resolve()
DOCS_DIR = THIS_DIR.parent.resolve()
ROOT_DIR = DOCS_DIR.parent.resolve()
MODULE_STUB = "__init__.pyi"
MODULE_FILEPATH = ROOT_DIR / "src/dataparsers" / MODULE_STUB
FEATURES_FILE = THIS_DIR / "3_features.md"
ROOT_README = ROOT_DIR / "README.md"

INITIAL_README = """# dataparsers

A simple module to wrap around `argparse` to get command line argument parsers from `dataclasses`.

## Installation

```bash
pip install dataparsers
```
"""

LINK_TO_DOCS = "For more information, see the [documentation](https://dataparsers.readthedocs.io/en/latest/index.html)."


def process_readme():
    # Gets module docstring
    module_docstring = initial_docstring(MODULE_FILEPATH)

    basic_usage = markdown_subsection(module_docstring, "Basic usage")

    arguments_specification = markdown_subsection(module_docstring, "Argument specification")
    strip_index = arguments_specification.index("One parameter of")
    arguments_specification = arguments_specification[:strip_index]

    with open(FEATURES_FILE, "r") as file:
        features = file.read()

    features = features.replace("##", "###")

    with open(ROOT_README, "w") as file:
        file.write(INITIAL_README)
        file.write(basic_usage)
        file.write(arguments_specification)
        file.write(LINK_TO_DOCS)
        file.write(f"\n\n#{features}")

    replace_snippets_and_notes(ROOT_README, True, False)


if __name__ == "__main__":
    process_readme()
