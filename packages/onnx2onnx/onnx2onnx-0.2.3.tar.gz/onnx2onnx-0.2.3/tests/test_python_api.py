"""
Copyright Wenyi Tang 2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""
# pylint: disable=missing-function-docstring

import onnx
import pooch

from onnx2onnx import convert


def test_convert_api(classification_models):
    model_url, hash_value = classification_models
    model_file = pooch.retrieve(model_url, hash_value)
    model = onnx.load_model(model_file)
    convert(model)
    convert(model_file, strict=True)
