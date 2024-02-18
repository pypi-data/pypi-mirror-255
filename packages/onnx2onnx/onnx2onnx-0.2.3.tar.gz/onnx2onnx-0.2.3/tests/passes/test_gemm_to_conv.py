"""
Copyright Jianjin Liao 2024

:Author: Jianjin Liao
:Email: jianjin.liao@intel.com

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

from onnx2onnx import PassManager
from onnx2onnx.graph import OnnxGraph


def _build_test_graph(alpha, beta, transA, transB):
    gemm = make_node(
        "Gemm",
        inputs=["x", "B", "C"],
        outputs=["y"],
        name="gemm",
        alpha=float(alpha),
        beta=float(beta),
        transA=transA,
        transB=transB,
    )
    x_shape = (64, 1) if transA else (1, 64)
    b_shape = (32, 64) if transB else (64, 32)
    graph = make_graph(
        [gemm],
        "graph",
        [make_value_info("x", make_tensor_type_proto(1, x_shape))],
        [make_value_info("y", make_tensor_type_proto(1, [1, 32]))],
        [
            make_tensor("B", 1, b_shape, np.random.rand(*b_shape)),
            make_tensor("C", 1, [32], np.random.rand(32)),
        ],
    )
    return make_model(graph)


def _build_quantize_test_graph(alpha, beta, transA, transB):
    gemm = make_node(
        "Gemm",
        inputs=["A", "B", "C"],
        outputs=["Y"],
        name="gemm",
        alpha=float(alpha),
        beta=float(beta),
        transA=transA,
        transB=transB,
    )
    dequant = make_node(
        "DequantizeLinear",
        inputs=["x", "x_scale", "x_zero_point"],
        outputs=["B"],
        name="dequantzie",
        axis=0 if transB else 1,
    )

    a_shape = (64, 1) if transA else (1, 64)
    b_shape = (32, 64) if transB else (64, 32)
    graph = make_graph(
        [dequant, gemm],
        "graph",
        [make_value_info("A", make_tensor_type_proto(1, a_shape))],
        [make_value_info("Y", make_tensor_type_proto(1, [1, 32]))],
        [
            make_tensor("C", 1, [32], np.random.rand(32)),
            make_tensor(
                "x", 3, b_shape, np.random.randint(-128, 128, b_shape, dtype="int8")
            ),
            make_tensor("x_scale", 1, [32], np.random.rand(32)),
            make_tensor(
                "x_zero_point",
                3,
                [32],
                np.random.randint(-128, 128, [32], dtype="int8"),
            ),
        ],
    )
    return make_model(graph)


def test_rewriter():
    graph = OnnxGraph(_build_test_graph(1, 1, 0, 0))
    pm = PassManager(["initializer_to_constant", "gemm_to_conv"])
    graph = pm.optimize(graph, strict=True)
    onnx.checker.check_model(graph.model, True)


def test_rewriter_transB():
    graph = OnnxGraph(_build_test_graph(1, 1, 0, 1))
    pm = PassManager(["initializer_to_constant", "gemm_to_conv"])
    graph = pm.optimize(graph, strict=True)
    onnx.checker.check_model(graph.model, True)


def test_rewriter_transA():
    graph = OnnxGraph(_build_test_graph(1, 1, 1, 0))
    pm = PassManager(["initializer_to_constant", "gemm_to_conv"])
    graph = pm.optimize(graph, strict=True)
    onnx.checker.check_model(graph.model, True)


def test_quantize_rewriter():
    graph = OnnxGraph(_build_quantize_test_graph(1, 1, 0, 0))
    pm = PassManager(["initializer_to_constant", "gemm_to_conv"])
    graph = pm.optimize(graph, strict=True)
    onnx.checker.check_model(graph.model, True)


def test_quantize_rewriter_transA():
    graph = OnnxGraph(_build_quantize_test_graph(1, 1, 1, 0))
    pm = PassManager(["initializer_to_constant", "gemm_to_conv"])
    graph = pm.optimize(graph, strict=True)
    onnx.checker.check_model(graph.model, True)


def test_quantize_rewriter_transB():
    graph = OnnxGraph(_build_quantize_test_graph(1, 1, 0, 1))
    pm = PassManager(["initializer_to_constant", "gemm_to_conv"])
    graph = pm.optimize(graph, strict=True)
    onnx.checker.check_model(graph.model, True)


def test_quantize_rewriter_scale_alpha():
    graph = OnnxGraph(_build_quantize_test_graph(0.5, 1, 0, 1))
    pm = PassManager(["initializer_to_constant", "gemm_to_conv"])
    graph = pm.optimize(graph, strict=True)
    onnx.checker.check_model(graph.model, True)
