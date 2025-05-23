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

from collections.abc import Iterator
from typing import cast

from flipper.contrib.interface import AbstractFeatureFlagStore, FlagDoesNotExistError
from flipper.contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from flipper.contrib.util.date import now


class MemoryFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self) -> None:
        self._memory = {}

    def create(
        self,
        feature_name: str,
        is_enabled: bool = False,
        client_data: dict | None = None,
    ) -> FeatureFlagStoreItem:
        item = FeatureFlagStoreItem(
            feature_name,
            is_enabled,
            FeatureFlagStoreMeta(now(), client_data),
        )
        return self._save(item)

    def _save(self, item: FeatureFlagStoreItem):  # noqa: ANN202
        self._memory[item.feature_name] = item
        return item

    def get(self, feature_name: str) -> FeatureFlagStoreItem | None:
        return self._memory.get(feature_name)

    def set(self, feature_name: str, is_enabled: bool) -> None:
        existing = self.get(feature_name)

        if existing is None:
            self.create(feature_name, is_enabled)
            return

        item = FeatureFlagStoreItem(
            feature_name,
            is_enabled,
            FeatureFlagStoreMeta.from_dict(existing.meta),
        )
        self._save(item)

    def delete(self, feature_name: str) -> None:
        if feature_name in self._memory:
            del self._memory[feature_name]

    def list(
        self,
        limit: int | None = None,
        offset: int = 0,
    ) -> Iterator[FeatureFlagStoreItem]:
        feature_names = sorted(self._memory.keys())[offset:]

        if limit is not None:
            feature_names = feature_names[:limit]

        for feature_name in feature_names:
            yield cast("FeatureFlagStoreItem", self.get(feature_name))

    def set_meta(self, feature_name: str, meta: FeatureFlagStoreMeta) -> None:
        existing = self.get(feature_name)

        if existing is None:
            msg = f"Feature {feature_name} does not exist"
            raise FlagDoesNotExistError(
                msg,
            )

        item = FeatureFlagStoreItem(feature_name, existing.raw_is_enabled, meta)

        self._save(item)
