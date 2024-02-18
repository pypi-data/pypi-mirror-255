#!/usr/bin/env python
# ******************************************************************************
# Copyright 2023 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
import numpy as np

import akida

from .base_converter import OnnxConverter
from .check_compatibility import check_weight_types, check_attributes, check_if_squared
from .weights import broadcast_and_set_variable, set_weight_variables
from .activation import set_activation_variables
from .scale_out import set_output_scale_variables


def set_convolutional_variables(converter, ak_layer, is_depthwise=False):
    """Transfer converter weights to ak_layer.

    Args:
        converter (OnnxConverter): the converter to extract weights.
        ak_layer (akida.Layer): the target Akida model.
        is_depthwise (bool, optional): whether to transpose kernel on depthwise. Defaults to False.
    """
    assert isinstance(converter, OnnxConverter)

    # Set padding value (in case of InputConv2D)
    if ak_layer.parameters.layer_type == akida.LayerType.InputConv2D:
        ak_variables = ak_layer.variables
        broadcast_and_set_variable(ak_variables, "padding_value", converter.weights["x_pad_value"])

    # Get kernels and transpose them (FCKxKy -> KxKyCF)
    kernel = converter.weights["W"].transpose((2, 3, 1, 0))
    if not converter.is_input_layer:
        # Kernel need to be flipped
        kernel = np.flip(kernel, axis=(0, 1))

    # Akida interprets depthwise kernel with respect to ONNX in a different way:
    # * Akida: Number of filters is 1, with C input channels.
    # * Onnx: Channels is 1 (C / groups) and filters is the desired output F.
    # That is why we need to transpose both dimensions
    if is_depthwise:
        kernel = kernel.transpose((0, 1, 3, 2))

    bias = converter.weights.get("bias", None)
    set_weight_variables(ak_layer, [kernel], bias)

    # Activation
    if converter.activation:
        set_activation_variables(ak_layer, converter.weights.get("max_value", None))

    # Scale out
    set_output_scale_variables(ak_layer, converter.weights["Scale"], converter.weights["Shift"])


def check_convolution_compatibility(converter, use_pad_value=False):
    """Check convolution compatibility with Akida.

    Args:
        converter (OnnxConverter): the converter to check.
        use_pad_value (bool, optional): extend checks to padding value. Defaults to False.
    """
    # Weights constrains
    check_weight_types(converter,
                       weight_names=["W", "Scale", "Shift", "pads"],
                       expect_types=["int8", "uint8", "float32", "int64"])

    # Zero point constrains
    if use_pad_value:
        check_weight_types(converter, ["x_pad_value"], expect_types=["uint8"])
        channel = converter.weights["W"].shape[1]
        pad_size = converter.weights["x_pad_value"].size
        if pad_size != channel:
            raise ValueError("Padding value size must be equal to the number of channel.")
        if not converter.is_input_layer and np.any(converter.weights["x_pad_value"]):
            raise ValueError("Padding value must be zero.")

    # Bias constrains
    if converter.use_bias:
        check_weight_types(converter=converter, weight_names=["bias"], expect_types=["int32"])

    # Max value constrains
    if "max_value" in converter.weights:
        check_weight_types(converter=converter, weight_names=["max_value"], expect_types=["int32"])

    # Attributes checks
    check_attributes(converter, ["strides"])
    if converter.pool_type == akida.PoolType.Max:
        check_attributes(converter, ["pool_size", "pool_strides", "pool_pads"])

    # Other checks
    kernel_shapes = converter.weights["W"].shape[-2:]
    check_if_squared(kernel_shapes, name_val="kernels")
    check_if_squared(converter.strides, name_val="strides")
    if converter.pool_type == akida.PoolType.Max:
        check_if_squared(converter.pool_size, name_val="pool sizes")
        check_if_squared(converter.pool_strides, name_val="pool strides")
