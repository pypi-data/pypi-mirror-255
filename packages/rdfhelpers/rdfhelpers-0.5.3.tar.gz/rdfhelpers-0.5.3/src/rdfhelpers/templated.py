# Copyright (c) 2022, Ora Lassila & So Many Aircraft
# All rights reserved.
#
# See LICENSE for licensing information
#
# This module implements some useful functionality for querying with RDFLib.
#
import logging
import rdflib
import rdflib.plugins.sparql.processor
from rdflib import Literal, URIRef
import string
import numbers

def identity(x):
    return x

# Make a new dictionary with values mapped using a callable
def mapDict(dictionary, mapper=identity):
    return {key: mapper(value) for key, value in dictionary.items()}

# TEMPLATED QUERIES
#
# This mechanism can be used in lieu of RDFLib's "initBindings=" parameter for SPARQL queries *and
# updates* with the added benefit that replacements are not limited to SPARQL terms.
class Templated:

    @classmethod
    def query(cls, graph, template, **kwargs):
        q = cls.convert(template, kwargs) if kwargs else template
        logging.debug(q)
        return graph.query(q)

    @classmethod
    def update(cls, graph, template, **kwargs):
        q = cls.convert(template, kwargs) if kwargs else template
        logging.debug(q)
        graph.update(q)

    @classmethod
    def ask(cls, graph, ask_template, **kwargs):
        try:
            return graph.query(ask_template, **kwargs).askAnswer
        except Exception as e:
            logging.error("Maybe not an ASK query...")
            raise e

    @classmethod
    def convert(cls, template, kwargs):
        return string.Template(template).substitute(**mapDict(kwargs, mapper=cls.forSPARQL))

    @classmethod
    def forSPARQL(cls, thing):
        if isinstance(thing, URIRef) or isinstance(thing, Literal):
            return thing.n3()
        elif isinstance(thing, str):
            return thing  # if thing[0] == '?' else cls.forSPARQL(Literal(thing))
        elif isinstance(thing, bool):
            return "true" if thing else "false"
        elif isinstance(thing, numbers.Number):
            return thing
        elif thing is None:
            return ""
        else:
            raise ValueError("Cannot make a SPARQL compatible value: %s", thing)

class TemplatedQueryMixin:  # abstract, can be mixed with Graph or Store

    def query(self, querystring, **kwargs):
        return Templated.query(super(), querystring, **kwargs)

    def update(self, querystring, **kwargs):
        Templated.update(super(), querystring, **kwargs)

    def ask(self, querystring, **kwargs):
        return Templated.ask(self, querystring, **kwargs)  # no super() since the ask method is new

class TemplateWrapper:
    def __init__(self, graph):
        self._graph = graph

    def query(self, querystring, **kwargs):
        return Templated.query(self._graph, querystring, **kwargs)

    def update(self, querystring, **kwargs):
        Templated.update(self._graph, querystring, **kwargs)


# Make a new Graph instance from triples (an iterable)
def graphFrom(triples, add_to=None, graph_class=rdflib.Graph, **kwargs):
    if add_to is None:
        add_to = graph_class(**kwargs)
    for triple in triples:
        add_to.add(triple)
    return add_to if len(add_to) > 0 else None

class Composable:
    def __init__(self, contents=None):
        # Copy the graph from the Composable that was passed
        if isinstance(contents, Composable):
            self._graph = contents._graph
        # A graph was passed, use that one
        elif isinstance(contents, rdflib.Graph):
            self._graph = contents
        # An iterable was passed, let's assume it is an iterable of triples
        elif hasattr(contents, "__iter__"):
            self._graph = graphFrom(contents) or rdflib.Graph()
        # Create an empty graph
        elif contents is None:
            self._graph = rdflib.Graph()
        else:
            raise ValueError("Illegal contents: {}".format(contents))

    @property
    def result(self):
        return self._graph

    def __len__(self):
        return len(self._graph)

    def __add__(self, other):
        other_graph = None
        if isinstance(other, Composable):
            other_graph = other._graph
        elif isinstance(other, rdflib.Graph):
            other_graph = other
        elif hasattr(other, "__iter__"):
            other_graph = graphFrom(other)
        else:
            raise ValueError("Cannot be added to a graph: {}".format(other))
        if other_graph and len(other_graph) > 0:
            return self.__class__(self._graph + other_graph)
        else:
            # TODO: Could we just return self?
            return self.__class__(self._graph)

    def add(self, *triples):
        for triple in triples:
            self._graph.add(triple)
        return self

    def bind(self, prefix, namespace):
        self._graph.bind(prefix, namespace)
        return self

    def parse(self, *args, **kwargs):
        self._graph.parse(*args, **kwargs)
        return self

    def serialize(self, *args, **kwargs):
        self._graph.serialize(*args, **kwargs)

    def construct(self, template, **kwargs):
        # TODO: How do we confirm that `template` is a `CONSTRUCT` query?
        return self.__class__(graphFrom(Templated.query(self._graph, template, **kwargs)))

    def query(self, template, **kwargs):
        return Templated.query(self._graph, template, **kwargs)

    def update(self, template, **kwargs):
        Templated.update(self._graph, template, **kwargs)
        return self

    def call(self, function, **kwargs):
        result = function(self, **kwargs)
        return self

    def injectResult(self, target, context, function, **kwargs):
        logging.warning("Adding data to graph {}".format(context))
        return function(target, self.result, context, **kwargs)
