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

import logging
import threading
from collections.abc import Iterator
from typing import cast

from flipper.contrib.interface import AbstractFeatureFlagStore, FlagDoesNotExistError
from flipper.contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from flipper.contrib.util.date import now

logger = logging.getLogger(__name__)


class ConsulFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, consul, base_key="features") -> None:  # noqa: ANN001
        self._cache = {}
        self._consul = consul
        self.base_key = base_key

        self._start()

    def _start(self) -> None:
        logger.debug("Spawning a thread to track changes in consul")

        self._thread = threading.Thread(target=self._watch)
        self._thread.daemon = True
        self._thread.start()

    def _watch(self) -> None:
        index = None
        while True:
            index, data = self._consul.kv.get(self.base_key, recurse=True)
            self._parse_data(data)

    def _parse_data(self, data: tuple[dict]) -> None:
        if data is None:
            return
        for item in data:
            serialized = item["Value"]

            if serialized is None:
                continue

            deserialized = FeatureFlagStoreItem.deserialize(serialized)
            self._set_item_in_cache(item["Key"], deserialized)

    def _set_item_in_cache(self, key: str, item: FeatureFlagStoreItem) -> None:
        self._cache[key] = item

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

    def _save(self, item: FeatureFlagStoreItem) -> FeatureFlagStoreItem:
        self._consul.kv.put(self._make_key(item.feature_name), item.serialize())

        self._set_item_in_cache(item.feature_name, item)

        return item

    def get(self, feature_name: str) -> FeatureFlagStoreItem | None:
        return self._cache.get(self._make_key(feature_name))

    def _make_key(self, feature_name: str) -> str:
        return f"{self.base_key}/{feature_name}"

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
        self._consul.kv.delete(self._make_key(feature_name))

    def list(
        self,
        limit: int | None = None,
        offset: int = 0,
    ) -> Iterator[FeatureFlagStoreItem]:
        feature_names = sorted(self._cache.keys())[offset:]

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
