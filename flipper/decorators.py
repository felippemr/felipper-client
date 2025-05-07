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

from collections.abc import Callable

from .client import FeatureFlagClient


def is_enabled(  # noqa: ANN201
    flags: FeatureFlagClient,
    feature_name: str,
    redirect: Callable | None = None,
):
    def decorator(fn):  # noqa: ANN001, ANN202
        def wrapper(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            if flags.is_enabled(feature_name):
                return fn(*args, **kwargs)
            if redirect is None:
                return None
            return redirect(*args, **kwargs)

        return wrapper

    return decorator
