# 🐈 CatWalk — Teach Me

CatWalk is a declarative workflow engine written in Python, defined entirely in JSON.  
It lets you create, connect, and run workflow nodes like *trigger*, *extraction*, *conditional*, and *execution* blocks — all without writing complex backend code.

## 📋 Table of Contents

- [⚙️ Install](#️-install)
- [🧩 CLI Commands](#-cli-commands)
- [🧠 Example Workflow](#-example-workflow)
- [📚 Comprehensive Tutorial](#-comprehensive-tutorial)
- [🧾 Validation](#-validation)
- [🌐 Serve as HTTP API](#-serve-as-http-api)
- [🧱 Architecture Overview](#-architecture-overview)
- [🧩 Extending CatWalk](#-extending-catwalk)
- [💡 Design Principles](#-design-principles)

> 📖 **Additional Resources:**
> - [CLI_TUTORIAL.md](CLI_TUTORIAL.md) - Detailed command-line interface guide
> - [REACTFLOW_INTEGRATION.md](REACTFLOW_INTEGRATION.md) - Frontend integration guide
> - [DEMO.sh](DEMO.sh) - Interactive demonstration script

---

## ⚙️ Install

```bash
curl -fsSL https://raw.githubusercontent.com/pycatwalk/catwalk/main/install.sh | bash
````

Once installed, use:

```bash
catwalk --help
```

---

## 🧩 CLI Commands

| Command                      | Description           |
| ---------------------------- | --------------------- |
| `catwalk run flow.json`      | Run a JSON workflow   |
| `catwalk add node`           | Add node              |
| `catwalk add edge`           | Add edge              |
| `catwalk update node`        | Update node           |
| `catwalk remove node`        | Remove node           |
| `catwalk validate flow.json` | Validate JSON         |
| `catwalk serve`              | Start HTTP API server |

---

## 🧠 Example Workflow

```json
{
  "nodes": [
    {
      "id": "n1",
      "type": "trigger",
      "name": "start",
      "func": "lambda ctx: {\"user\": \"Wan\"}"
    },
    {
      "id": "n2",
      "type": "extraction",
      "name": "get_name",
      "func": "lambda ctx: ctx[\"n1\"][\"user\"]"
    },
    {
      "id": "n3",
      "type": "conditional",
      "name": "is_active",
      "func": "lambda ctx: True"
    },
    {
      "id": "n4",
      "type": "execution",
      "name": "greet",
      "func": "lambda ctx: f\"Hello {ctx['n2']}, active={ctx['n3']}\""
    }
  ],
  "edges": [
    {
      "from": "n1",
      "to": "n2"
    },
    {
      "from": "n2",
      "to": "n3"
    },
    {
      "from": "n3",
      "to": "n4"
    }
  ]
}
```

Run the workflow:

```bash
catwalk run flow.json
```

Expected output:

```
✅ Flow validation passed.
Executing flow...
Hello Wan, active=True
```

---

## 📚 Comprehensive Tutorial

### Working with Nodes

#### Adding Nodes

You can add nodes to your workflow using several methods:

**Method 1: Direct JSON editing**

Start with a basic flow:
```json
{
  "nodes": [
    {
      "id": "n1",
      "type": "trigger",
      "name": "start",
      "func": "lambda ctx: {'input': 'Hello World'}"
    }
  ],
  "edges": []
}
```

Add a new processing node:
```json
{
  "nodes": [
    {
      "id": "n1",
      "type": "trigger",
      "name": "start", 
      "func": "lambda ctx: {'input': 'Hello World'}"
    },
    {
      "id": "n2",
      "type": "extraction",
      "name": "extract_length",
      "func": "lambda ctx: len(ctx['n1']['input'])"
    }
  ],
  "edges": [
    {
      "source": "n1",
      "target": "n2"
    }
  ]
}
```

**Method 2: CLI commands (future implementation)**
```bash
# Add a new node
catwalk add node --id n3 --type conditional --name check_length \
  --func "lambda ctx: ctx['n2'] > 5"

# Add with position for ReactFlow compatibility
catwalk add node --id n4 --type execution --name output \
  --func "lambda ctx: f'Length is {ctx[\"n2\"]}'" \
  --position '{"x": 400, "y": 100}'
```

#### Updating Nodes

**Update node properties:**
```json
// Before
{
  "id": "n2",
  "type": "extraction", 
  "name": "extract_length",
  "func": "lambda ctx: len(ctx['n1']['input'])"
}

// After - Updated function and name
{
  "id": "n2",
  "type": "extraction",
  "name": "extract_word_count", 
  "func": "lambda ctx: len(ctx['n1']['input'].split())"
}
```

**Update with ReactFlow positioning:**
```json
{
  "id": "n2",
  "type": "extraction",
  "name": "extract_word_count",
  "func": "lambda ctx: len(ctx['n1']['input'].split())",
  "position": {"x": 200, "y": 150},
  "data": {
    "description": "Counts words in input text",
    "category": "text-processing"
  }
}
```

#### Removing Nodes

When removing a node, also remove any edges that reference it:

**Before removal:**
```json
{
  "nodes": [
    {"id": "n1", "type": "trigger", "name": "start", "func": "..."},
    {"id": "n2", "type": "extraction", "name": "process", "func": "..."},
    {"id": "n3", "type": "execution", "name": "output", "func": "..."}
  ],
  "edges": [
    {"source": "n1", "target": "n2"},
    {"source": "n2", "target": "n3"}
  ]
}
```

**After removing n2:**
```json
{
  "nodes": [
    {"id": "n1", "type": "trigger", "name": "start", "func": "..."},
    {"id": "n3", "type": "execution", "name": "output", "func": "..."}
  ],
  "edges": [
    {"source": "n1", "target": "n3"}
  ]
}
```

### Working with Edges

#### Adding Edges

**Basic edge connection:**
```json
{
  "edges": [
    {
      "source": "n1",
      "target": "n2"
    }
  ]
}
```

**ReactFlow-compatible edge with ID:**
```json
{
  "edges": [
    {
      "id": "e1",
      "source": "n1", 
      "target": "n2",
      "animated": true,
      "style": {"stroke": "#f59e0b"}
    }
  ]
}
```

**Legacy format (still supported):**
```json
{
  "edges": [
    {
      "from": "n1",
      "to": "n2"
    }
  ]
}
```

#### Complex Edge Patterns

**Parallel processing:**
```json
{
  "nodes": [
    {"id": "input", "type": "trigger", "name": "data_source", "func": "..."},
    {"id": "process_a", "type": "extraction", "name": "path_a", "func": "..."},
    {"id": "process_b", "type": "extraction", "name": "path_b", "func": "..."},
    {"id": "merge", "type": "execution", "name": "combine", "func": "..."}
  ],
  "edges": [
    {"source": "input", "target": "process_a"},
    {"source": "input", "target": "process_b"},
    {"source": "process_a", "target": "merge"},
    {"source": "process_b", "target": "merge"}
  ]
}
```

**Conditional branching:**
```json
{
  "nodes": [
    {"id": "start", "type": "trigger", "name": "input", "func": "..."},
    {"id": "check", "type": "conditional", "name": "validate", "func": "..."},
    {"id": "success_path", "type": "execution", "name": "handle_success", "func": "..."},
    {"id": "error_path", "type": "execution", "name": "handle_error", "func": "..."}
  ],
  "edges": [
    {"source": "start", "target": "check"},
    {"source": "check", "target": "success_path"},
    {"source": "check", "target": "error_path"}
  ]
}
```

#### Updating Edges

**Change edge target:**
```json
// Before
{"source": "n1", "target": "n2"}

// After
{"source": "n1", "target": "n3"}
```

**Add edge styling:**
```json
// Before
{"source": "n1", "target": "n2"}

// After - with ReactFlow styling
{
  "id": "edge-n1-n2",
  "source": "n1",
  "target": "n2", 
  "animated": true,
  "style": {"strokeWidth": 2, "stroke": "#10b981"}
}
```

#### Removing Edges

Simply remove the edge object from the edges array:

```json
// Remove this edge
{"source": "n1", "target": "n2"}
```

### Complete Workflow Examples

#### Example 1: Text Processing Pipeline

```json
{
  "nodes": [
    {
      "id": "input",
      "type": "trigger",
      "name": "text_input",
      "func": "lambda ctx: {'text': 'Hello beautiful world!'}",
      "position": {"x": 100, "y": 100}
    },
    {
      "id": "clean",
      "type": "extraction", 
      "name": "clean_text",
      "func": "lambda ctx: ctx['input']['text'].lower().strip()",
      "position": {"x": 300, "y": 100}
    },
    {
      "id": "count_words",
      "type": "extraction",
      "name": "word_count", 
      "func": "lambda ctx: len(ctx['clean'].split())",
      "position": {"x": 500, "y": 50}
    },
    {
      "id": "count_chars",
      "type": "extraction",
      "name": "char_count",
      "func": "lambda ctx: len(ctx['clean'])",
      "position": {"x": 500, "y": 150}
    },
    {
      "id": "summary",
      "type": "execution",
      "name": "create_summary",
      "func": "lambda ctx: f'Text: {ctx[\"clean\"]} | Words: {ctx[\"count_words\"]} | Chars: {ctx[\"count_chars\"]}'",
      "position": {"x": 700, "y": 100}
    }
  ],
  "edges": [
    {"id": "e1", "source": "input", "target": "clean"},
    {"id": "e2", "source": "clean", "target": "count_words"},
    {"id": "e3", "source": "clean", "target": "count_chars"},
    {"id": "e4", "source": "count_words", "target": "summary"},
    {"id": "e5", "source": "count_chars", "target": "summary"}
  ]
}
```

#### Example 2: Data Validation and Processing

```json
{
  "nodes": [
    {
      "id": "data_source",
      "type": "trigger",
      "name": "load_data",
      "func": "lambda ctx: {'numbers': [1, 2, 3, 4, 5, -1, 10]}",
      "position": {"x": 100, "y": 200}
    },
    {
      "id": "validate",
      "type": "conditional",
      "name": "check_positive",
      "func": "lambda ctx: all(n >= 0 for n in ctx['data_source']['numbers'])",
      "position": {"x": 300, "y": 200}
    },
    {
      "id": "filter_positive",
      "type": "extraction", 
      "name": "remove_negatives",
      "func": "lambda ctx: [n for n in ctx['data_source']['numbers'] if n >= 0]",
      "position": {"x": 500, "y": 150}
    },
    {
      "id": "calculate_sum",
      "type": "execution",
      "name": "sum_numbers",
      "func": "lambda ctx: sum(ctx['filter_positive'])",
      "position": {"x": 700, "y": 150}
    },
    {
      "id": "handle_error",
      "type": "execution",
      "name": "error_message", 
      "func": "lambda ctx: 'Error: Found negative numbers in data'",
      "position": {"x": 500, "y": 250}
    }
  ],
  "edges": [
    {"source": "data_source", "target": "validate"},
    {"source": "validate", "target": "filter_positive"},
    {"source": "validate", "target": "handle_error"},
    {"source": "filter_positive", "target": "calculate_sum"}
  ]
}
```

### Node Types Explained

| Type | Purpose | Example Function |
|------|---------|------------------|
| `trigger` | Start nodes with no dependencies | `lambda ctx: {'data': 'initial_value'}` |
| `extraction` | Transform/extract data | `lambda ctx: ctx['prev_node']['field']` |
| `conditional` | Boolean logic/branching | `lambda ctx: ctx['prev_node'] > 10` |
| `execution` | Final actions/outputs | `lambda ctx: print(ctx['prev_node'])` |

### Best Practices

1. **Node IDs**: Use descriptive, unique identifiers
2. **Function Context**: Always access previous nodes via `ctx['node_id']`
3. **Error Handling**: Include validation nodes for robust workflows
4. **Positioning**: Add position data for ReactFlow compatibility
5. **Edge IDs**: Use meaningful edge IDs for complex workflows
6. **Validation**: Always run `catwalk validate` after modifications

---

## 🧾 Validation

To check that your JSON flow is well-formed:

```bash
catwalk validate flow.json
```

Outputs:

```
✅ Flow is valid.
```

Or an error like:

```
❌ Invalid flow: edge references unknown node: n5
```

---

## 🌐 Serve as HTTP API

You can run your workflows as HTTP endpoints.

```bash
catwalk serve --port 9000
```

Then send a JSON flow:

```bash
curl -X POST -H "Content-Type: application/json" \
--data-binary @flow.json http://127.0.0.1:9000/run
```

Response:

```json
{"status": "ok", "context": {"n4": "Hello Wan, active=True"}}
```

---

## 🧱 Architecture Overview

| Component           | Purpose                         |
| ------------------- | ------------------------------- |
| `cli.py`            | CLI entrypoint                  |
| `catwalk_core.py`   | Graph, Compiler, Runtime engine |
| `catwalk_schema.py` | JSON structure validator        |
| `catwalk_server.py` | HTTP server via uvicorn         |
| `flow.json`         | User-defined workflow file      |
| `install.sh`        | Installer script                |

---

## 🧩 Extending CatWalk

Add your own nodes by defining new functions or modules in the `nodes/` folder.
Example:

```python
def get_weather(ctx):
    return {"weather": "sunny"}
```

Add it in your JSON as:

```json
{
  "id": "n5",
  "type": "extraction",
  "name": "get_weather",
  "func": "get_weather"
}
```

---

## 💡 Design Principles

* **Readable**: Flows are JSON, easy to diff and share.
* **Composable**: Each node is a function.
* **Portable**: Runs from CLI or HTTP.
* **Framework-Free**: Only Python + Uvicorn.

---

## ✅ License

MIT © 2025 CatWalk Initiatives.