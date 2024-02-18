"""
Copyright Wenyi Tang 2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

from abc import ABCMeta, abstractmethod
from itertools import chain, permutations
from typing import Any, List, Optional

import networkx as nx
from networkx.algorithms.isomorphism import DiGraphMatcher
from onnx import AttributeProto
from onnx.helper import make_attribute

from onnx2onnx.graph import OnnxGraph

from .utils import attribute_value


class Pattern(metaclass=ABCMeta):
    """Pattern to be matched. A pattern can be ORed and ADDed.

    Example::

        p1 = SingleNodePattern("Conv")
        p2 = SingleNodePattern("Relu")
        conv_or_relu = p1 | p2  # same as `p1 + p2`
    """

    @abstractmethod
    def match(self, graph: OnnxGraph):
        """Implementation how to match in the graph

        Args:
            graph (OnnxGraph): onnx graph
        """

    def __or__(self, pattern: "Pattern") -> "Pattern":
        return OrPattern(self, pattern)

    def __add__(self, pattern: "Pattern") -> "Pattern":
        return OrPattern(self, pattern)


class OrPattern(Pattern):
    """A special pattern to match either p1 or p2."""

    def __init__(self, p1: Pattern, p2: Pattern):
        self.patterns = [p1, p2]

    def match(self, graph: OnnxGraph):
        yield from chain(*(p.match(graph) for p in self.patterns))


class SingleNodePattern(Pattern):
    """Match a single node type."""

    __id__ = 0

    def __init__(self, op_type: str):
        self.op_type = op_type
        self.attr: List[str | AttributeProto] = []
        self.id = SingleNodePattern.__id__
        SingleNodePattern.__id__ += 1

    def match(self, graph: OnnxGraph):
        if isinstance(graph, OnnxGraph):
            for node in graph:
                node_pb = graph.nodes[node]["pb"]
                if self._check(node_pb):
                    yield node_pb
        else:  # match a single node
            node_pb = graph
            if self._check(node_pb):
                yield node_pb

    def _check(self, node):
        return self.op_type == node.op_type and self._check_attr(node)

    def _check_attr(self, node):
        if not self.attr:
            return True
        match_table = {}  # all attribute to check
        for attr in self.attr:
            if isinstance(attr, str):
                match_table[attr] = None
            else:
                match_table[attr.name] = attr
        matched = 0  # matched number of attributes
        for attr in node.attribute:
            if attr.name in match_table:
                matched += 1 if self._match_attr(match_table[attr.name], attr) else 0
        return matched == len(match_table)

    def _match_attr(self, attr0, attr1):
        if attr0.type != attr1.type:
            return False
        return attribute_value(attr0) == attribute_value(attr1)

    def __hash__(self):
        return hash(self.op_type + str(self.id))

    def with_attr(
        self, name: str | AttributeProto, value: Optional[Any] = None
    ) -> "SingleNodePattern":
        """Match the node with specific attribute."""
        if isinstance(name, AttributeProto):
            self.attr.append(name)
        elif value is not None:
            self.attr.append(make_attribute(name, value))
        else:
            self.attr.append(name)
        return self


class GraphPattern(Pattern, nx.DiGraph):
    """Match a subgraph."""

    def __init__(self, dag: nx.DiGraph = None):
        if dag is not None:
            assert isinstance(dag, nx.DiGraph)
            assert all(isinstance(n, SingleNodePattern) for n in dag.nodes)
        super().__init__(dag)

    def add_node(self, node_for_adding, **attr) -> "GraphPattern":
        assert isinstance(node_for_adding, SingleNodePattern)
        attr.update(pattern=node_for_adding)
        super().add_node(node_for_adding, **attr)
        return self

    def add_edge(self, u_of_edge, v_of_edge, **attr) -> "GraphPattern":
        assert isinstance(u_of_edge, SingleNodePattern)
        assert isinstance(v_of_edge, SingleNodePattern)
        self.add_node(u_of_edge)
        self.add_node(v_of_edge)
        super().add_edge(u_of_edge, v_of_edge, **attr)
        return self

    def match(self, graph: OnnxGraph):
        yield from self._match_fast(graph)

    def _match_slow(self, graph: OnnxGraph):
        # matching by brute force searching
        h = self.to_undirected(as_view=True)
        g = graph.to_undirected(as_view=True)
        for node in list(h)[0].match(graph):
            if nodes := self._traverse(g, h, node.name):
                yield nodes

    def _traverse(self, g: nx.Graph, h: nx.Graph, n: str):
        visited = set()
        node_list = [(n, list(h)[0])]
        while node_list:
            x, y = node_list.pop(0)
            if x in visited:
                continue
            visited.add(x)
            paired = False
            for pair in permutations(g[x]):
                if all(list(i.match(j["pb"])) for i, j in zip(h[y], pair)):
                    node_list.extend((j, i) for i, j in zip(h[y], pair))
                    paired = True
                    break
            if not paired:
                return False
        return list(visited)

    def _match_fast(self, graph: OnnxGraph):
        # Matching subgraph using nx method
        def _nm(g, h):
            return list(h["pattern"].match(g["pb"]))

        matcher = DiGraphMatcher(graph, self, node_match=_nm)
        for matches in matcher.subgraph_isomorphisms_iter():
            yield [graph.nodes[key]["pb"] for key in matches.keys()]


class ConstantGraphPattern(Pattern):
    """Match each subgraph contains constant nodes"""

    def _is_deterministic(self, node) -> bool:
        return node.op_type not in {
            "RandomUniform",
            "RandomNormal",
            "RandomUniformLike",
            "RandomNormalLike",
            "Multinomial",
        }

    def _is_qdq(self, node) -> bool:
        return node.op_type in {
            "DequantizeLinear",
            "DynamicQuantizeLinear",
            "QuantizeLinear",
        }

    def _has_subgraph(self, node) -> bool:
        return any(
            attr.type in (AttributeProto.GRAPH, AttributeProto.GRAPHS)
            for attr in node.attribute
        )

    def match(self, graph: OnnxGraph):
        const_names = {None, ""}  # for inputs with empty (dangled) name
        # get from initializers
        const_names.update(i.name for i in graph.initializer)
        const_nodes = []
        for _, node_name in enumerate(nx.topological_sort(graph)):
            node = graph.nodes[node_name]["pb"]
            if not self._is_deterministic(node) or self._is_qdq(node):
                continue
            if self._has_subgraph(node):
                continue
            if all(i in const_names for i in node.input):
                const_nodes.append(node)
                const_names.update(node.output)
        # TODO: cluster into subgraphs
        yield const_nodes
