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

import hashlib
import json
from typing import Any

from .percentage import PercentageFactory
from .percentage_bucketer import PercentageBucketer


class ConsistentHashPercentageBucketer(PercentageBucketer):
    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        self._key_whitelist = set(kwargs.pop("key_whitelist", []))
        super().__init__(**kwargs)

    @classmethod
    def get_type(cls) -> str:
        return "ConsistentHashPercentageBucketer"

    def check(self, randomizer=None, **checks) -> bool:  # noqa: ANN001, ANN003, ARG002
        if self._percentage == 0:
            return False

        serialized = self._serialize_checks(checks)

        hashed = hashlib.sha1(serialized)  # nosec  # noqa: S324
        score = self._score_hash(hashed)

        return score <= self._percentage

    def _serialize_checks(self, checks: dict[str, Any]) -> bytes:
        filtered_checks = self._filter_checks(checks)
        sorted_checks = self._sort_checks(filtered_checks)
        return json.dumps(sorted_checks).encode("utf-8")

    def _filter_checks(self, checks: dict[str, Any]) -> dict[str, Any]:
        return {k: v for (k, v) in checks.items() if self._should_check_key(k)}

    def _should_check_key(self, key: str) -> bool:
        if len(self._key_whitelist) == 0:
            return True
        return key in self._key_whitelist

    def _sort_checks(self, checks: dict[str, Any]) -> list[tuple[str, Any]]:
        return sorted(checks.items(), key=lambda x: x[0])

    def _score_hash(self, hashed) -> float:  # noqa: ANN001
        return (int(hashed.hexdigest(), 16) % 100) / 100

    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            "type": ConsistentHashPercentageBucketer.get_type(),
            "key_whitelist": list(self._key_whitelist),
        }

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> "ConsistentHashPercentageBucketer":
        key_whitelist = fields.get("key_whitelist", [])
        percentage_fields = fields.get("percentage")
        percentage = None
        if percentage_fields is not None:
            percentage = PercentageFactory.create(percentage_fields)
        return cls(key_whitelist=key_whitelist, percentage=percentage)
