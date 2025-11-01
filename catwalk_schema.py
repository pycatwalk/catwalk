import yaml

FLOW_SCHEMA = {
    "required": ["nodes", "edges"],
    "properties": {
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "type", "name", "func"],
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string"},
                    "name": {"type": "string"},
                    "func": {"type": "string"},
                },
            },
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["from", "to"],
                "properties": {
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                },
            },
        },
    },
}

def validate_flow(flow_dict):
    if not isinstance(flow_dict, dict):
        raise ValueError("flow must be a dictionary")

    for key in FLOW_SCHEMA["required"]:
        if key not in flow_dict:
            raise ValueError(f"missing required key: {key}")

    nodes = flow_dict["nodes"]
    edges = flow_dict["edges"]
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("nodes and edges must be lists")

    node_ids = set()
    for node in nodes:
        for req in ["id", "type", "name", "func"]:
            if req not in node:
                raise ValueError(f"node missing required field: {req}")
        if node["id"] in node_ids:
            raise ValueError(f"duplicate node id: {node['id']}")
        node_ids.add(node["id"])

    for edge in edges:
        for req in ["from", "to"]:
            if req not in edge:
                raise ValueError(f"edge missing required field: {req}")
        if edge["from"] not in node_ids or edge["to"] not in node_ids:
            raise ValueError(f"edge references unknown node: {edge}")

    return True
