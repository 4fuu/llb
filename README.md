# LLB (Large Language Blocks)

A context packaging format designed for LLMs.

## Installation

```bash
pip install llb_doc
```

## Quick Start

```python
from llb_doc import create_llb, parse_llb

doc = create_llb()

# Method 1: Fluent API
doc.block("ticket", lang="en").meta(source="jira", priority="high").content(
    "User cannot upload files larger than 10MB"
).add()

# Method 2: Context manager
with doc.block("api", "json") as b:
    b.source = "storage_service"
    b.content = '{"max_size": 5242880, "unit": "bytes"}'

# Method 3: Direct add
doc.add_block("note", "前端限制与后端配置不一致", source="code_review", lang="zh")

# Render to LLB format
print(doc.render())

# Parse LLB text back to document
doc2 = parse_llb(doc.render())
```

### Output

```text
@block b1 ticket en
source=jira
priority=high

User cannot upload files larger than 10MB

@end b1

@block b2 api json
source=storage_service

{"max_size": 5242880, "unit": "bytes"}

@end b2

@block b3 note zh
source=code_review

前端限制与后端配置不一致

@end b3
```

### Block Structure

Each block follows this structure:

```text
@block <id> <type> [lang]
key1=value1
key2=value2

<content>

@end <id>
```

## Roadmap

- [x] Flat Mode (independent blocks)
- [ ] Graph Mode (`@ctx`, `@node`, `@edge` for graph-structured context)

## License

MIT
