import sys
from typing import List

import click
import uvicorn
from rdflib import Dataset, Graph
import pycottas

from pycottas_endpoint import SparqlEndpoint


@click.group()
def cli() -> None:
    """Quickly serve COTTAS files as an SPARQL endpoint with pycottas endpoint."""


@cli.command(help="Serve a local COTTAS file as an SPARQL endpoint")
@click.argument("file")
@click.option("--host", default="localhost", help="Host of the SPARQL endpoint")
@click.option("--port", default=8000, help="Port of the SPARQL endpoint")
def serve(file: str, host: str, port: int) -> None:
    run_serve(file, host, port)


def run_serve(file: str, host: str, port: int) -> None:
    # There is one COTTAS file
    if type(file) is str:
        click.echo(click.style("INFO", fg="green") + f": 📦 Loading COTTAS file → {file}")
        g = Graph(store=pycottas.COTTASStore(file))

    # There are multiple COTTAS files (it is a list)
    else:
        click.echo(click.style("ERROR", fg="red") + ": 🚫 you can't serve multiples COTTAS files at the same time. Use pycottas to merge them all into one file.")
        sys.exit(1)

    # Create and run the SPARQL endpoint
    app = SparqlEndpoint(
        graph=g,
        enable_update=False,
        example_query="""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {
    ?s ?p ?o .
} LIMIT 100""",
    )
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    sys.exit(cli())
