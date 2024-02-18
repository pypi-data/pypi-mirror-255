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
__all__ = ["Dense1DOnnxConverter"]

import numpy as np

import akida

from .base_converter import OnnxConverter
from .register import register_onnx_converter_target
from .weights import set_weight_variables
from .activation import set_activation_variables
from .scale_out import set_output_scale_variables
from .check_compatibility import check_weight_types


@register_onnx_converter_target("QuantizedDense1D")
class Dense1DOnnxConverter(OnnxConverter):
    """Convert QuantizedDense1D type node into akida.Dense1D.

    Args:
        node (NodeProto): the node to convert.
        model (ModelProto): the model that the node is.
    """

    def load_attributes(self, node):
        # Some attributes should infer from node.op_type
        n_op = node.op_type
        self.is_flatten = "Flatten" in n_op
        self.activation = "ReLU" in n_op
        self.use_bias = "Biased" in n_op
        self.out_scaled = "Scaled" in n_op
        return super().load_attributes(node)

    def _additional_checks(self):
        # Expect weights/attributes
        check_weight_types(converter=self, weight_names=["W"], expect_types=["int8"])
        if self.use_bias:
            check_weight_types(self, ["bias"], ["int32"])
        if "max_value" in self.weights:
            check_weight_types(self, ["max_value"], ["int32"])
        if self.out_scaled:
            check_weight_types(self, ["Scale", "Shift"], ["uint8", "float32"])

    def _parse_akida_layer(self):
        # Parse common information
        layer_params = {
            "name": self.name,
            "units": self.weights["W"].shape[0],
            "output_bits": 8 if self.out_scaled else 32,
            "activation": self.activation,
        }
        return akida.Dense1D(**layer_params)

    def _set_akida_variables(self, ak_layer):
        assert isinstance(ak_layer, akida.Dense1D)

        # Get kernels
        kernels = self.weights["W"]
        if self.is_flatten:
            # Akida and ONNX flatten operations are not identical.
            # We need to reshape weights to compensate.
            # Note: original input_shape is (c, x, y), but property return akida shape
            x, y, c = self.input_shape
            # First, unroll flattened inputs
            kernels = np.reshape(kernels, (-1, c, x, y))
            # Second, transpose to match akida ordering
            kernels = np.transpose(kernels, (2, 3, 1, 0))
            # Finally, flatten again
            kernels = np.reshape(kernels, (x * y * c, -1))
        else:
            # Transpose weights to match akida ordering (channel at last dimension)
            kernels = np.transpose(kernels)

        # Get bias
        bias = self.weights.get("bias", None)
        set_weight_variables(ak_layer, [kernels], bias)

        # Activation
        if self.activation:
            set_activation_variables(ak_layer, self.weights.get("max_value", None))

        # Scale out
        if self.out_scaled:
            set_output_scale_variables(ak_layer, self.weights["Scale"], self.weights["Shift"])
