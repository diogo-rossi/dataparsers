from typing import Protocol
from dataclasses import dataclass


class OutErr(Protocol):
    out: str
    err: str


class CapSys(Protocol):
    def readouterr(self) -> OutErr: ...


@dataclass
class HelpDisplay:
    help_text: str

    def __post_init__(self):
        self.text_lines = self.help_text.splitlines()
        self.usage = self.get_usage()
        self.positionals = self.get_positionals()
        self.flags = self.get_flags()

    def get_usage(self) -> str:
        try:
            return [line for line in self.text_lines if line.startswith("usage:")][0]
        except IndexError:
            return ""

    def get_section(self, title: str) -> list[str]:
        try:
            start = self.text_lines.index([line for line in self.text_lines if line.strip().startswith(title)][0]) + 1
            lines = []
            for line in self.text_lines[start:]:
                if not (line.startswith(" ") or line == ""):
                    break
                lines.append(line)
            return lines
        except IndexError:
            return []

    def get_positionals(self) -> list[str]:
        return [
            arg.strip().split()[0].strip()
            for arg in self.get_section("positional arguments:")
            if arg and not arg.startswith(" " * 10)
        ]

    def get_flags(self) -> list[str]:
        flags = []
        for line in self.get_section("options:"):
            if line:
                for part in line.split(","):
                    flags.append(part.strip().split()[0])
        return flags

    def group(self, group_id) -> list[str]:
        args = []
        for line in self.get_section(f"{group_id}:"):
            if line and not line.startswith(" " * 10):
                for part in line.split(","):
                    args.append(part.strip().split()[0])
        return args
