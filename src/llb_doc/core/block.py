from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .document import Document


class Block:
    _fields = frozenset({"id", "type", "lang", "meta", "content", "_doc"})

    def __init__(
        self,
        id: str,
        type: str,
        lang: str | None = None,
        meta: dict[str, str] | None = None,
        content: str = "",
        _doc: Document | None = None,
        **kwargs: str,
    ) -> None:
        self.id = id
        self.type = type
        self.lang = lang
        self.meta = meta if meta is not None else {}
        self.content = content
        self._doc = _doc
        self.meta.update(kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Block):
            return NotImplemented
        return (
            self.id == other.id
            and self.type == other.type
            and self.lang == other.lang
            and self.meta == other.meta
            and self.content == other.content
        )

    def __repr__(self) -> str:
        return f"Block(id={self.id!r}, type={self.type!r}, lang={self.lang!r}, meta={self.meta!r}, content={self.content!r})"

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
