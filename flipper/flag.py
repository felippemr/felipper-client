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
from collections.abc import Iterable
from typing import TYPE_CHECKING

from .bucketing.base import AbstractBucketer
from .conditions import Condition

if TYPE_CHECKING:
    from .client import FeatureFlagClient


class FeatureFlag:
    def __init__(self, feature_name: str, client: "FeatureFlagClient") -> None:
        self.name = feature_name
        self._client = client

    def is_enabled(self, default=False, **conditions) -> bool:  # noqa: ANN001, ANN003
        return self._client.is_enabled(self.name, default=default, **conditions)

    def exists(self):  # noqa: ANN201
        return self._client.exists(self.name)

    def enable(self) -> None:
        self._client.enable(self.name)

    def disable(self) -> None:
        self._client.disable(self.name)

    def destroy(self) -> None:
        self._client.destroy(self.name)

    def add_condition(self, condition: Condition) -> None:
        self._client.add_condition(self.name, condition)

    def set_client_data(self, client_data: dict) -> None:
        self._client.set_client_data(self.name, client_data)

    def get_client_data(self) -> dict:
        return self.get_meta()["client_data"]

    def get_meta(self) -> dict:
        return self._client.get_meta(self.name)

    def set_bucketer(self, bucketer: AbstractBucketer) -> None:
        self._client.set_bucketer(self.name, bucketer)

    def set_conditions(self, conditions: Iterable[Condition]) -> None:
        self._client.set_conditions(self.name, conditions)
