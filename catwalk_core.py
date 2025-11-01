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
        return order


class Runtime:
    """Executes a compiled workflow in topological order."""

    def __init__(self, graph: Graph, order):
        self.graph = graph
        self.order = order

    async def run(self, ctx=None):
        ctx = ctx or {}
        for node_id in self.order:
            node = self.graph.nodes[node_id]
            func = getattr(node, "func", None)

            if isinstance(func, str):
                func = self._resolve_func(func)

            result = await self._execute(func, ctx)
            ctx[node_id] = result

        return ctx

    async def _execute(self, func, ctx):
        if func is None:
            return None
        if inspect.iscoroutinefunction(func):
            return await func(ctx)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, ctx)

    def _resolve_func(self, func_str):
        """Resolves 'module.func' or inline 'lambda' strings."""
        if func_str.strip().startswith("lambda"):
            return eval(func_str)
        parts = func_str.split(".")
        if len(parts) == 1:
            # single name in current globals
            return globals().get(func_str)
        mod_name = ".".join(parts[:-1])
        fn_name = parts[-1]
        mod = __import__(mod_name, fromlist=[fn_name])
        return getattr(mod, fn_name)
