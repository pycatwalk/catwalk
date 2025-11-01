import json

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
                    "position": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"}
                        }
                    },
                    "data": {"type": "object"}
                },
            },
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                    "source": {"type": "string"},
                    "target": {"type": "string"},
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
        # Check if edge has required connection fields (either from/to or source/target)
        has_from_to = "from" in edge and "to" in edge
        has_source_target = "source" in edge and "target" in edge
        
        if not (has_from_to or has_source_target):
            raise ValueError(f"edge missing required connection fields (either 'from'/'to' or 'source'/'target'): {edge}")
        
        # Get the actual source and target node IDs
        from_node = edge.get("from") or edge.get("source")
        to_node = edge.get("to") or edge.get("target")
        
        if from_node not in node_ids or to_node not in node_ids:
            raise ValueError(f"edge references unknown node: {edge}")

    return True