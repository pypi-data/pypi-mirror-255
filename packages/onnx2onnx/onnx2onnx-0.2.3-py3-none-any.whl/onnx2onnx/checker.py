"""
Copyright Wenyi Tang 2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

# pylint: disable=import-outside-toplevel

from tempfile import TemporaryDirectory
from typing import Dict, Literal

import numpy as np
import onnx

from .graph import OnnxGraph


def _get_eval_backend(backend, model):
    if backend == "onnx":
        from onnx.reference import ReferenceEvaluator

        model = ReferenceEvaluator(model)

        def _run_code(output_names, inputs_feed):
            return model.run(output_names, inputs_feed)

        return _run_code
    elif backend == "onnxruntime":
        import onnxruntime

        with TemporaryDirectory() as tmpdir:
            onnx.save_model(model, f"{tmpdir}/model.onnx")
            sess = onnxruntime.InferenceSession(f"{tmpdir}/model.onnx")

        def _run_code(output_names, inputs_feed):
            return sess.run(output_names, inputs_feed)

        return _run_code
    elif backend == "openvino":
        import openvino

        with TemporaryDirectory() as tmpdir:
            onnx.save_model(model, f"{tmpdir}/model.onnx")
            model = openvino.compile_model(f"{tmpdir}/model.onnx")

        def _run_code(output_names, inputs_feed):
            outputs = model(inputs_feed)
            return [outputs[name] for name in output_names]

        return _run_code


def check_accuracy(
    model1: str | onnx.ModelProto,
    model2: str | onnx.ModelProto,
    input_maps: Dict[str, np.ndarray] = None,
    backend: Literal["onnx", "onnxruntime", "openvino"] = "onnx",
) -> Dict[str, float]:
    """
    Check the accuracy of two ONNX models.

    Args:
        model1 (onnx.ModelProto): The first ONNX model to be compared.
        model2 (onnx.ModelProto): The second ONNX model to be compared.
        input_maps (Dict[str, numpy.ndarray], optional): The input data to be used for
            the comparison. If not provided, the model will be run with random input
            data.
        backend (Literal["onnx", "onnxruntime", "openvino"], optional): The backend
            to be used for the comparison. Defaults to "onnx".

    Returns:
        Dict[str, float]: A dictionary containing the accuracy metrics.
    """

    if not isinstance(model1, onnx.ModelProto):
        model1 = onnx.load_model(model1)
    if not isinstance(model2, onnx.ModelProto):
        model2 = onnx.load_model(model2)
    graph1 = OnnxGraph(model1)
    graph2 = OnnxGraph(model2)

    if input_maps is None:
        input_maps = {}
        for input_name in graph1.inputs:
            assert input_name in graph2.inputs
            shape, etype = graph1.tensor_info(input_name)
            dtype = onnx.mapping.TENSOR_TYPE_TO_NP_TYPE[etype]
            input_maps[input_name] = np.random.rand(*shape).astype(dtype)
    output_maps = graph1.outputs
    for output_name in graph2.outputs:
        assert output_name in output_maps

    runner1 = _get_eval_backend(backend, model1)
    runner2 = _get_eval_backend(backend, model2)
    results1 = runner1(list(output_maps), input_maps)
    results2 = runner2(list(output_maps), input_maps)

    error_maps = {}
    for name, x, y in zip(output_maps, results1, results2):
        abs_error = np.abs(x - y)
        rel_error = np.abs(x - y) / np.abs(x)
        error_maps[name] = {
            "ABS": abs_error.mean(),
            "REL": rel_error[np.abs(x) > 1e-8].mean(),
        }
    return error_maps
