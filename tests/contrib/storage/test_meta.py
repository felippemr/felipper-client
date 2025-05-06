import unittest
from datetime import datetime
from uuid import uuid4

from flipper import Condition
from flipper.bucketing import Percentage, PercentageBucketer
from flipper.contrib.storage import FeatureFlagStoreMeta


class BaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.now = int(datetime.now().timestamp())  # noqa: DTZ005

    def txt(self):
        return uuid4().hex


class TestToDict(BaseTest):
    def test_includes_correct_created_date(self) -> None:
        meta = FeatureFlagStoreMeta(self.now, {})
        assert self.now == meta.to_dict()["created_date"]

    def test_includes_correct_client_data(self) -> None:
        client_data = {"foo": 99, "bar": "ajds"}
        meta = FeatureFlagStoreMeta(self.now, client_data)
        assert client_data == meta.to_dict()["client_data"]

    def test_includes_correct_conditions(self) -> None:
        conditions = [Condition(foo=1), Condition(bar="baz")]
        meta = FeatureFlagStoreMeta(self.now, conditions=conditions)
        serialized_conditions = [c.to_dict() for c in conditions]
        assert serialized_conditions == meta.to_dict()["conditions"]

    def test_includes_currect_bucketer(self) -> None:
        bucketer = PercentageBucketer(percentage=Percentage(0.3))
        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer)
        assert bucketer.to_dict() == meta.to_dict()["bucketer"]


class TestFromDict(BaseTest):
    def test_will_not_crash_if_client_data_not_present(self) -> None:
        json = {"created_date": self.now, "conditions": []}
        meta = FeatureFlagStoreMeta.from_dict(json)
        assert meta.client_data == {}

    def test_will_not_crash_if_conditions_not_present(self) -> None:
        json = {"created_date": self.now, "client_data": {}}
        meta = FeatureFlagStoreMeta.from_dict(json)
        assert meta.conditions == []

    def test_can_create_with_bucketer(self) -> None:
        bucketer = PercentageBucketer(percentage=Percentage(0.3))
        json = {"created_date": self.now, "bucketer": bucketer.to_dict()}
        meta = FeatureFlagStoreMeta.from_dict(json)
        assert bucketer.to_dict() == meta.bucketer.to_dict()


class TestUpdate(BaseTest):
    def test_updates_created_date(self) -> None:
        later = self.now + 1
        meta = FeatureFlagStoreMeta(self.now, {})
        meta.update(created_date=later)
        assert later == meta.created_date

    def test_updates_client_data(self) -> None:
        updated_client_data = {self.txt(): self.txt()}
        meta = FeatureFlagStoreMeta(self.now, {})
        meta.update(client_data=updated_client_data)
        assert updated_client_data == meta.client_data

    def test_merges_old_and_new_client_data(self) -> None:
        original_client_data = {"a": 1, "b": 2}
        updated_client_data = {"b": 3}
        meta = FeatureFlagStoreMeta(self.now, original_client_data)
        meta.update(client_data=updated_client_data)
        assert {"a": original_client_data["a"], "b": updated_client_data["b"]} == meta.client_data

    def test_updating_created_date_does_not_affect_client_data(self) -> None:
        later = self.now + 1
        meta = FeatureFlagStoreMeta(self.now, {})
        meta.update(created_date=later)
        assert meta.client_data == {}

    def test_updating_client_data_does_not_affect_created_date(self) -> None:
        updated_client_data = {self.txt(): self.txt()}
        meta = FeatureFlagStoreMeta(self.now, {})
        meta.update(client_data=updated_client_data)
        assert self.now == meta.created_date

    def test_sets_conditions(self) -> None:
        conditions = [Condition(foo=1)]
        meta = FeatureFlagStoreMeta(self.now)
        meta.update(conditions=conditions)
        assert conditions == meta.conditions

    def test_replaces_conditions_entirely(self) -> None:
        conditions = [Condition(foo=1)]
        meta = FeatureFlagStoreMeta(self.now)
        meta.update(conditions=conditions)
        meta.update(conditions=conditions)
        assert conditions == meta.conditions

    def test_sets_bucketer(self) -> None:
        percentage_value = 0.1
        bucketer = PercentageBucketer(percentage=Percentage(percentage_value))
        meta = FeatureFlagStoreMeta(self.now)
        meta.update(bucketer=bucketer)
        assert percentage_value == meta.bucketer.percentage
