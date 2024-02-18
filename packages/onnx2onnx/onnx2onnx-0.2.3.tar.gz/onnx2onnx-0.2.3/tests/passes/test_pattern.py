"""
Copyright Wenyi Tang 2023

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

import numpy as np
import onnx
from onnx.helper import (
    make_graph,
    make_model,
    make_node,
    make_tensor,
    make_tensor_type_proto,
    make_value_info,
)

from onnx2onnx import OnnxGraph
from onnx2onnx.passes.pattern import GraphPattern, SingleNodePattern


def _build_test_graph1():
    conv0 = make_node("Conv", inputs=["a", "w0"], outputs=["c"], group=2, name="conv0")
    conv1 = make_node("Conv", inputs=["c", "w1"], outputs=["d"], group=1, name="conv1")
    graph = make_graph(
        [conv0, conv1],
        name="graph",
        inputs=[make_value_info("a", make_tensor_type_proto(1, [1, 3, 128, 127]))],
        outputs=[make_value_info("d", make_tensor_type_proto(1, None))],
        initializer=[
            make_tensor(
                "w0",
                1,
                [8, 3, 3, 3],
                np.ones([8, 3, 3, 3], "float32").tobytes(),
                raw=True,
            ),
            make_tensor(
                "w1",
                1,
                [8, 8, 3, 3],
                np.ones([8, 8, 3, 3], "float32").tobytes(),
                raw=True,
            ),
        ],
    )
    model = make_model(graph)
    return model


def test_single_node_match():
    graph = OnnxGraph(_build_test_graph1())
    pattern = SingleNodePattern("Conv")
    nodes = list(pattern.match(graph))
    assert len(nodes) == 2
    for i in nodes:
        assert isinstance(i, onnx.NodeProto)
        assert i.op_type == "Conv"

    pattern = SingleNodePattern("Conv").with_attr("group", 1)
    nodes = list(pattern.match(graph))
    assert len(nodes) == 1
    for i in nodes:
        assert i.attribute[0].i == 1

    pattern1 = SingleNodePattern("Conv").with_attr("group", 1)
    pattern2 = SingleNodePattern("Conv").with_attr("group", 2)
    nodes = list((pattern1 | pattern2).match(graph))
    assert len(nodes) == 2
    for i in nodes:
        assert isinstance(i, onnx.NodeProto)
        assert i.op_type == "Conv"
        assert i.attribute[0].i in (1, 2)


def test_or_pattern():
    graph = OnnxGraph(_build_test_graph1())
    pattern1 = SingleNodePattern("Conv").with_attr("group", 1)
    pattern2 = SingleNodePattern("Conv").with_attr("group", 2)
    nodes = list((pattern1 | pattern2).match(graph))
    assert len(nodes) == 2
    for i in nodes:
        assert isinstance(i, onnx.NodeProto)
        assert i.op_type == "Conv"
        assert i.attribute[0].i in (1, 2)


def test_subgraph_match():
    graph = OnnxGraph(_build_test_graph1())
    pattern = GraphPattern().add_edge(
        SingleNodePattern("Conv"), SingleNodePattern("Conv")
    )
    nodes = list(pattern.match(graph))
    assert len(nodes) == 1
    assert len(nodes[0]) == 2
