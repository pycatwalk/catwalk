# 🐈 CatWalk — Teach Me

CatWalk is a declarative workflow engine written in Python, defined entirely in YAML.  
It lets you create, connect, and run workflow nodes like *trigger*, *extraction*, *conditional*, and *execution* blocks — all without writing complex backend code.

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
| `catwalk run flow.yaml`      | Run a YAML workflow   |
| `catwalk add node`           | Add node              |
| `catwalk add edge`           | Add edge              |
| `catwalk update node`        | Update node           |
| `catwalk remove node`        | Remove node           |
| `catwalk validate flow.yaml` | Validate YAML         |
| `catwalk serve`              | Start HTTP API server |

---

## 🧠 Example Workflow

```yaml
nodes:
  - id: n1
    type: trigger
    name: start
    func: lambda ctx: {"user": "Wan"}

  - id: n2
    type: extraction
    name: get_name
    func: lambda ctx: ctx["n1"]["user"]

  - id: n3
    type: conditional
    name: is_active
    func: lambda ctx: True

  - id: n4
    type: execution
    name: greet
    func: lambda ctx: f"Hello {ctx['n2']}, active={ctx['n3']}"
edges:
  - from: n1
    to: n2
  - from: n2
    to: n3
  - from: n3
    to: n4
```

Run the workflow:

```bash
catwalk run flow.yaml
```

Expected output:

```
✅ Flow validation passed.
Executing flow...
Hello Wan, active=True
```

---

## 🧾 Validation

To check that your YAML flow is well-formed:

```bash
catwalk validate flow.yaml
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

Then send a YAML flow:

```bash
curl -X POST -H "Content-Type: text/yaml" \
--data-binary @flow.yaml http://127.0.0.1:9000/run
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
| `catwalk_schema.py` | YAML structure validator        |
| `catwalk_server.py` | HTTP server via uvicorn         |
| `flow.yaml`         | User-defined workflow file      |
| `install.sh`        | Installer script                |

---

## 🧩 Extending CatWalk

Add your own nodes by defining new functions or modules in the `nodes/` folder.
Example:

```python
def get_weather(ctx):
    return {"weather": "sunny"}
```

Add it in your YAML as:

```yaml
- id: n5
  type: extraction
  name: get_weather
  func: get_weather
```

---

## 💡 Design Principles

* **Readable**: Flows are YAML, easy to diff and share.
* **Composable**: Each node is a function.
* **Portable**: Runs from CLI or HTTP.
* **Framework-Free**: Only Python + Uvicorn.

---

## ✅ License

MIT © 2025 CatWalk Contributors
