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
__all__ = ["Depthwise2DOnnxConverter"]

import akida

from .base_converter import OnnxConverter
from .check_compatibility import check_attributes
from .register import register_onnx_converter_target
from .conv_commons import set_convolutional_variables, check_convolution_compatibility
from .padding import get_akida_padding


@register_onnx_converter_target("QuantizedDepthwise2D")
class Depthwise2DOnnxConverter(OnnxConverter):
    """Convert QuantizedDepthwise2D type node into an akida.DepthwiseConv2D.

    Args:
        node (NodeProto): the node to convert.
        model (ModelProto): the model that the node is.
    """

    def load_attributes(self, node):
        # Load default attributes
        super().load_attributes(node)

        # Some attributes should infer from node.op_type
        n_op = node.op_type
        self.activation = "ReLU" in n_op
        self.pool_type = akida.PoolType.NoPooling
        self.use_bias = "Biased" in n_op

        # Padding type is inferred from pads attribute
        self.pads = self.weights["pads"].tolist()
        self.padding = akida.Padding.Same if any(self.pads) else akida.Padding.Valid

    def _additional_checks(self):
        # Convolutional checks
        check_convolution_compatibility(self)

        # Group constrains
        check_attributes(self, ["groups"])
        filters = self.weights["W"].shape[0]
        channels = self.weights["W"].shape[1]
        if self.groups != filters or channels != 1:
            raise ValueError(f"The number of groups in the node {self.name} ({self.groups}) "
                             f"does not match the number of filters ({filters}).")

    def _parse_akida_layer(self):
        # Parse information
        layer_params = {
            "name": self.name,
            "activation": self.activation,
            "output_bits": 8,
            "kernel_size": self.weights["W"].shape[-1],
            "padding": get_akida_padding(self),
            "pool_type": self.pool_type,
            "kernel_stride": self.strides[0],
        }
        return akida.DepthwiseConv2D(**layer_params)

    def _set_akida_variables(self, ak_layer):
        set_convolutional_variables(self, ak_layer, is_depthwise=True)
