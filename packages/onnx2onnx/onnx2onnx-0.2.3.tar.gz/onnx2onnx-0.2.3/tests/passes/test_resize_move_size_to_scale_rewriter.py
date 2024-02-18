"""
Copyright Wenyi Tang 2023

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

import numpy as np
from onnx import TensorProto
from onnx.helper import (
    make_graph,
    make_model,
    make_node,
    make_tensor,
    make_tensor_type_proto,
    make_value_info,
)

from onnx2onnx.graph import OnnxGraph
from onnx2onnx.passes.convert import initializer_to_constant
from onnx2onnx.passes.transforms import ResizeMoveSizeToScaleRewriter


def _build_test_graph():
    resize = make_node(
        "Resize",
        inputs=["x", "roi", "scales", "sizes"],
        outputs=["y"],
        name="resize",
        coordinate_transformation_mode="tf_crop_and_resize",
        mode="cubic",
        axes=[2, 3],
    )
    graph = make_graph(
        [resize],
        "graph",
        [make_value_info("x", make_tensor_type_proto(1, [1, 3, 8, 8]))],
        [make_value_info("y", make_tensor_type_proto(1, None))],
        [
            make_tensor(
                "roi", TensorProto.INT64, [4], np.array([2, 2, 6, -2], "int64")
            ),
            make_tensor("sizes", TensorProto.INT64, [2], np.array([8, 8], "int64")),
        ],
    )
    return make_model(graph)


def test_roi_rewriter():
    graph = OnnxGraph(_build_test_graph())
    rewriter = ResizeMoveSizeToScaleRewriter()
    graph = rewriter(initializer_to_constant(graph))
