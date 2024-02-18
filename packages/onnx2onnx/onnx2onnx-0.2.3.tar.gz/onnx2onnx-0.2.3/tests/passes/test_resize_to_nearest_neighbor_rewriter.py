"""
Copyright Wenyi Tang 2023

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

import numpy as np
from onnx.helper import (
    make_graph,
    make_model,
    make_node,
    make_tensor,
    make_tensor_type_proto,
    make_value_info,
)

from onnx2onnx.graph import OnnxGraph
from onnx2onnx.passes import PASSES


def _build_test_graph():
    resize = make_node(
        "Resize",
        inputs=["x", "roi", "scales", "sizes"],
        outputs=["y"],
        name="resize",
        coordinate_transformation_mode="half_pixel",
        mode="cubic",
    )
    graph = make_graph(
        [resize],
        "graph",
        [make_value_info("x", make_tensor_type_proto(1, [1, 3, 8, 8]))],
        [make_value_info("y", make_tensor_type_proto(1, None))],
        [make_tensor("scales", 1, [4], np.array([1, 1, 2, 2], "float32"))],
    )
    return make_model(graph)


def test_rewriter():
    graph = OnnxGraph(_build_test_graph())
    rewriter = PASSES.get("resize_to_nearest_neighbor")
    graph = rewriter(graph)
    assert "nearest" == rewriter.get_attribute(graph.nodes["resize"]["pb"], "mode")
    assert "asymmetric" == rewriter.get_attribute(
        graph.nodes["resize"]["pb"], "coordinate_transformation_mode"
    )
