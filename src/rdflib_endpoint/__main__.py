import glob
import sys
from typing import List

import click
import uvicorn
from rdflib import Dataset, Graph
import pycottas

from rdflib_endpoint import SparqlEndpoint


@click.group()
def cli() -> None:
    """Quickly serve RDF files as SPARQL endpoint with RDFLib Endpoint"""


@cli.command(help="Serve a local RDF file (or .cottas) as a SPARQL endpoint")
@click.argument("files", nargs=-1)
@click.option("--host", default="localhost", help="Host of the SPARQL endpoint")
@click.option("--port", default=8000, help="Port of the SPARQL endpoint")
@click.option("--store", default="default", help="Store used by RDFLib: default or Oxigraph")
@click.option("--enable-update", is_flag=True, help="Enable SPARQL updates")
def serve(files: List[str], host: str, port: int, store: str, enable_update: bool) -> None:
    run_serve(files, host, port, store, enable_update)


def run_serve(files: List[str], host: str, port: int, store: str = "default", enable_update: bool = False) -> None:
    if store == "oxigraph":
        store = store.capitalize()


    file = files[0]

    # Si es un archivo .cottas
    if file.lower().endswith(".cottas"):
        click.echo(click.style("INFO", fg="green") + f": 📦 Cargando archivo COTTAS → {file}")
        g = Graph(store=pycottas.COTTASStore(file))

    # Si es otro formato RDF
    else:
        g = Dataset(store=store, default_union=True)
        file_list = glob.glob(file)
        for f in file_list:
            g.parse(f)
            click.echo(
                click.style("INFO", fg="green")
                + ": 📥️ Loaded triples from "
                + click.style(str(f), bold=True)
                + ", for a total of "
                + click.style(str(len(g)), bold=True)
            )

    # Crear y lanzar el endpoint SPARQL
    app = SparqlEndpoint(
        graph=g,
        enable_update=enable_update,
        example_query="""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {
    ?s ?p ?o .
} LIMIT 100""",
    )
    uvicorn.run(app, host=host, port=port)


@cli.command(help="Merge and convert local RDF files to another format easily")
@click.argument("files", nargs=-1)
@click.option("--output", default="output.ttl", help="Output file name")
@click.option("--store", default="default", help="Store used by RDFLib: default or Oxigraph")
def convert(files: List[str], output: str, store: str) -> None:
    run_convert(files, output, store)


def run_convert(files: List[str], output: str, store: str = "default") -> None:
    if store == "oxigraph":
        store = store.capitalize()
    g = Dataset(store=store, default_union=True)
    for glob_file in files:
        file_list = glob.glob(glob_file)
        for f in file_list:
            g.parse(f)
            click.echo(
                click.style("INFO", fg="green")
                + ": 📥️ Loaded triples from "
                + click.style(str(f), bold=True)
                + ", for a total of "
                + click.style(str(len(g)), bold=True)
            )

    out_format = "ttl"
    if output.endswith(".nt"):
        out_format = "nt"
    elif output.endswith(".xml") or output.endswith(".rdf"):
        out_format = "xml"
    elif output.endswith(".json") or output.endswith(".jsonld"):
        out_format = "json-ld"
    elif output.endswith(".trig"):
        out_format = "trig"

    g.serialize(output, format=out_format)


if __name__ == "__main__":
    sys.exit(cli())
