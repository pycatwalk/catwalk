import asyncio
import json
import yaml
from catwalk import Graph, Compiler, Runtime
from catwalk_schema import validate_flow
from uvicorn import Config, Server

async def app(scope, receive, send):
    if scope["type"] != "http":
        return
    path = scope["path"]
    method = scope["method"]

    if path == "/run" and method == "POST":
        body = b""
        while True:
            message = await receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
                if not message.get("more_body"):
                    break
        try:
            data = yaml.safe_load(body.decode())
            validate_flow(data)
            nodes = [type("NS", (), n) for n in data["nodes"]]
            edges = [type("ES", (), e) for e in data["edges"]]
            g = Graph(nodes, edges)
            comp = Compiler()
            rt = Runtime(comp.compile(g))
            ctx = await rt.run()
            response = json.dumps({"status": "ok", "context": ctx}).encode()
            status = 200
        except Exception as e:
            response = json.dumps({"status": "error", "detail": str(e)}).encode()
            status = 400
    else:
        response = b'{"error": "not found"}'
        status = 404

    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [(b"content-type", b"application/json")],
    })
    await send({"type": "http.response.body", "body": response})

def serve(port=8000):
    config = Config(app=app, host="0.0.0.0", port=port, loop="asyncio")
    server = Server(config)
    print(f"CatWalk server running at http://127.0.0.1:{port}")
    asyncio.run(server.serve())

if __name__ == "__main__":
    serve()
