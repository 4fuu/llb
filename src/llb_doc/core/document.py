from __future__ import annotations

import asyncio
from enum import Enum
from typing import TYPE_CHECKING, Self

from .block import Block

if TYPE_CHECKING:
    from ..generators.registry import GeneratorRegistry


class MetaRefreshMode(Enum):
    NONE = "none"
    NORMAL = "normal"
    FORCE = "force"


class IDGenerator:
    def __init__(self, prefix: str = "b") -> None:
        self._prefix = prefix
        self._counter = 0

    def next(self) -> str:
        self._counter += 1
        return f"{self._prefix}{self._counter:X}"


class BlockBuilder:
    def __init__(self, doc: Document, type_: str, lang: str | None = None) -> None:
        self._doc = doc
        self._id: str | None = None
        self._type = type_
        self._lang = lang
        self._meta: dict[str, str] = {}
        self._content: str = ""

    def id(self, id_: str) -> Self:
        self._id = id_
        return self

    def meta(self, **kwargs: str) -> Self:
        self._meta.update(kwargs)
        return self

    def content(self, text: str) -> Self:
        self._content = text
        return self

    def add(self) -> Block:
        block_id = self._id or self._doc._id_gen.next()
        block = Block(
            id=block_id,
            type=self._type,
            lang=self._lang,
            meta=self._meta,
            content=self._content,
            _doc=self._doc,
        )
        self._doc._blocks.append(block)
        return block

    def __enter__(self) -> Block:
        block_id = self._id or self._doc._id_gen.next()
        self._block = Block(
            id=block_id,
            type=self._type,
            lang=self._lang,
            meta=self._meta,
            content=self._content,
            _doc=self._doc,
        )
        return self._block

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self._doc._blocks.append(self._block)


class Document:
    def __init__(self) -> None:
        self._blocks: list[Block] = []
        self._id_gen = IDGenerator()
        self._generator_registry: GeneratorRegistry | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Document):
            return NotImplemented
        return self._blocks == other._blocks

    @property
    def blocks(self) -> list[Block]:
        return self._blocks

    def block(self, type_: str, lang: str | None = None) -> BlockBuilder:
        return BlockBuilder(self, type_, lang)

    def add_block(
        self,
        type_: str,
        content: str = "",
        *,
        lang: str | None = None,
        id_: str | None = None,
        **meta: str,
    ) -> Block:
        block_id = id_ or self._id_gen.next()
        block = Block(
            id=block_id,
            type=type_,
            lang=lang,
            meta=meta,
            content=content,
            _doc=self,
        )
        self._blocks.append(block)
        return block

    def render(self, *, meta_refresh: MetaRefreshMode = MetaRefreshMode.NORMAL) -> str:
        if meta_refresh != MetaRefreshMode.NONE:
            force = meta_refresh == MetaRefreshMode.FORCE
            asyncio.run(self.ensure_meta(force=force))

        rendered_blocks = [b.render() for b in self._blocks]
        return "\n\n".join(rendered_blocks)

    async def ensure_meta(self, *, force: bool = False) -> None:
        if self._generator_registry:
            await self._generator_registry.apply_all(self, force=force)


def create_llb() -> Document:
    return Document()
