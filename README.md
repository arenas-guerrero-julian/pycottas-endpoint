<div align="center">

# 💫 SPARQL endpoint for COTTAS files

[![PyPI - Version](https://img.shields.io/pypi/v/pycottas-endpoint.svg?logo=pypi&label=PyPI&logoColor=silver)](https://pypi.org/project/pycottas-endpoint/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pycottas-endpoint.svg?logo=python&label=Python&logoColor=silver)](https://pypi.org/project/pycottas-endpoint/)

[![Test package](https://github.com/arenas-guerrero-julian/pycottas-endpoint/actions/workflows/test.yml/badge.svg)](https://github.com/arenas-guerrero-julian/pycottas-endpoint/actions/workflows/test.yml)
[![Publish package](https://github.com/arenas-guerrero-julian/pycottas-endpoint/actions/workflows/release.yml/badge.svg)](https://github.com/arenas-guerrero-julian/pycottas-endpoint/actions/workflows/release.yml)
[![Coverage Status](https://coveralls.io/repos/github/arenas-guerrero-julian/pycottas-endpoint/badge.svg?branch=main)](https://coveralls.io/github/arenas-guerrero-julian/pycottas-endpoint?branch=main)

[![license](https://img.shields.io/pypi/l/pycottas-endpoint.svg?color=%2334D058)](https://github.com/arenas-guerrero-julian/pycottas-endpoint/blob/main/LICENSE.txt)
[![types - Mypy](https://img.shields.io/badge/types-mypy-blue.svg)](https://github.com/python/mypy)

</div>

`pycottas-endpoint` can be used directly from the terminal to quickly serve COTTAS files through a SPARQL endpoint automatically deployed locally.

It can also be used to define custom SPARQL functions: the user defines and registers custom SPARQL functions, then the endpoint is started using `uvicorn`.

The deployed SPARQL endpoint can be used as a `SERVICE` in a federated SPARQL query from regular triplestores SPARQL endpoints. The endpoint is CORS enabled by default to enable querying it from client JavaScript (can be turned off).

## 📦️ Installation

Install from [PyPI](https://pypi.org/project/pycottas-endpoint/) with:

```shell
pip install pycottas-endpoint
```

The `uvicorn` and `gunicorn` dependencies are not included by default, if you want to install them use the optional dependency `web`:

```bash
pip install "pycottas-endpoint[web]"
```

If you want to use `pycottas-endpoint` as a CLI you can install with the optional dependency `cli`:

```bash
pip install "pycottas-endpoint[cli]"
```

## ⚡️ Quickly serve COTTAS files through a SPARQL endpoint

Use `pycottas-endpoint` as a command line interface (CLI) in your terminal to quickly serve one or multiple COTTAS files as a SPARQL endpoint.

You can use wildcard to provide multiple files, for example to serve all COTTAS files in the current directory you could run:

```bash
pycottas-endpoint serve '*.cottas'
```

> Then access the YASGUI SPARQL editor on http://localhost:8000

## ✨ Deploy your SPARQL endpoint

`pycottas-endpoint` enables you to easily define and deploy SPARQL endpoints based on RDFLib. Additionally it provides helpers to defines custom functions in the endpoint.

Checkout the [`example`](https://github.com/arenas-guerrero-julian/pycottas-endpoint/tree/main/example) folder for a complete working app example to get started, including a docker deployment. A good way to create a new SPARQL endpoint is to copy this `example` folder, and start from it.

### 🚨 Deploy as a standalone API

Deploy your SPARQL endpoint as a standalone API:

```python
from rdflib import Graph
from rdflib_endpoint import SparqlEndpoint
from pycottas import COTTASStore

# Start the SPARQL endpoint based on a RDFLib Graph backed by pycottas and register your custom functions
g = Graph(store=COTTASStore('my_file.cottas'))

# Then use either SparqlEndpoint or SparqlRouter, they take the same arguments
app = SparqlEndpoint(
    graph=g,
    path="/",
    cors_enabled=True,
    # Metadata used for the SPARQL service description and Swagger UI:
    title="SPARQL endpoint for COTTAS files",
    description="SPARQL endpoint for COTTAS files. \n[Source code](https://github.com/arenas-guerrero-julian/pycottas-endpoint)",
    version="0.1.0",
    public_url='https://your-endpoint-url/',
    # Example query displayed in YASGUI default tab
    example_query="""PREFIX myfunctions: <https://w3id.org/sparql-functions/>
SELECT ?concat ?concatLength WHERE {
    BIND("First" AS ?first)
    BIND(myfunctions:custom_concat(?first, "last") AS ?concat)
}""",
    # Additional example queries displayed in additional YASGUI tabs
    example_queries = {
    	"Bio2RDF query": {
        	"endpoint": "https://bio2rdf.org/sparql",
        	"query": """SELECT DISTINCT * WHERE {
    ?s a ?o .
} LIMIT 10""",
    	},
    	"Custom function": {
        	"query": """PREFIX myfunctions: <https://w3id.org/sparql-functions/>
SELECT ?concat ?concatLength WHERE {
    BIND("First" AS ?first)
    BIND(myfunctions:custom_concat(?first, "last") AS ?concat)
}""",
    	}
	}
)
```

Finally deploy this app using `uvicorn` (see below)

### 🛣️ Deploy as a router to include in an existing API

Deploy your SPARQL endpoint as an `APIRouter` to include in an existing `FastAPI` API. The `SparqlRouter` constructor takes the same arguments as the `SparqlEndpoint`, apart from `enable_cors` which needs be enabled at the API level.

```python
from fastapi import FastAPI
from rdflib import Dataset
from rdflib_endpoint import SparqlRouter
from pycottas import COTTASStore

g = Graph(store=COTTASStore('my_file.cottas'))
sparql_router = SparqlRouter(
    graph=g,
    path="/",
    # Metadata used for the SPARQL service description and Swagger UI:
    title="SPARQL endpoint for COTTAS files",
    description="SPARQL endpoint for COTTAS files. \n[Source code](https://github.com/arenas-guerrero-julian/pycottas-endpoint)",
    version="0.1.0",
    public_url='https://your-endpoint-url/',
)

app = FastAPI()
app.include_router(sparql_router)
```

> To deploy this route in a **Flask** app checkout how it has been done in the [curies mapping service](https://github.com/biopragmatics/curies/blob/main/src/curies/mapping_service/api.py) of the [Bioregistry](https://bioregistry.io/).

### 📝 Define custom SPARQL functions

This option makes it easier to define functions in your SPARQL endpoint, e.g. `BIND(myfunction:custom_concat("start", "end") AS ?concat)`. It can be used with the `SparqlEndpoint` and `SparqlRouter` classes.

Create a `app/main.py` file in your project folder with your custom SPARQL functions, and endpoint parameters:

````python
import rdflib
from rdflib import Dataset
from rdflib.plugins.sparql.evalutils import _eval
from rdflib_endpoint import SparqlEndpoint
from pycottas import COTTASStore

def custom_concat(query_results, ctx, part, eval_part):
    """Concat 2 strings in the 2 senses and return the length as additional Length variable
    """
    # Retrieve the 2 input arguments
    argument1 = str(_eval(part.expr.expr[0], eval_part.forget(ctx, _except=part.expr._vars)))
    argument2 = str(_eval(part.expr.expr[1], eval_part.forget(ctx, _except=part.expr._vars)))
    evaluation = []
    scores = []
    # Prepare the 2 result string, 1 for eval, 1 for scores
    evaluation.append(argument1 + argument2)
    evaluation.append(argument2 + argument1)
    scores.append(len(argument1 + argument2))
    scores.append(len(argument2 + argument1))
    # Append the results for our custom function
    for i, result in enumerate(evaluation):
        query_results.append(eval_part.merge({
            part.var: rdflib.Literal(result),
            # With an additional custom var for the length
            rdflib.term.Variable(part.var + 'Length'): rdflib.Literal(scores[i])
        }))
    return query_results, ctx, part, eval_part

# Start the SPARQL endpoint based on a RDFLib Graph backed by pycottas and register your custom functions
g = Graph(store=COTTASStore('my_file.cottas'))
# Use either SparqlEndpoint or SparqlRouter, they take the same arguments
app = SparqlEndpoint(
    graph=g,
    path="/",
    # Register the functions:
    functions={
        'https://w3id.org/sparql-functions/custom_concat': custom_concat
    },
    cors_enabled=True,
    # Metadata used for the SPARQL service description and Swagger UI:
    title="SPARQL endpoint for COTTAS files",
    description="SPARQL endpoint for COTTAS files. \n[Source code](https://github.com/arenas-guerrero-julian/pycottas-endpoint)",
    version="0.1.0",
    public_url='https://your-endpoint-url/',
    # Example queries displayed in the Swagger UI to help users try your function
    example_query="""PREFIX myfunctions: <https://w3id.org/sparql-functions/>
SELECT ?concat ?concatLength WHERE {
    BIND("First" AS ?first)
    BIND(myfunctions:custom_concat(?first, "last") AS ?concat)
}"""
)
````

### ✒️ Or directly define the custom evaluation

You can also directly provide the custom evaluation function, this will override the `functions`.

Refer to the [RDFLib documentation](https://rdflib.readthedocs.io/en/stable/_modules/examples/custom_eval.html) to define the custom evaluation function. Then provide it when instantiating the SPARQL endpoint:

```python
import rdflib
from rdflib.plugins.sparql.evaluate import evalBGP
from rdflib.namespace import FOAF, RDF, RDFS
from pycottas import COTTASStore

def custom_eval(ctx, part):
    """Rewrite triple patterns to get super-classes"""
    if part.name == "BGP":
        # rewrite triples
        triples = []
        for t in part.triples:
            if t[1] == RDF.type:
                bnode = rdflib.BNode()
                triples.append((t[0], t[1], bnode))
                triples.append((bnode, RDFS.subClassOf, t[2]))
            else:
                triples.append(t)
        # delegate to normal evalBGP
        return evalBGP(ctx, triples)
    raise NotImplementedError()

app = SparqlEndpoint(
    graph=g,
    custom_eval=custom_eval
)
```

### 🦄 Run the SPARQL endpoint

You can then run the SPARQL endpoint server from the folder where your script is defined with `uvicorn` on http://localhost:8000

```bash
cd example
uv run uvicorn main:app --reload
```

> Checkout in the `example/README.md` for more details, such as deploying it with docker.

## 🛠️ Contributing

To run the project in development and make a contribution checkout the [contributing page](https://github.com/arenas-guerrero-julian/pycottas-endpoint/blob/main/CONTRIBUTING.md).

## 🏅 Acknowledgements

`pycottas-endpoint` is a fork from [`rdflib-endpoint`](https://github.com/vemonet/rdflib-endpoint) by [Vincent Emonet](https://github.com/vemonet/rdflib-endpoint).
