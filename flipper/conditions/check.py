# Copyright 2018 eShares, Inc. dba Carta, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import contextlib
from typing import Any

from .operators import Operator
from .operators.interface import AbstractOperator

OPERATOR_DELIMITER = "__"


class Check:
    def __init__(self, variable: str, value: Any, operator: AbstractOperator) -> None:
        self._variable = variable
        self._value = value
        self._operator = operator

    @property
    def variable(self):  # noqa: ANN201
        return self._variable

    @property
    def value(self):  # noqa: ANN201
        return self._value

    @property
    def operator(self):  # noqa: ANN201
        return self._operator

    def check(self, value):  # noqa: ANN001, ANN201
        return self._operator.compare(value, self._value)

    @classmethod
    def factory(cls, check_key: str, check_value: Any):  # noqa: ANN206
        variable, operator = cls._parse_check_key(check_key)
        return cls(variable, check_value, operator)

    @classmethod
    def _parse_check_key(cls, check_key: str) -> tuple[str, AbstractOperator]:
        variable, raw_operator = check_key, None

        with contextlib.suppress(ValueError):
            variable, raw_operator = check_key.split(OPERATOR_DELIMITER)

        return variable, Operator.factory(raw_operator)

    def to_dict(self) -> dict:
        return {
            "variable": self._variable,
            "value": self._value,
            "operator": self._operator.SYMBOL,
        }

    @classmethod
    def from_dict(cls, fields: dict) -> "Check":
        return cls(
            fields["variable"],
            fields["value"],
            Operator.factory(fields["operator"]),
        )

    @classmethod
    def make_check_key(cls, variable: str, operator: str) -> str:
        if operator is None:
            return variable
        return OPERATOR_DELIMITER.join([variable, operator])
