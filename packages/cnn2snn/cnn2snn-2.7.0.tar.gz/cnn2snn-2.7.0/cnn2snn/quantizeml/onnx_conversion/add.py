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
__all__ = ["AddOnnxConverter"]

import numpy as np

import akida

from .base_converter import OnnxConverter
from .register import register_onnx_converter_target
from .weights import broadcast_and_set_variable
from .check_compatibility import check_weight_types
from .scale_out import set_output_scale_variables


@register_onnx_converter_target("QuantizedAdd")
class AddOnnxConverter(OnnxConverter):
    """Convert QuantizedAdd type node into akida.Add.

    Args:
        node (NodeProto): the node to convert.
        model (ModelProto): the model containing the node.
    """

    def load_attributes(self, node):
        # Some attributes should infer from node.op_type
        n_op = node.op_type
        self.out_scaled = "Scaled" in n_op
        return super().load_attributes(node)

    def _additional_checks(self):
        # Expect weights/attributes
        check_weight_types(self, ["Xs", "Ys"], ["int32", "int32"])
        if self.out_scaled:
            check_weight_types(self, ["Shift"], ["float32"])

        # Check input shifts are always positive
        if np.any(self.weights["Xs"] < 0) or np.any(self.weights["Ys"] < 0):
            raise RuntimeError(f"Impossible to convert {self.name} into akida. "
                               "Input shifts should be positive.")

        # Reject Add(X, X) (inputs are the same tensor)
        if self._node.input[0] == self._node.input[1]:
            raise RuntimeError(f"Impossible to convert {self.name} into akida. "
                               "Inputs must come from different tensors.")

    def _parse_akida_layer(self):
        return akida.Add(output_bits=8 if self.out_scaled else 32, name=self.name)

    def _set_akida_variables(self, ak_layer):
        def to_power(x):
            return np.log2(x)

        assert isinstance(ak_layer, akida.Add)

        # Input shifts
        ak_vars = ak_layer.variables
        broadcast_and_set_variable(ak_vars, "a_shift", to_power(self.weights["Xs"]))
        broadcast_and_set_variable(ak_vars, "b_shift", to_power(self.weights["Ys"]))

        # Shift out
        if self.out_scaled:
            set_output_scale_variables(ak_layer, shift=self.weights["Shift"])
