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

from collections.abc import Callable, Iterator
from threading import Thread

from flipper.contrib.interface import AbstractFeatureFlagStore
from flipper.contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta

StoreType = AbstractFeatureFlagStore


class ReplicatedFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(
        self,
        primary: StoreType,
        *replicas: StoreType,
        replication_timeout=1,  # noqa: ANN001
    ) -> None:
        self._primary = primary
        self._replicas = replicas
        self._stores = [primary, *list(replicas)]
        self._replication_timeout = replication_timeout

    def create(
        self,
        feature_name: str,
        is_enabled: bool = False,
        client_data: dict | None = None,
        asynch: bool | None = True,
    ) -> None:
        def perform_create_on_store(store, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
            store.create(*args, **kwargs)

        args = (feature_name,)
        kwargs = {"is_enabled": is_enabled, "client_data": client_data}

        perform_create_on_store(self._primary, *args, **kwargs)

        self._replicate(
            perform_create_on_store,
            asynch=asynch,
            args=args,
            kwargs=kwargs,
        )

    def _replicate(
        self,
        fn: Callable,
        asynch: bool | None = True,
        args: tuple = (),
        kwargs: dict | None = None,
    ) -> None:
        if kwargs is None:
            kwargs = {}
        threads = []

        for replica in self._replicas:
            threads.append(self._start_thread(fn, args=(replica, *args), kwargs=kwargs))  # noqa: PERF401

        if asynch is False:
            return

        for thread in threads:
            thread.join(timeout=self._replication_timeout)

    def _start_thread(
        self,
        fn: Callable,
        args: tuple = (),
        kwargs: dict | None = None,
    ) -> Thread:
        if kwargs is None:
            kwargs = {}
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread

    def get(self, *args, **kwargs) -> FeatureFlagStoreItem | None:  # noqa: ANN002, ANN003
        return self._primary.get(*args, **kwargs)

    def set(
        self,
        feature_name: str,
        is_enabled: bool,
        asynch: bool | None = True,
    ) -> None:
        def perform_set_on_store(store, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
            store.set(*args, **kwargs)

        args = (feature_name, is_enabled)

        perform_set_on_store(self._primary, *args)

        self._replicate(perform_set_on_store, asynch=asynch, args=args)

    def delete(self, feature_name: str, asynch: bool | None = True) -> None:
        def perform_delete_on_store(store, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
            store.delete(*args, **kwargs)

        perform_delete_on_store(self._primary, feature_name)

        self._replicate(perform_delete_on_store, asynch=asynch, args=(feature_name,))

    def list(self, *args, **kwargs) -> Iterator[FeatureFlagStoreItem]:  # noqa: ANN002, ANN003
        return self._primary.list(*args, **kwargs)

    def set_meta(
        self,
        feature_name: str,
        meta: FeatureFlagStoreMeta,
        asynch: bool | None = True,
    ) -> None:
        def perform_set_meta_on_store(store, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
            store.set_meta(*args, **kwargs)

        args = (feature_name, meta)

        perform_set_meta_on_store(self._primary, *args)

        self._replicate(perform_set_meta_on_store, asynch=asynch, args=args)
