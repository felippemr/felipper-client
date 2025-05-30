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

from typing import Any

from .base import AbstractPercentage


class Percentage(AbstractPercentage):
    def __init__(self, value: float | None = 1.0) -> None:
        self._value = value

    @classmethod
    def get_type(cls) -> str:
        return "Percentage"

    @property
    def value(self):  # noqa: ANN201
        return self._value

    def to_dict(self) -> dict[str, Any]:
        return {**super().to_dict(), "value": self._value}

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> "Percentage":
        return cls(value=fields.get("value"))
