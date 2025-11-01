import asyncio
import inspect

class Graph:
    """Represents the workflow graph structure."""

    def __init__(self, nodes, edges):
        # nodes: list of objects with at least .id and node attributes
        # edges: list of objects with either (source,target) or (from,to)
        self.nodes = {n.id: n for n in nodes}
        self.edges = edges
        self.adj = self._build_adjacency()

    def _edge_endpoints(self, e):
        src = getattr(e, "source", None) or getattr(e, "from", None)
        dst = getattr(e, "target", None) or getattr(e, "to", None)
        return src, dst

    def _build_adjacency(self):
        adj = {nid: [] for nid in self.nodes}
        for e in self.edges:
            src, dst = self._edge_endpoints(e)
            if src not in self.nodes or dst not in self.nodes:
                raise ValueError(f"Invalid edge {src} -> {dst}")
            adj[src].append(dst)
        return adj

    def get_start_nodes(self):
        targets = { (getattr(e, "target", None) or getattr(e, "to", None)) for e in self.edges }
        return [nid for nid in self.nodes if nid not in targets]


class Compiler:
    """Compiles a graph into a topologically sorted execution plan."""

    def compile(self, graph: Graph):
        visited = set()
        order = []

        def dfs(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            for nxt in graph.adj.get(node_id, []):
                dfs(nxt)
            order.append(node_id)

        for start in graph.get_start_nodes():
            dfs(start)

        order.reverse()
        return graph.nodes, order  # Return both nodes dict and execution order


class Runtime:
    def __init__(self, compiled_graph, order):
        self.graph = compiled_graph  # dict of node_id -> node objects
        self.order = order

    async def run(self):
        print("Executing flow...")
        ctx = {}
        for node_id in self.order:
            node = self.graph[node_id]
            func_code = getattr(node, 'func', None)
            if func_code:
                func = eval(func_code)
                result = func(ctx)
                ctx[node_id] = result
        print(ctx)
        return ctx
    