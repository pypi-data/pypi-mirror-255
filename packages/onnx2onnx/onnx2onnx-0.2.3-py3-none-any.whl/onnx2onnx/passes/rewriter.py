"""
Copyright Wenyi Tang 2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

from abc import ABCMeta, abstractmethod
from typing import Any, Generator, List, Sequence

import numpy as np
import onnx
from onnx import numpy_helper
from onnx.helper import make_attribute

from onnx2onnx.graph import OnnxGraph

from .pattern import Pattern
from .utils import attribute_value


class Rewriter(metaclass=ABCMeta):
    """OnnxGraph rewriter to modify the graph"""

    def __init__(self, pattern: Pattern):
        assert isinstance(pattern, Pattern)
        self.pattern = pattern
        self.node_to_add = []
        self.node_to_remove = []

    @abstractmethod
    def rewrite(self, graph: OnnxGraph, nodes: List[onnx.NodeProto], *args, **kwargs):
        """Implement how to rewrite matched nodes in the graph

        Args:
            graph (OnnxGraph): an onnx graph
            nodes (List[NodeProto]): a list of matched nodes
        """

    def add(self, nodes: Sequence[onnx.NodeProto] | onnx.NodeProto):
        """Append nodes to be added to the graph

        Args:
            nodes: a single node or a list of nodes to add
        """
        if isinstance(nodes, onnx.NodeProto):
            self.node_to_add.append(nodes)
        elif isinstance(nodes, Sequence):
            assert all(isinstance(i, onnx.NodeProto) for i in nodes)
            self.node_to_add.extend(nodes)
        else:
            raise TypeError(
                f"Expect to add a node or a list of nodes, but got {type(nodes)}."
            )

    def remove(self, nodes: Sequence[onnx.NodeProto] | onnx.NodeProto):
        """Remove nodes from the graph.

        Args:
            nodes: a single node or a list of nodes to remove
        """
        if isinstance(nodes, onnx.NodeProto):
            self.node_to_remove.append(nodes)
        elif isinstance(nodes, Sequence):
            assert all(isinstance(i, onnx.NodeProto) for i in nodes)
            self.node_to_remove.extend(nodes)
        else:
            raise TypeError(
                f"Expect to add a node or a list of nodes, but got {type(nodes)}."
            )

    def match_and_rewrite(self, graph: OnnxGraph, *args, **kwargs) -> OnnxGraph:
        """Look up for matched patterns in the graph and rewrite it.

        Args:
            graph (OnnxGraph): onnx graph

        Returns:
            OnnxGraph: rewritten graph
        """
        matched_nodes = self.pattern.match(graph)
        if matched_nodes is None:
            return graph  # no nothing
        if not isinstance(matched_nodes, Generator):
            raise RuntimeError(
                f"{type(self.pattern)} match function is invalid! "
                f"It should yield matched nodes, but it returns {type(matched_nodes)}"
            )
        # pylint: disable=attribute-defined-outside-init
        self._graph = graph
        for nodes in matched_nodes:
            if isinstance(nodes, onnx.NodeProto):
                nodes = [nodes]
            if self.node_to_remove:
                # filter nodes that been removed in previous pass
                nodes = list(filter(lambda n: n not in self.node_to_remove, nodes))
            if nodes:
                self.rewrite(graph, nodes, *args, **kwargs)
        for node in self.node_to_add:
            graph.add_onnx_node(node)
        for node in self.node_to_remove:
            graph.remove_onnx_node(node)
        self.node_to_add.clear()
        self.node_to_remove.clear()
        return graph

    def get_input_node(
        self, node: onnx.NodeProto, i_or_s: int | str
    ) -> onnx.NodeProto | None:
        """Get the input node to the i-th input."""
        graph = self.graph
        # pylint: disable=protected-access
        if isinstance(i_or_s, int):
            i = i_or_s
            if i < 0:
                i += len(node.input)
            assert i < len(node.input), f"index {i} exceeds input number"
            if name := graph._out_to_node.get(node.input[i]):
                return graph.nodes[name]["pb"]
        else:
            name = i_or_s
            if name := graph._out_to_node.get(name):
                return graph.nodes[name]["pb"]

    def get_input_nodes(self, node: onnx.NodeProto) -> List[onnx.NodeProto]:
        """Get all input nodes for the given node."""
        return [self.get_input_node(node, i) for i in node.input]

    def get_output_node(
        self, node: onnx.NodeProto, i_or_s: int | str = 0
    ) -> onnx.NodeProto | None:
        """Get the output node from the i-th output."""
        graph = self.graph
        if isinstance(i_or_s, int):
            i = i_or_s
            if i < 0:
                i += len(node.output)
            assert i < len(node.output), f"index {i} exceeds output number"
            port = node.output[i]
        else:
            port = i_or_s
        for s in graph.onnx_successors(node):
            if port in s.input:
                return s

    def get_attribute(self, node: onnx.NodeProto, name: str):
        """Try to get the value of an attribute of the node.

        Args:
            node: a node
            name: name of the attribute
        """
        for attr in node.attribute:
            if attr.name == name:
                return attribute_value(attr)

    def set_attribute(self, node: onnx.NodeProto, name: str, value: Any):
        """Set a new value to an attribute of the node."""
        for attr in node.attribute:
            if attr.name == name:
                match attr.type:
                    case onnx.AttributeProto.FLOAT:
                        attr.f = float(value)
                    case onnx.AttributeProto.INT:
                        attr.i = int(value)
                    case onnx.AttributeProto.STRING:
                        attr.s = str(value).encode()
                    case onnx.AttributeProto.TENSOR:
                        attr.t = numpy_helper.from_array(value)
                    case onnx.AttributeProto.GRAPH:
                        attr.g = value
                    case onnx.AttributeProto.TYPE_PROTO:
                        attr.tp = value
                    case onnx.AttributeProto.FLOATS:
                        attr.floats.extend(value)
                    case onnx.AttributeProto.INTS:
                        attr.ints.extend(value)
                    case onnx.AttributeProto.STRINGS:
                        attr.strings.extend(i.encode() for i in value)
                    case onnx.AttributeProto.TENSORS:
                        attr.tensors.extend(value)
                    case onnx.AttributeProto.GRAPHS:
                        attr.graphs.extend(value)
                    case onnx.AttributeProto.TYPE_PROTOS:
                        attr.type_protos.extend(value)
                return
        node.attribute.append(make_attribute(name, value))

    def get_value(self, node: onnx.NodeProto):
        """Get value from a constant node."""
        if node.op_type == "Constant":
            return numpy_helper.to_array(node.attribute[0].t)
        elif node.op_type == "Shape":
            return np.asarray(self.graph.tensor_shape(node.input[0]))

    @property
    def graph(self) -> OnnxGraph:
        """Get the current graph."""
        return self._graph

    def __call__(self, graph: OnnxGraph, *args, **kwargs) -> OnnxGraph:
        """Make rewriter a callable."""
        return self.match_and_rewrite(graph, *args, **kwargs)

    def __iadd__(self, nodes: Sequence[onnx.NodeProto] | onnx.NodeProto):
        self.add(nodes)
        return self

    def __isub__(self, nodes: Sequence[onnx.NodeProto] | onnx.NodeProto):
        self.remove(nodes)
        return self
