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
"""Functions to convert QuantizedDepthwiseConv2D to Akida.
"""
import numpy as np

from quantizeml.layers import (QuantizedDepthwiseConv2D, QuantizedReLU,
                               QuantizedMaxPool2D, WeightQuantizer, AlignedWeightQuantizer)
from akida import DepthwiseConv2D

from ..akida_versions import AkidaVersion
from .activations import set_relu_variables
from .weights import broadcast_and_set_variable
from .outputs import set_output_v2_variables, parse_output_bits, parse_post_op_buffer_bits
from .padding import check_conv_and_max_pool_compatibility
from .pooling import max_pool_param_checks
from .blocks import get_block_out_quantizer
from .conv_common import get_layer_by_type, parse_depthwise_conv_block
from .block_converter import BlockConverter, register_conversion_patterns

__all__ = ["DepthwiseConvBlockConverter"]

_PATTERNS = [(QuantizedDepthwiseConv2D,), (QuantizedDepthwiseConv2D, QuantizedReLU),
             (QuantizedDepthwiseConv2D, QuantizedMaxPool2D, QuantizedReLU)]


def _set_depthwise_conv2d_block_variables(layer_ak, block):
    """Computes and sets the variables for an Akida v2 DepthwiseConv2D layer.

    This function converts the variables of a Keras layers block and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        layer_ak (:obj:`akida.Layer`): the targeted akida layer.
        block (list(:obj:`tf.keras.Layer`)): the depthwise convolutional block layers.
    """
    depth_conv = block[0]
    assert isinstance(depth_conv.weight_quantizer, WeightQuantizer)
    if depth_conv.use_bias:
        assert isinstance(depth_conv.bias_quantizer, AlignedWeightQuantizer)

    # Get the weights
    weights = depth_conv.weight_quantizer.qweights.value.fp.values.numpy()
    # Flip W and H dimensions for depthwise
    weights = np.flip(weights, axis=[0, 1])

    layer_ak.variables["weights"] = weights.astype(np.int8)

    # Set the bias (if there is one)
    if depth_conv.use_bias:
        bias_quantizer = depth_conv.bias_quantizer
        bias = bias_quantizer.qweights.value.values.numpy().astype(np.int32)
        bias_shift = bias_quantizer.shift.value.numpy().astype(np.uint8)

        # Unshift the bias and store it
        layer_ak.variables["bias"] = (bias >> bias_shift).astype(np.int8)
        # Also store the bias shift
        broadcast_and_set_variable(layer_ak.variables, "bias_shift", bias_shift)

    # Set input shift
    input_shift = getattr(depth_conv, 'input_shift', None)
    if input_shift is not None:
        broadcast_and_set_variable(layer_ak.variables, "input_shift",
                                   depth_conv.input_shift.value.numpy().astype(np.uint8))

    # Check if we have ReLU
    relu_layer = get_layer_by_type(block, QuantizedReLU)
    if relu_layer:
        set_relu_variables(layer_ak, relu_layer)

    # Get the layer block output_quantizer
    out_quantizer = get_block_out_quantizer(block)
    # Set optional output_quantizer variables
    if out_quantizer:
        set_output_v2_variables(layer_ak, out_quantizer)


def convert_depthwise_conv_block(model_ak, block):
    """Converts a depthwise convolutional block into an akida v2 DepthwiseConv2D layer.

    The expected sequence is:

    - QuantizedDepthwiseConv2D,
    - QuantizedMaxPool2D (optional),
    - QuantizedReLU (optional).

    Args:
        model_ak (:obj:`akida.Model`): the target Akida model.
        block (list(:obj:`tf.keras.Layer`)): the block layers.

    Returns:
        bool: Returns True for a successful conversion.

    """

    # Evaluate the depthwise convolutional layer parameters
    conv_params = parse_depthwise_conv_block(block)

    # add output quantizer bitwidth parameter
    parse_output_bits(block, conv_params)
    # parse the block post op buffer bits
    parse_post_op_buffer_bits(block, conv_params)

    # Create Akida layer
    dw_conv_ak = DepthwiseConv2D(**conv_params)
    # Add layer to the model to build its internal variables
    model_ak.add(dw_conv_ak)

    # Set base variables
    _set_depthwise_conv2d_block_variables(dw_conv_ak, block)

    return True


class DepthwiseConvBlockConverter(BlockConverter):
    """Main class that should be used to check if the depthwise conv block is compatible to an
    Akida v2 conversion and provides a method to convert it in an equivalent Akida DepthwiseConv2D
    layer.

    Args:
        block (list): list of quantizeml quantized layers.
    """

    def __init__(self, block):
        super().__init__(block)
        self._depthwise_conv_additional_checks()

    def _depthwise_conv_additional_checks(self):
        depth_conv = self._block[0]
        # Make sure the DepthwiseConv2D kernel size and stride params are square
        assert depth_conv.kernel_size[0] == depth_conv.kernel_size[1], (
            "DepthwiseConv2D kernel should be square")
        assert depth_conv.strides[0] == depth_conv.strides[1], (
            "DepthwiseConv2D strides should be the same on both dimensions")

        # The only weight bitwidth supported is [4, 8]
        weight_bits = depth_conv.weight_quantizer.bitwidth
        assert weight_bits in [4, 8], ("DepthwiseConv2D layer can only handle weights"
                                       f" with 4 or 8 bits. Received: {weight_bits}.")

        # Check optional pooling compatibility
        pool_layer = get_layer_by_type(self._block, QuantizedMaxPool2D)
        if pool_layer:
            check_conv_and_max_pool_compatibility(depth_conv, pool_layer)
            max_pool_param_checks(pool_layer)

    def convert(self, model_ak):
        return convert_depthwise_conv_block(model_ak, self._block)


# Register the valid depthwise conv block pattern for Akida v2
register_conversion_patterns(AkidaVersion.v2, _PATTERNS, DepthwiseConvBlockConverter)
