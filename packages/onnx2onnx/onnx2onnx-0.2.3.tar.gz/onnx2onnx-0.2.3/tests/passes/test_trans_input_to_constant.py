"""
Copyright Wenyi Tang 2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

import numpy as np
from onnx.helper import (
    make_graph,
    make_model,
    make_node,
    make_tensor_type_proto,
    make_value_info,
)

from onnx2onnx import OnnxGraph, PassManager


def _build_test_graph():
    conv0 = make_node("Conv", inputs=["a", "w0"], outputs=["c"], group=1, name="conv0")
    graph = make_graph(
        [conv0],
        name="graph",
        inputs=[
            make_value_info("a", make_tensor_type_proto(1, [1, 3, 128, 127])),
            make_value_info("w0", make_tensor_type_proto(1, [8, 3, 3, 3])),
        ],
        outputs=[make_value_info("c", make_tensor_type_proto(1, [1, 8, 126, 125]))],
    )
    model = make_model(graph)
    return model


def test_trans_input_to_constant_with_config():
    graph = OnnxGraph(_build_test_graph())
    assert "w0" in graph.inputs
    pass_manager = PassManager(
        ["trans_input_to_constant"],
        configs={
            "trans_input_to_constant": dict(
                input_name="w0", value=np.ones([8, 3, 3, 3], "float32")
            )
        },
    )
    graph = pass_manager.optimize(graph)
    assert len(graph.inputs) == 1
    assert "w0" not in graph.inputs
