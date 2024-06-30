from pathlib import Path


def initial_docstring(filepath: Path):
    """Returns the module's docstring (the initial docstring of the module)"""
    with open(filepath, "r") as file:
        text = file.read()
    return text[3 : text.index('"""\n', 1)]


def markdown_subsection(text: str, title: str):
    ini = text.index(f"## {title}")
    end = ini + text[ini:].index("##", 1)
    return text[ini:end]


def remove_overloads(filepath: Path):
    """Remove the `@overload` signatures that comes in the stub file, to create a simple module file"""
    with open(filepath, "r") as file:
        text = file.read()
    ini = text.index("@overload", 0)
    end = ini + text[ini:].index("@overload", len("@overload"))
    text_to_remove = text[ini : end + len("@overload")]
    text = text.replace(text_to_remove, "")
    with open(filepath, "w") as file:
        file.write(text)


def make_rst_link(link: str):
    """Make a hyperlink to the external Python documentation using the reST syntax"""
    link = link.replace("`", "")
    if "ClassVar" in link:  # link to `typing`
        return f":data:`~typing.{link}`"
    if link in ["argparse", "dataclasses"]:  # link to the modules `argparse` or `dataclasses`
        return f":mod:`~{link}`"
    if link.replace("()", "") in ["dataclass"]:  # link to the function/decorator dataclass()`
        return f":func:`~dataclasses.dataclass`"
    if link.endswith("()"):  # link to methods of `argparse.ArgumentParser`
        return f':meth:`~argparse.ArgumentParser.{link.replace("()","")}`'
    if link[0].isupper():  # link to classes inside `argparse`
        return f":class:`~argparse.{link}`"
    return link


def put_links_on_file(
    filepath: Path, external_links: dict[str, str], internal_links: list[str], arguments_links: list[str]
):
    """Put links on the module file to be processed by sphinx

    - External links to python documentation
    - Internal links to parameters descriptions
    """
    lines = []
    with open(filepath, "r") as file:
        for line in file:
            for link in external_links:
                line = line.replace(link, make_rst_link(link))
            for func in internal_links:
                line = line.replace(func, f":func:`~dataparsers.{func.replace('`','').replace('()','')}`")
            for arg in arguments_links:
                arg_without_backticks = arg.replace("`", "")
                arg_without_backticks_and_under_for_hifen = arg_without_backticks.replace("_", "-")
                if line.startswith(f"    - {arg}"):
                    line = f"\n    .. _{arg_without_backticks_and_under_for_hifen}:\n\n{line}"
                elif arg in line:
                    line = line.replace(
                        arg, f":argument_link:`{arg_without_backticks}<{arg_without_backticks_and_under_for_hifen}>`"
                    )
            lines.append(line)
            if line.startswith("    -------------"):
                lines[-1] = "    " + "-" * (len(lines[-2]) - 4) + "\n"
    with open(filepath, "w") as file:
        file.write("".join(lines))
