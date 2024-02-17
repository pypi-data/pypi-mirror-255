import sys

sys.path.append("/opt/extensions")
import anyio
import typer
from server import Server

from lambchop.client import Client

app = typer.Typer()


@app.command()
def pinger():
    c = Client()
    out = anyio.run(c.ping)
    print(out)


@app.command()
def serve(port: int = typer.Option(1956, help="Port to listen on.")):
    s = Server(port=port)
    anyio.run(s.serve)


if __name__ == "__main__":
    app()
