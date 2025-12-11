"""Tests for llb_doc library."""

from llb_doc import Block, Document, create_llb, parse_llb


class TestBlock:
    def test_block_creation(self):
        block = Block(id="b1", type="ticket", content="Test content")
        assert block.type == "ticket"
        assert block.content == "Test content"
        assert block.lang is None
        assert block.meta == {}

    def test_block_with_lang(self):
        block = Block(id="b2", type="code", content="print('hello')", lang="python")
        assert block.lang == "python"

    def test_block_with_meta(self):
        block = Block(id="b3", type="note", content="content", meta={"source": "test", "priority": "high"})
        assert block.meta["source"] == "test"
        assert block.meta["priority"] == "high"

    def test_block_with_kwargs(self):
        block = Block(id="b4", type="log", content="error", level="error", service="api")
        assert block.meta["level"] == "error"
        assert block.meta["service"] == "api"

    def test_block_kwargs_merge_with_meta(self):
        block = Block(id="b5", type="note", meta={"existing": "value"}, author="alice", status="open")
        assert block.meta["existing"] == "value"
        assert block.meta["author"] == "alice"
        assert block.meta["status"] == "open"

    def test_block_equality(self):
        block1 = Block(id="b1", type="note", content="test", lang="en", source="a")
        block2 = Block(id="b1", type="note", content="test", lang="en", source="a")
        block3 = Block(id="b1", type="note", content="different")
        assert block1 == block2
        assert block1 != block3

    def test_block_repr(self):
        block = Block(id="b1", type="note", content="test")
        assert "Block(" in repr(block)
        assert "id='b1'" in repr(block)


class TestDocument:
    def test_create_empty_document(self):
        doc = create_llb()
        assert isinstance(doc, Document)
        assert len(doc.blocks) == 0

    def test_add_block(self):
        doc = create_llb()
        doc.add_block("ticket", "Test content", lang="en", source="jira")
        assert len(doc.blocks) == 1
        assert doc.blocks[0].type == "ticket"
        assert doc.blocks[0].content == "Test content"

    def test_fluent_api(self):
        doc = create_llb()
        doc.block("api", lang="json").meta(source="test").content('{"key": "value"}').add()
        assert len(doc.blocks) == 1
        assert doc.blocks[0].type == "api"

    def test_context_manager(self):
        doc = create_llb()
        with doc.block("note", "zh") as b:
            b.source = "review"
            b.content = "测试内容"
        assert len(doc.blocks) == 1
        assert doc.blocks[0].lang == "zh"


class TestRenderAndParse:
    def test_render_produces_string(self):
        doc = create_llb()
        doc.add_block("test", "content")
        result = doc.render()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_parse_roundtrip(self):
        doc = create_llb()
        doc.add_block("ticket", "User cannot login", lang="en", source="jira")
        doc.add_block("note", "需要检查认证逻辑", lang="zh", source="review")
        
        rendered = doc.render()
        parsed = parse_llb(rendered)
        
        assert len(parsed.blocks) == len(doc.blocks)
        for orig, parsed_block in zip(doc.blocks, parsed.blocks):
            assert orig.type == parsed_block.type
            assert orig.content == parsed_block.content
            assert orig.lang == parsed_block.lang

    def test_empty_document_render(self):
        doc = create_llb()
        result = doc.render()
        assert isinstance(result, str)


class TestPrefixSuffix:
    def test_prefix_only(self):
        doc = create_llb()
        doc.prefix = "This is the prefix"
        doc.add_block("test", "content")
        rendered = doc.render()
        assert rendered.startswith("This is the prefix")
        parsed = parse_llb(rendered)
        assert parsed.prefix == "This is the prefix"

    def test_suffix_only(self):
        doc = create_llb()
        doc.suffix = "--- END ---"
        doc.add_block("test", "content")
        rendered = doc.render()
        assert rendered.endswith("--- END ---")
        parsed = parse_llb(rendered)
        assert parsed.suffix == "--- END ---"

    def test_prefix_and_suffix(self):
        doc = create_llb()
        doc.prefix = "Header text"
        doc.suffix = "Footer text"
        doc.add_block("test", "content")
        rendered = doc.render()
        parsed = parse_llb(rendered)
        assert parsed.prefix == "Header text"
        assert parsed.suffix == "Footer text"
        assert len(parsed.blocks) == 1

    def test_prefix_suffix_roundtrip(self):
        doc = create_llb()
        doc.prefix = "Multi\nline\nprefix"
        doc.suffix = "Multi\nline\nsuffix"
        doc.add_block("note", "content", lang="en")
        rendered = doc.render()
        parsed = parse_llb(rendered)
        assert parsed == doc

    def test_empty_prefix_suffix(self):
        doc = create_llb()
        doc.add_block("test", "content")
        assert doc.prefix == ""
        assert doc.suffix == ""

    def test_document_equality_with_prefix_suffix(self):
        doc1 = create_llb()
        doc1.prefix = "prefix"
        doc1.suffix = "suffix"
        doc1.add_block("test", "content")

        doc2 = create_llb()
        doc2.prefix = "prefix"
        doc2.suffix = "suffix"
        doc2.add_block("test", "content")

        doc3 = create_llb()
        doc3.prefix = "different"
        doc3.suffix = "suffix"
        doc3.add_block("test", "content")

        assert doc1 == doc2
        assert doc1 != doc3


class TestEdgeCases:
    def test_special_characters_in_content(self):
        doc = create_llb()
        special_content = "Line1\nLine2\n<tag>value</tag>"
        doc.add_block("test", special_content)
        rendered = doc.render()
        parsed = parse_llb(rendered)
        assert parsed.blocks[0].content == special_content

    def test_unicode_content(self):
        doc = create_llb()
        doc.add_block("note", "中文内容 日本語 한국어 🎉", lang="multi")
        rendered = doc.render()
        parsed = parse_llb(rendered)
        assert "中文内容" in parsed.blocks[0].content

    def test_multiple_meta_fields(self):
        doc = create_llb()
        doc.add_block(
            "log",
            "Error occurred",
            level="error",
            timestamp="2024-01-15T10:30:00Z",
            service="api",
        )
        assert len(doc.blocks[0].meta) == 3
