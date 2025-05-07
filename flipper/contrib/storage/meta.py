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


from flipper.bucketing import BucketerFactory, NoOpBucketer
from flipper.bucketing.base import AbstractBucketer
from flipper.conditions import Condition


class FeatureFlagStoreMeta:
    def __init__(
        self,
        created_date: int,
        client_data: dict | None = None,
        conditions: list[Condition] | None = None,
        bucketer: AbstractBucketer | None = None,
    ) -> None:
        self.created_date = created_date
        self.client_data = client_data or {}
        self.conditions = conditions or []
        self.bucketer = bucketer or NoOpBucketer()

    def to_dict(self):  # noqa: ANN201
        return {
            "client_data": self.client_data,
            "created_date": self.created_date,
            "conditions": [condition.to_dict() for condition in self.conditions],
            "bucketer": self.bucketer.to_dict(),
        }

    @classmethod
    def from_dict(cls, fields: dict):  # noqa: ANN206
        kwargs = {
            "client_data": fields.get("client_data", []),
            "conditions": [Condition.from_dict(condition) for condition in fields.get("conditions", [])],
        }

        bucketer_fields = fields.get("bucketer")
        if bucketer_fields is not None:
            kwargs["bucketer"] = BucketerFactory.create(bucketer_fields)

        return cls(fields["created_date"], **kwargs)

    def update(
        self,
        created_date: int | None = None,
        client_data: dict | None = None,
        conditions: list[Condition] | None = None,
        bucketer: AbstractBucketer | None = None,
    ) -> None:
        if created_date is not None:
            self.created_date = created_date
        if client_data is not None:
            self._merge_client_data(client_data)
        if conditions is not None:
            self.conditions = conditions
        if bucketer is not None:
            self.bucketer = bucketer

    def _merge_client_data(self, client_data: dict) -> None:
        self.client_data.update(client_data)
