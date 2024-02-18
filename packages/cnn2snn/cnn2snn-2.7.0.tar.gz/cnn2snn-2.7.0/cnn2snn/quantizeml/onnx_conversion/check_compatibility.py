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
__all__ = ["check_weight_types"]

import numpy as np


def check_weight_types(converter, weight_names, expect_types):
    """Check that weights have the expected type.

    Args:
        converter (OnnxConverter): the converter.
        weight_names (list of str): list of weight names to check.
        expect_types (list of str): list of expected weight types.

    Raises:
        RuntimeError: if a weight does not exist.
        ValueError: if a weight does not have the expected type.
    """
    assert len(weight_names) == len(expect_types), "Expect to have same lenght of elements."

    weights = converter.weights
    for w_name, e_type in zip(weight_names, expect_types):
        if w_name not in weight_names:
            raise RuntimeError(f"{converter.name} was expected to have '{w_name}' weight.")
        w_dtype = weights[w_name].dtype
        if w_dtype != np.dtype(e_type):
            raise ValueError(f"{w_name} in {converter.name} must be {e_type} type, not {w_dtype}.")


def check_attributes(converter, attr_names):
    """Check that attributes were loaded into converter.

    Args:
        converter (OnnxConverter): the converter.
        weight_names (list of str): list of attribute names to check.

    Raises:
        RuntimeError: if an attribute does not exist.
    """
    for expect_attr in attr_names:
        if not hasattr(converter, expect_attr):
            raise RuntimeError(f"{converter.name} expect to have '{expect_attr}' attribute.")


def check_if_squared(value, name_val=None):
    """Check if input value is square.

    Args:
        value (object): the value to check.
        name_val (str, optional): name of the value. Defaults to None.

    Raises:
        ValueError: if value is not square.
    """
    assert hasattr(value, "__iter__")
    if name_val is None:
        name_val = str(value)
    if value[0] != value[1]:
        raise ValueError(f"{name_val} is expected to be square.")
