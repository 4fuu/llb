"""LLB (Large Language Blocks) - Demo Script

Demonstrates core features: 3 usage patterns, flat/graph modes, meta generators, and sorters.
"""

from llb_doc import (
    Block,
    block_sorter,
    create_graph,
    create_llb,
    meta_generator,
    parse_llb,
)


# =============================================================================
#  1. FLAT MODE - Three Usage Patterns
# =============================================================================

print("=" * 50)
print("  1. Flat Mode - Three Usage Patterns")
print("=" * 50 + "\n")

doc = create_llb()

# Pattern 1: Fluent API (builder pattern)
doc.block("ticket", lang="en").meta(source="jira", priority="high").content(
    "User cannot upload files larger than 10MB"
).add()

# Pattern 2: Context manager
with doc.block("api", "json") as b:
    b.meta["source"] = "storage_service"
    b.content = '{"max_size": 5242880}'

# Pattern 3: Direct add
doc.add_block("note", "Frontend limit mismatch", source="review")

print(doc.render())


# =============================================================================
#  2. Meta Generators & Block Sorters
# =============================================================================

print("\n" + "=" * 50)
print("  2. Meta Generators & Block Sorters")
print("=" * 50 + "\n")


@meta_generator("word_count")
def gen_word_count(block: Block) -> str:
    return str(len(block.content.split()))


@block_sorter("by_priority")
def sort_priority(blocks: list[Block]) -> list[Block]:
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(blocks, key=lambda b: order.get(b.meta.get("priority", ""), 99))


doc2 = create_llb(generators=[gen_word_count], sorters=[sort_priority])
doc2.add_block("task", "Fix critical bug now", priority="high")
doc2.add_block("task", "Add new feature later", priority="low")
doc2.add_block("task", "Update documentation", priority="medium")

print("Sorted by priority (with auto word_count):")
print(doc2.render(order="by_priority"))


# =============================================================================
#  3. GRAPH MODE - Nodes, Edges & Focus Rendering
# =============================================================================

print("\n" + "=" * 50)
print("  3. Graph Mode - Nodes, Edges & Focus Rendering")
print("=" * 50 + "\n")

g = create_graph()

# Add nodes (3 patterns same as flat mode)
g.node("concept").id("python").meta(category="language").content("Python").add()

with g.node("concept") as n:
    n.id = "django"
    n.meta["category"] = "framework"
    n.content = "Django"

g.add_node("concept", "Flask", id_="flask", category="framework")

# Add edges
g.add_edge("python", "django", "has_framework")
g.add_edge("python", "flask", "has_framework")

print("Focus on 'python' with radius=1:")
print(g.render(focus="python", radius=1))


# =============================================================================
#  4. Parse LLB Format
# =============================================================================

print("\n" + "=" * 50)
print("  4. Parse LLB Format")
print("=" * 50 + "\n")

llb_text = """@block B1 ticket en
source=jira

User cannot login

@end B1"""

parsed = parse_llb(llb_text)
print(f"Parsed {len(parsed)} block(s): {[b.id for b in parsed.blocks]}")
