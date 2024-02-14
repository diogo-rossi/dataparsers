def initial_docstring(filepath):
    with open(filepath, "r") as file:
        text = file.read()
    return text[3 : text.index('"""\n', 1)]


def markdown_subsection(text: str, title: str):
    ini = text.index(f"## {title}")
    end = ini + text[ini:].index("##", 1)
    return text[ini:end]


def remove_overloads(filepath):
    with open(filepath, "r") as file:
        text = file.read()
    ini = text.index("@overload", 0)
    end = ini + text[ini:].index("@overload", len("@overload"))
    text_to_remove = text[ini : end + len("@overload")]
    text = text.replace(text_to_remove, "")
    with open(filepath, "w") as file:
        file.write(text)


def make_rst_link(link: str):
    link = link.replace("`", "")
    if link in ["argparse", "dataclasses"]:
        return f":mod:`~{link}`"
    if link.replace("()", "") in ["dataclass"]:
        return f":func:`~dataclasses.dataclass`"
    if link.endswith("()"):
        return f':meth:`~argparse.ArgumentParser.{link.replace("()","")}`'
    if link[0].isupper():
        return f":class:`~argparse.{link}`"
    return link


def put_links_on_file(filepath: str, links: dict[str, str], int_links: list[str]):
    lines = []
    with open(filepath, "r") as file:
        for line in file:
            for link in links:
                line = line.replace(link, make_rst_link(link))
            for link in int_links:
                line = line.replace(link, f":literal_issue:{link}")
            lines.append(line)
            if line.startswith("    -------------"):
                lines[-1] = "    " + "-" * (len(lines[-2]) - 4) + "\n"
    with open(filepath, "w") as file:
        file.write("".join(lines))


if __name__ == "__main__":
    text = initial_docstring("dataparsers.py")
