"""An Open Neural Network Exchange (ONNX) Optimization and Transformation Tool.

Copyright Wenyi Tang 2023-2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

__version__ = "0.2.3"

import os
from copy import deepcopy
from typing import Literal, Sequence

import onnx
from onnx import ModelProto

from .graph import OnnxGraph
from .pass_manager import PassManager


def convert_graph(
    model: str | os.PathLike | ModelProto,
    passes: Sequence[str] = None,
    onnx_format: Literal["protobuf", "textproto", "json", "onnxtxt"] = None,
    strict: bool = False,
    configs: dict = None,
) -> OnnxGraph:
    """Convert an ONNX model to OnnxGraph

    Args:
        model (str | os.PathLike | ModelProto): path to the model or a loaded model.
        passes (Sequence[str], optional): Names of selected passes. Defaults to None.
        onnx_format (str, optional): The serialization format of model file.
        strict (bool, optional): Break if any pass goes wrong. Defaults to False.
        configs (dict, optional): Specify configuration for passes

    Returns:
        OnnxGraph: converted graph
    """
    if isinstance(model, (str, os.PathLike)):
        model = onnx.load_model(model, format=onnx_format)
    else:
        model = deepcopy(model)
    graph = OnnxGraph(model)
    pm = PassManager(passes, configs=configs)
    print(pm)
    graph = pm.optimize(graph, strict=strict)
    return graph


def convert(
    model: str | os.PathLike | ModelProto,
    passes: Sequence[str] = None,
    onnx_format: Literal["protobuf", "textproto", "json", "onnxtxt"] = None,
    strict: bool = False,
    configs: dict = None,
) -> ModelProto:
    """Convert an ONNX model with default or given passes

    Args:
        model (str | os.PathLike | ModelProto): path to the model or a loaded model.
        passes (Sequence[str], optional): Names of selected passes. Defaults to None.
        onnx_format (str, optional): The serialization format of model file.
        strict (bool, optional): Break if any pass goes wrong. Defaults to False.
        configs (dict, optional): Specify configuration for passes
    """

    graph = convert_graph(model, passes, onnx_format, strict, configs)
    return graph.model


__all__ = ["convert", "PassManager"]
