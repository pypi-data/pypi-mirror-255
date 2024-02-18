"""
Copyright Wenyi Tang 2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

from copy import deepcopy

import numpy as np
from onnx import numpy_helper
from onnx.helper import (
    make_graph,
    make_model,
    make_node,
    make_operatorsetid,
    make_tensor_type_proto,
    make_value_info,
)
from onnx.reference import ReferenceEvaluator

from onnx2onnx import PassManager
from onnx2onnx.graph import OnnxGraph


def _build_graph(blocksize: int):
    s2d = make_node("SpaceToDepth", ["x"], ["y"], "s2d", blocksize=blocksize)
    graph = make_graph(
        [s2d],
        "graph",
        [make_value_info("x", make_tensor_type_proto(1, [1, 3, 192, 192]))],
        [
            make_value_info(
                "y",
                make_tensor_type_proto(
                    1, [1, 3 * blocksize**2, 192 // blocksize, 192 // blocksize]
                ),
            )
        ],
    )
    return make_model(graph, opset_imports=[make_operatorsetid("", 19)])


def _build_qdq_graph(blocksize: int, channelwise=False):
    s2d = make_node("SpaceToDepth", ["x"], ["y"], "s2d", blocksize=blocksize)
    qlinear = make_node("QuantizeLinear", ["y", "s0", "z0"], ["q"], "qlinear")
    dqlinear = make_node("DequantizeLinear", ["q", "s1", "z1"], ["dq"], "dqlinear")
    ic = 3
    oc = 3 * blocksize**2
    qc = [oc] if channelwise else [1]
    graph = make_graph(
        [s2d, qlinear, dqlinear],
        "graph",
        [make_value_info("x", make_tensor_type_proto(1, [1, ic, 192, 192]))],
        [
            make_value_info(
                "dq",
                make_tensor_type_proto(1, [1, oc, 192 // blocksize, 192 // blocksize]),
            )
        ],
        [
            numpy_helper.from_array(np.ones(qc, "float32"), "s0"),
            numpy_helper.from_array(np.zeros(qc, "uint8"), "z0"),
            numpy_helper.from_array(np.ones(qc, "float32"), "s1"),
            numpy_helper.from_array(np.zeros(qc, "uint8"), "z1"),
        ],
    )
    return make_model(graph, opset_imports=[make_operatorsetid("", 19)])


def test_blocksize_2():
    model = _build_graph(2)
    graph = OnnxGraph(model)
    pm = PassManager(["space2depth_to_conv"])
    graph = pm.optimize(graph, strict=True)

    assert any(graph.nodes[op]["pb"].op_type == "Conv" for op in graph)

    runner1 = ReferenceEvaluator(model)
    runner2 = ReferenceEvaluator(graph.model)
    x = np.random.uniform(0, 1, size=[1, 3, 192, 192]).astype(np.float32)
    y1 = runner1.run(None, {"x": x})[0]
    y2 = runner2.run(None, {"x": x})[0]
    assert np.allclose(y1, y2)


def test_blocksize_3():
    model = _build_graph(3)
    graph = OnnxGraph(model)
    pm = PassManager(["space2depth_to_conv"])
    graph = pm.optimize(graph, strict=True)

    assert any(graph.nodes[op]["pb"].op_type == "Conv" for op in graph)

    runner1 = ReferenceEvaluator(model)
    runner2 = ReferenceEvaluator(graph.model)
    x = np.random.uniform(0, 1, size=[1, 3, 192, 192]).astype(np.float32)
    y1 = runner1.run(None, {"x": x})[0]
    y2 = runner2.run(None, {"x": x})[0]
    assert np.allclose(y1, y2)


def test_qdq_blocksize_2():
    model = _build_qdq_graph(2)
    graph = OnnxGraph(deepcopy(model))
    pm = PassManager(["initializer_to_constant", "space2depth_to_qconv"])
    graph = pm.optimize(graph, strict=True)

    assert any(graph.nodes[op]["pb"].op_type == "Conv" for op in graph)

    runner1 = ReferenceEvaluator(model)
    runner2 = ReferenceEvaluator(graph.model)
    x = np.random.uniform(0, 1, size=[1, 3, 192, 192]).astype(np.float32)
    y1 = runner1.run(None, {"x": x})[0]
    y2 = runner2.run(None, {"x": x})[0]
    assert np.allclose(y1, y2)
