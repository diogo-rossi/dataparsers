from pathlib import Path


def identify_code_snippets(filepath: Path) -> list[str]:
    """Returns a list of code snippets (delimited by `::`) inside docstrings of a module filepath"""
    snippets = []
    with open(filepath, "r") as file:
        in_snippet = False
        current_snippet = []

        for line in file:
            clean_line = line.rstrip()  # Remove whitespace at the end of the line

            if clean_line.endswith("::"):
                if in_snippet:
                    snippets.append("".join(current_snippet))
                current_snippet = ["::\n"]
                in_snippet = True
                continue

            if in_snippet:
                if clean_line == "" or clean_line.startswith("    "):  # Checks if the line is indented with 4 spaces
                    current_snippet.append(line)
                else:
                    if current_snippet:  # If there are lines in the current snippet, store it
                        snippets.append("".join(current_snippet))
                        current_snippet = []
                    in_snippet = False

        if current_snippet:
            snippets.append("".join(current_snippet))  # Add the last snippet, if any

    return snippets


def separate_snippets_by_type(snippets: list[str]) -> dict[str, list[str]]:
    """Separate code snippets by types: "Python" and "Shell" """
    result = {"python": [], "sh": []}
    for snippet in snippets:
        if "$" in snippet:
            result["sh"].append(snippet)
        else:
            result["python"].append(snippet)
    return result


def code_snippet_to_replace_in_markdown_for_myst(snippet: str, type_of_code: str) -> str:
    """Returns a corrected code snippet to replace in markdown docs (removes indentation and put back ticks)"""
    lines = snippet.split("\n")
    corrected_snippet_lines = []
    for line in lines[2:-2]:
        line = line.rstrip()
        if line == "" or line.startswith("    "):
            corrected_snippet_lines.append(line.removeprefix("    "))
        else:
            raise ValueError("ERROR")
    final_lines = [":", lines[1]] + [f"```{type_of_code}"] + corrected_snippet_lines + ["```", "\n"]
    return "\n".join(final_lines)


def replace_note_sections_in_markdown_for_myst(file: Path):
    """Put the correct "Note" section inside the markdown docs (for MyST with sphinx)"""
    in_Note = False
    note_section = []
    note_sections_list: list[str] = []
    for line in open(file, "r"):
        if line.startswith("Note:"):
            in_Note = True
            note_section.append(line)
            continue
        if in_Note:
            if line.rstrip().startswith("    "):
                note_section.append(line)
            else:
                in_Note = False
                note_sections_list.append("".join(note_section))
                note_section = []
    with open(file, "r") as fd:
        text = fd.read()
    for note in note_sections_list:
        note_snippet = note.replace("Note:", "```{note}", 1) + "```"
        new_snippet = "\n".join([line.lstrip() for line in note_snippet.split("\n")])
        text = text.replace(note, new_snippet)
    with open(file, "w") as fd:
        fd.write(text)


def replace_code_snippets_in_markdown_for_myst(file: Path):
    "Replaces the code snippets written for VSCode stub file by corrected snippets to write in markdown format"
    code_snippets = separate_snippets_by_type(identify_code_snippets(file))
    with open(file, "r") as fd:
        text = fd.read()
    for type_of_snippet in code_snippets:
        for snippet in code_snippets[type_of_snippet]:
            new_snippet = code_snippet_to_replace_in_markdown_for_myst(snippet, type_of_snippet)
            text = text.replace(snippet, new_snippet)
    with open(file, "w") as fd:
        fd.write(text)


def replace_snippets_and_notes(filepath: Path, replace_snippets: bool, replace_notes: bool):
    """Formats a markdown file that supports VSCode stubs for pylance replacing snippets and notes sections.

    - snippets are given in the stub by a `::` symbol (the are replaced by markdown code snippet)
    - Notes are simple paragraphs with indentation (the are replaced by MyST notes sections)

    """
    if replace_snippets:
        replace_code_snippets_in_markdown_for_myst(filepath)
    if replace_notes:
        replace_note_sections_in_markdown_for_myst(filepath)
