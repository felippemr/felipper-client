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
from .linear_ramp_percentage import LinearRampPercentage
from .percentage import Percentage


class PercentageFactory:
    PERCENTAGE_MAP = {  # noqa: RUF012
        LinearRampPercentage.get_type(): LinearRampPercentage,
        Percentage.get_type(): Percentage,
    }

    class InvalidPercentageTypeError(Exception):
        pass

    @classmethod
    def create(cls, fields: dict[str, Any]) -> AbstractPercentage:
        try:
            return cls.PERCENTAGE_MAP[fields["type"]].from_dict(fields)  # type: ignore  # noqa: PGH003
        except KeyError:
            msg = "Percentage type not supported: {}".format(fields["type"])
            raise cls.InvalidPercentageTypeError(  # noqa: B904
                msg,
            )
