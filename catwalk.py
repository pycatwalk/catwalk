#!/usr/bin/env python3
import argparse
import yaml
import asyncio
from catwalk_schema import validate_flow
from catwalk_core import Graph, Compiler, Runtime

def main():
    parser = argparse.ArgumentParser(prog="catwalk", description="CatWalk workflow framework CLI")
    sub = parser.add_subparsers(dest="cmd")

    # run
    run_cmd = sub.add_parser("run", help="Run a YAML workflow")
    run_cmd.add_argument("path")

    # node/edge management
    sub.add_parser("add", help="Add node or edge").add_argument("type")
    sub.add_parser("remove", help="Remove node or edge").add_argument("type")
    sub.add_parser("update", help="Update node or edge").add_argument("type")

    # validate
    val_cmd = sub.add_parser("validate", help="Validate YAML flow")
    val_cmd.add_argument("path")

    # serve
    serve_cmd = sub.add_parser("serve", help="Start HTTP server")
    serve_cmd.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.cmd == "run":
        with open(args.path) as f:
            flow = yaml.safe_load(f)
        try:
            validate_flow(flow)
            print("✅ Flow validation passed.")
        except Exception as e:
            print(f"❌ Invalid flow: {e}")
            exit(1)
        nodes = [type("NS", (), n) for n in flow["nodes"]]
        edges = [type("ES", (), e) for e in flow["edges"]]
        g = Graph(nodes, edges)
        comp = Compiler()
        rt = Runtime(comp.compile(g))
        asyncio.run(rt.run())

    elif args.cmd == "validate":
        with open(args.path) as f:
            flow = yaml.safe_load(f)
        try:
            validate_flow(flow)
            print("✅ Flow is valid.")
        except Exception as e:
            print(f"❌ Invalid flow: {e}")

    elif args.cmd == "serve":
        from catwalk_server import serve
        serve(args.port)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
