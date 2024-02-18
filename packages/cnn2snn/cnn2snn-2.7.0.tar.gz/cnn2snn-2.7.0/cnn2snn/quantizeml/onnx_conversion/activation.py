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
__all__ = ["set_activation_variables"]

from .weights import broadcast_and_set_variable, to_value_shift


def set_activation_variables(ak_layer, max_value=None):
    """Set max value into akida variables.

    Args:
        ak_layer (akida.Layer): the akida layer to set variables.
        max_value (int, optional): the maximal value to set. Defaults to None.
    """
    if max_value is not None:
        # Max value is converted to a fixed point: unsigned 8bit << unsigned 8bit
        max_value, max_value_shift = to_value_shift(max_value, signed=False)
    else:
        # When max_value is not provided, resolve threshold as maximal SHIFTED int32 value
        max_value, max_value_shift = 1, 30
    broadcast_and_set_variable(ak_layer.variables, "max_value", max_value)
    broadcast_and_set_variable(ak_layer.variables, "max_value_shift", max_value_shift)
