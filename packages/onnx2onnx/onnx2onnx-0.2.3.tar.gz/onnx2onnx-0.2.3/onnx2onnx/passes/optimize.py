"""
Copyright Wenyi Tang 2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

from contextlib import suppress
from typing import List

import networkx as nx
from onnx import NodeProto
from onnx.reference.reference_evaluator import ReferenceEvaluator

from . import PASSES, OnnxGraph
from .pattern import ConstantGraphPattern
from .rewriter import Rewriter
from .utils import make_constant

with suppress(ImportError):
    import onnxoptimizer

    @PASSES.register()
    def onnx_optimizer(graph: OnnxGraph):
        """Fuse op and remove isolated nodes."""
        return OnnxGraph(onnxoptimizer.optimize(graph.model))


with suppress(ImportError):
    import onnxsim

    @PASSES.register()
    def onnx_simplifier(graph: OnnxGraph):
        """Simplify onnx graph"""
        model_sim, succeed = onnxsim.simplify(graph.model)
        if succeed:
            return OnnxGraph(model_sim)
        return graph


@PASSES.register(name="fold_constant")
class FoldConstantPass(Rewriter):
    """Fold constants to a single node."""

    def __init__(self):
        super().__init__(pattern=ConstantGraphPattern())

    def _is_constant_or_qdq(self, node):
        return node.op_type in {"Constant", "DequantizeLinear", "QuantizeLinear"}

    def rewrite(self, graph: OnnxGraph, nodes: List[NodeProto]):
        # skip if all nodes are Constant
        if all(self._is_constant_or_qdq(node) for node in nodes):
            return
        subonnx = graph.onnx_subgraph(nodes)
        out_nodes = {}
        constants = []
        for node_name in nx.topological_sort(subonnx):
            node_pb = subonnx.nodes[node_name]["pb"]
            if subonnx.nodes[node_name]["has_output"]:
                for out_name in node_pb.output:
                    if out_name in subonnx.outputs:
                        out_nodes[out_name] = node_pb
        # filter out the outputs that are exactly constant's output
        outputs_eval = set(subonnx.outputs)
        for node in list(filter(lambda n: n.op_type == "Constant", nodes)):
            if set(node.output).issubset(outputs_eval):
                nodes.remove(node)
                outputs_eval.difference_update(node.output)
        evaluator = ReferenceEvaluator(subonnx.model)
        outputs = evaluator.run(outputs_eval, {})
        for output_name, out_value in zip(outputs_eval, outputs):
            constants.append(make_constant(output_name, out_value))
            constants[-1].output[0] = output_name  # keep the edge name
        self -= nodes
        self += constants
