#!/usr/bin/env python3
import argparse
import json
import asyncio
import sys
from pathlib import Path
from catwalk_schema import validate_flow
from catwalk_core import Graph, Compiler, Runtime

def create_parser():
    """Create the main argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="catwalk", 
        description="CatWalk workflow framework CLI - Build and execute JSON workflows"
    )
    sub = parser.add_subparsers(dest="cmd", help="Available commands")

    # Run command
    run_cmd = sub.add_parser("run", help="Run a JSON workflow")
    run_cmd.add_argument("path", help="Path to the JSON workflow file")
    run_cmd.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    run_cmd.add_argument("--output", "-o", help="Save execution results to file")
    run_cmd.add_argument("--dry-run", action="store_true", help="Validate execution without running")

    # Node management
    node_cmd = sub.add_parser("node", help="Node management commands")
    node_sub = node_cmd.add_subparsers(dest="node_action")
    
    # Add node
    add_node = node_sub.add_parser("add", help="Add a new node")
    add_node.add_argument("--file", "-f", required=True, help="Workflow file")
    add_node.add_argument("--id", required=True, help="Node ID")
    add_node.add_argument("--type", required=True, choices=["trigger", "extraction", "conditional", "execution"], help="Node type")
    add_node.add_argument("--name", required=True, help="Node name")
    add_node.add_argument("--func", required=True, help="Node function")
    add_node.add_argument("--position", help="Node position as JSON (for ReactFlow)")
    add_node.add_argument("--data", help="Additional node data as JSON")

    # Update node
    update_node = node_sub.add_parser("update", help="Update an existing node")
    update_node.add_argument("--file", "-f", required=True, help="Workflow file")
    update_node.add_argument("--id", required=True, help="Node ID to update")
    update_node.add_argument("--type", choices=["trigger", "extraction", "conditional", "execution"], help="New node type")
    update_node.add_argument("--name", help="New node name")
    update_node.add_argument("--func", help="New node function")
    update_node.add_argument("--position", help="New node position as JSON")
    update_node.add_argument("--data", help="New node data as JSON")

    # Remove node
    remove_node = node_sub.add_parser("remove", help="Remove a node")
    remove_node.add_argument("--file", "-f", required=True, help="Workflow file")
    remove_node.add_argument("--id", required=True, help="Node ID to remove")
    remove_node.add_argument("--cascade", action="store_true", help="Also remove connected edges")

    # List nodes
    list_nodes = node_sub.add_parser("list", help="List all nodes")
    list_nodes.add_argument("--file", "-f", required=True, help="Workflow file")
    list_nodes.add_argument("--type", help="Filter by node type")
    list_nodes.add_argument("--format", choices=["table", "json", "simple"], default="simple", help="Output format")

    # Edge management
    edge_cmd = sub.add_parser("edge", help="Edge management commands")
    edge_sub = edge_cmd.add_subparsers(dest="edge_action")
    
    # Add edge
    add_edge = edge_sub.add_parser("add", help="Add a new edge")
    add_edge.add_argument("--file", "-f", required=True, help="Workflow file")
    add_edge.add_argument("--source", required=True, help="Source node ID")
    add_edge.add_argument("--target", required=True, help="Target node ID")
    add_edge.add_argument("--id", help="Edge ID (for ReactFlow)")
    add_edge.add_argument("--style", help="Edge style as JSON")
    add_edge.add_argument("--animated", action="store_true", help="Animated edge")

    # Remove edge
    remove_edge = edge_sub.add_parser("remove", help="Remove an edge")
    remove_edge.add_argument("--file", "-f", required=True, help="Workflow file")
    remove_edge.add_argument("--id", help="Edge ID to remove")
    remove_edge.add_argument("--source", help="Source node ID")
    remove_edge.add_argument("--target", help="Target node ID")

    # List edges
    list_edges = edge_sub.add_parser("list", help="List all edges")
    list_edges.add_argument("--file", "-f", required=True, help="Workflow file")
    list_edges.add_argument("--from", help="Filter edges from this node")
    list_edges.add_argument("--to", help="Filter edges to this node")

    # Validate command
    val_cmd = sub.add_parser("validate", help="Validate JSON flow")
    val_cmd.add_argument("path", help="Path to the JSON workflow file")
    val_cmd.add_argument("--detailed", action="store_true", help="Show detailed validation errors")
    val_cmd.add_argument("--fix", action="store_true", help="Attempt to fix common issues")

    # Serve command
    serve_cmd = sub.add_parser("serve", help="Start HTTP server")
    serve_cmd.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    serve_cmd.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    serve_cmd.add_argument("--reload", action="store_true", help="Auto-reload on file changes")

    # Info command
    info_cmd = sub.add_parser("info", help="Show workflow information")
    info_cmd.add_argument("path", help="Path to the JSON workflow file")
    info_cmd.add_argument("--stats", action="store_true", help="Show statistics")

    # Initialize command
    init_cmd = sub.add_parser("init", help="Initialize a new workflow")
    init_cmd.add_argument("path", help="Path for the new workflow file")
    init_cmd.add_argument("--template", choices=["simple", "reactflow", "complex"], default="simple", help="Workflow template")

    return parser

def load_workflow(path):
    """Load and validate a workflow file."""
    try:
        with open(path, 'r') as f:
            flow = json.load(f)
        validate_flow(flow)
        return flow
    except FileNotFoundError:
        print(f"❌ Error: File '{path}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in '{path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def save_workflow(path, flow):
    """Save a workflow to file."""
    try:
        validate_flow(flow)
        with open(path, 'w') as f:
            json.dump(flow, f, indent=2)
        print(f"✅ Workflow saved to '{path}'")
    except Exception as e:
        print(f"❌ Error saving workflow: {e}")
        sys.exit(1)

def handle_node_add(args):
    """Handle node addition."""
    flow = load_workflow(args.file)
    
    # Check if node ID already exists
    existing_ids = {node['id'] for node in flow['nodes']}
    if args.id in existing_ids:
        print(f"❌ Error: Node with ID '{args.id}' already exists")
        return

    # Create new node
    new_node = {
        "id": args.id,
        "type": args.type,
        "name": args.name,
        "func": args.func
    }
    
    # Add optional fields
    if args.position:
        try:
            new_node["position"] = json.loads(args.position)
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON in position argument")
            return
    
    if args.data:
        try:
            new_node["data"] = json.loads(args.data)
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON in data argument")
            return

    flow['nodes'].append(new_node)
    save_workflow(args.file, flow)
    print(f"✅ Added node '{args.id}' of type '{args.type}'")

def handle_node_update(args):
    """Handle node update."""
    flow = load_workflow(args.file)
    
    # Find node to update
    node = None
    for n in flow['nodes']:
        if n['id'] == args.id:
            node = n
            break
    
    if not node:
        print(f"❌ Error: Node '{args.id}' not found")
        return

    # Update fields
    if args.type:
        node['type'] = args.type
    if args.name:
        node['name'] = args.name
    if args.func:
        node['func'] = args.func
    if args.position:
        try:
            node['position'] = json.loads(args.position)
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON in position argument")
            return
    if args.data:
        try:
            node['data'] = json.loads(args.data)
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON in data argument")
            return

    save_workflow(args.file, flow)
    print(f"✅ Updated node '{args.id}'")

def handle_node_remove(args):
    """Handle node removal."""
    flow = load_workflow(args.file)
    
    # Remove node
    original_count = len(flow['nodes'])
    flow['nodes'] = [n for n in flow['nodes'] if n['id'] != args.id]
    
    if len(flow['nodes']) == original_count:
        print(f"❌ Error: Node '{args.id}' not found")
        return
    
    # Remove connected edges if cascade is enabled
    if args.cascade:
        original_edge_count = len(flow['edges'])
        flow['edges'] = [
            e for e in flow['edges'] 
            if not (e.get('source') == args.id or e.get('target') == args.id or 
                   e.get('from') == args.id or e.get('to') == args.id)
        ]
        removed_edges = original_edge_count - len(flow['edges'])
        if removed_edges > 0:
            print(f"✅ Also removed {removed_edges} connected edge(s)")

    save_workflow(args.file, flow)
    print(f"✅ Removed node '{args.id}'")

def handle_node_list(args):
    """Handle node listing."""
    flow = load_workflow(args.file)
    
    nodes = flow['nodes']
    if args.type:
        nodes = [n for n in nodes if n['type'] == args.type]
    
    if not nodes:
        print("No nodes found")
        return
    
    if args.format == "json":
        print(json.dumps(nodes, indent=2))
    elif args.format == "table":
        print(f"{'ID':<15} {'Type':<12} {'Name':<20} {'Function':<30}")
        print("-" * 80)
        for node in nodes:
            func_preview = node['func'][:27] + "..." if len(node['func']) > 30 else node['func']
            print(f"{node['id']:<15} {node['type']:<12} {node['name']:<20} {func_preview:<30}")
    else:  # simple
        for node in nodes:
            print(f"• {node['id']} ({node['type']}): {node['name']}")

def handle_edge_add(args):
    """Handle edge addition."""
    flow = load_workflow(args.file)
    
    # Verify source and target nodes exist
    node_ids = {node['id'] for node in flow['nodes']}
    if args.source not in node_ids:
        print(f"❌ Error: Source node '{args.source}' not found")
        return
    if args.target not in node_ids:
        print(f"❌ Error: Target node '{args.target}' not found")
        return
    
    # Create new edge
    new_edge = {
        "source": args.source,
        "target": args.target
    }
    
    if args.id:
        new_edge["id"] = args.id
    
    if args.style:
        try:
            new_edge["style"] = json.loads(args.style)
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON in style argument")
            return
    
    if args.animated:
        new_edge["animated"] = True

    flow['edges'].append(new_edge)
    save_workflow(args.file, flow)
    print(f"✅ Added edge from '{args.source}' to '{args.target}'")

def handle_edge_remove(args):
    """Handle edge removal."""
    flow = load_workflow(args.file)
    
    original_count = len(flow['edges'])
    
    if args.id:
        flow['edges'] = [e for e in flow['edges'] if e.get('id') != args.id]
    elif args.source and args.target:
        flow['edges'] = [
            e for e in flow['edges'] 
            if not ((e.get('source') == args.source and e.get('target') == args.target) or
                   (e.get('from') == args.source and e.get('to') == args.target))
        ]
    else:
        print("❌ Error: Must specify either --id or both --source and --target")
        return
    
    removed_count = original_count - len(flow['edges'])
    if removed_count == 0:
        print("❌ Error: No matching edge found")
        return
    
    save_workflow(args.file, flow)
    print(f"✅ Removed {removed_count} edge(s)")

def handle_edge_list(args):
    """Handle edge listing."""
    flow = load_workflow(args.file)
    
    edges = flow['edges']
    
    if getattr(args, 'from'):
        edges = [e for e in edges if e.get('source') == getattr(args, 'from') or e.get('from') == getattr(args, 'from')]
    
    if args.to:
        edges = [e for e in edges if e.get('target') == args.to or e.get('to') == args.to]
    
    if not edges:
        print("No edges found")
        return
    
    for edge in edges:
        source = edge.get('source') or edge.get('from')
        target = edge.get('target') or edge.get('to')
        edge_id = edge.get('id', '')
        id_part = f" ({edge_id})" if edge_id else ""
        print(f"• {source} → {target}{id_part}")

def handle_init(args):
    """Handle workflow initialization."""
    if Path(args.path).exists():
        print(f"❌ Error: File '{args.path}' already exists")
        return
    
    templates = {
        "simple": {
            "nodes": [
                {
                    "id": "start",
                    "type": "trigger",
                    "name": "Start Node",
                    "func": "lambda ctx: {'message': 'Hello World'}"
                }
            ],
            "edges": []
        },
        "reactflow": {
            "nodes": [
                {
                    "id": "start",
                    "type": "trigger", 
                    "name": "Start Node",
                    "func": "lambda ctx: {'data': [1, 2, 3]}",
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "process",
                    "type": "extraction",
                    "name": "Process Data",
                    "func": "lambda ctx: sum(ctx['start']['data'])",
                    "position": {"x": 300, "y": 100}
                }
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "start",
                    "target": "process"
                }
            ]
        },
        "complex": {
            "nodes": [
                {
                    "id": "input",
                    "type": "trigger",
                    "name": "Data Input",
                    "func": "lambda ctx: {'numbers': [1, 2, 3, 4, 5]}"
                },
                {
                    "id": "validate",
                    "type": "conditional", 
                    "name": "Validate Data",
                    "func": "lambda ctx: len(ctx['input']['numbers']) > 0"
                },
                {
                    "id": "process",
                    "type": "extraction",
                    "name": "Calculate Sum",
                    "func": "lambda ctx: sum(ctx['input']['numbers'])"
                },
                {
                    "id": "output",
                    "type": "execution",
                    "name": "Display Result", 
                    "func": "lambda ctx: f'Sum: {ctx[\"process\"]}'"
                }
            ],
            "edges": [
                {"source": "input", "target": "validate"},
                {"source": "validate", "target": "process"},
                {"source": "process", "target": "output"}
            ]
        }
    }
    
    template = templates[args.template]
    save_workflow(args.path, template)
    print(f"✅ Initialized '{args.template}' workflow in '{args.path}'")

def handle_info(args):
    """Handle workflow info display."""
    flow = load_workflow(args.file if hasattr(args, 'file') else args.path)
    
    node_count = len(flow['nodes'])
    edge_count = len(flow['edges'])
    
    print(f"📊 Workflow Information")
    print(f"   Nodes: {node_count}")
    print(f"   Edges: {edge_count}")
    
    if args.stats if hasattr(args, 'stats') else False:
        node_types = {}
        for node in flow['nodes']:
            node_type = node['type']
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print(f"\n📈 Node Types:")
        for node_type, count in node_types.items():
            print(f"   {node_type}: {count}")

def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        return

    try:
        if args.cmd == "run":
            with open(args.path) as f:
                flow = json.load(f)
            try:
                validate_flow(flow)
                if args.verbose or args.dry_run:
                    print("✅ Flow validation passed.")
                if args.dry_run:
                    print("🔍 Dry run complete - workflow is valid")
                    return
            except Exception as e:
                print(f"❌ Invalid flow: {e}")
                sys.exit(1)
            
            nodes = [type("NS", (), n) for n in flow["nodes"]]
            edges = [type("ES", (), e) for e in flow["edges"]]
            g = Graph(nodes, edges)
            comp = Compiler()
            
            compiled, order = comp.compile(g)
            rt = Runtime(compiled, order)
            
            if args.verbose:
                print("🚀 Executing flow...")
            
            result = asyncio.run(rt.run())
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"✅ Results saved to '{args.output}'")

        elif args.cmd == "validate":
            with open(args.path) as f:
                flow = json.load(f)
            try:
                validate_flow(flow)
                print("✅ Flow is valid.")
            except Exception as e:
                if args.detailed:
                    print(f"❌ Validation failed:")
                    print(f"   Error: {e}")
                    print(f"   File: {args.path}")
                else:
                    print(f"❌ Invalid flow: {e}")

        elif args.cmd == "serve":
            from catwalk_server import serve
            print(f"🌐 Starting server on {args.host}:{args.port}")
            serve(args.port)

        elif args.cmd == "node":
            if args.node_action == "add":
                handle_node_add(args)
            elif args.node_action == "update":
                handle_node_update(args)
            elif args.node_action == "remove":
                handle_node_remove(args)
            elif args.node_action == "list":
                handle_node_list(args)
            else:
                print("❌ Error: Unknown node action")

        elif args.cmd == "edge":
            if args.edge_action == "add":
                handle_edge_add(args)
            elif args.edge_action == "remove":
                handle_edge_remove(args)
            elif args.edge_action == "list":
                handle_edge_list(args)
            else:
                print("❌ Error: Unknown edge action")

        elif args.cmd == "init":
            handle_init(args)

        elif args.cmd == "info":
            handle_info(args)

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()