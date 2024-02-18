"""
Copyright Wenyi Tang 2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""
# pylint: disable=missing-function-docstring

import random

import onnx

from onnx2onnx import OnnxGraph, PassManager
from onnx2onnx.passes import PASSES


@PASSES.register(name="function_in_test")
def fake_pass_function(graph, args_x, args_y):
    assert args_x == args_y
    return graph


@PASSES.register(name="class_in_test")
class FakeClassPass:
    """Fake Pass"""

    def rewrite(self, graph, args_x=0, args_y=2):
        assert args_x == args_y

    def __call__(self, graph, *args, **kwargs):
        self.rewrite(graph, *args, **kwargs)
        return graph


def _empty_model():
    return onnx.helper.make_model(
        graph=onnx.helper.make_graph([], "empty", [], []),
    )


def test_pass_manager_default():
    graph = OnnxGraph(_empty_model())
    pass_manager = PassManager()
    pass_manager.optimize(graph)


def test_pass_manager_include_and_exclude():
    passes = list(iter(PASSES))
    random.shuffle(passes)
    cut_pos = len(passes) // 2
    pass_manager = PassManager(passes[:cut_pos], passes[cut_pos:])
    graph = OnnxGraph(_empty_model())
    pass_manager.optimize(graph)


def test_pass_manager_with_configs():
    pass_manager = PassManager(
        ["function_in_test", "class_in_test", "class_in_test", "function_in_test"],
        configs={
            "function_in_test": dict(args_x=1, args_y=1),
            "class_in_test:0": dict(args_x=1, args_y=1),
            "class_in_test:1": dict(args_x="2", args_y="2"),
        },
    )
    graph = OnnxGraph(_empty_model())
    pass_manager.optimize(graph, strict=True)
