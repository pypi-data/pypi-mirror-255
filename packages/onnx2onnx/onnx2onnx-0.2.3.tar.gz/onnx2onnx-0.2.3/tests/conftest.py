"""
Copyright Wenyi Tang 2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

import pytest


def classification_models():
    """A list of testing classification models from onnx hub."""
    header = "https://github.com/onnx/models/raw/main/validated/vision/classification/"
    models = [
        ("mobilenet/model/mobilenetv2-10.onnx", None),
        ("resnet/model/resnet18-v2-7.onnx", None),
        ("resnet/model/resnet50-v1-12-qdq.onnx", None),
    ]
    return [(header + i + "?download=", hash_value) for (i, hash_value) in models]


def pytest_generate_tests(metafunc: pytest.Metafunc):
    """Generate parametrized arguments to all tests with arg 'model'.
    `model` is acquired from model_zoo.
    """

    if "classification_models" in metafunc.fixturenames:
        metafunc.parametrize("classification_models", classification_models())
