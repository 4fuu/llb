from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.document import Document

from ..core.block import Block

BLOCK_START_RE = re.compile(r"^@block\s+(\S+)\s+(\S+)(?:\s+(\S+))?$")
BLOCK_END_RE = re.compile(r"^@end\s+(\S+)$")
META_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)=(.*)$")


def parse_llb(text: str) -> Document:
    from ..core.document import Document

    doc = Document()
    lines = text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]
        match = BLOCK_START_RE.match(line)
        if match:
            block_id, block_type, lang = match.groups()
            meta: dict[str, str] = {}
            content_lines: list[str] = []
            i += 1

            while i < len(lines) and lines[i].strip():
                meta_match = META_RE.match(lines[i])
                if meta_match:
                    key, value = meta_match.groups()
                    meta[key] = value
                i += 1

            if i < len(lines) and lines[i] == "":
                i += 1

            end_pattern = f"@end {block_id}"
            while i < len(lines):
                if lines[i] == end_pattern:
                    break
                content_lines.append(lines[i])
                i += 1

            block = Block(
                id=block_id,
                type=block_type,
                lang=lang,
                meta=meta,
                content="\n".join(content_lines).rstrip("\n"),
                _doc=doc,
            )
            doc._block_order.append(block_id)
            doc._id_index[block_id] = block
        i += 1

    return doc
