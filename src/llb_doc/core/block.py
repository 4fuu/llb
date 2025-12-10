from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .document import Document


@dataclass
class Block:
    id: str
    type: str
    lang: str | None = None
    meta: dict[str, str] = field(default_factory=dict)
    content: str = ""

    _doc: Document | None = field(default=None, repr=False, compare=False)

    _fields = frozenset({"id", "type", "lang", "meta", "content", "_doc"})

    def __getattr__(self, name: str) -> str | None:
        if name.startswith("_"):
            raise AttributeError(name)
        return self.meta.get(name)

    def __setattr__(self, name: str, value: str) -> None:
        if name in Block._fields:
            object.__setattr__(self, name, value)
        else:
            self.meta[name] = value

    def __delattr__(self, name: str) -> None:
        if name == "lang":
            object.__setattr__(self, "lang", None)
        elif name == "content":
            object.__setattr__(self, "content", "")
        elif name in self.meta:
            del self.meta[name]
        else:
            raise AttributeError(name)

    def render(self) -> str:
        lines: list[str] = []

        header_parts = ["@block", self.id, self.type]
        if self.lang:
            header_parts.append(self.lang)
        lines.append(" ".join(header_parts))

        for key, value in self.meta.items():
            if "\n" in str(value):
                lines.append(f'{key}="""{value}"""')
            else:
                lines.append(f"{key}={value}")

        lines.append("")
        if self.content:
            lines.append(self.content)
        lines.append("")

        lines.append(f"@end {self.id}")

        return "\n".join(lines)
