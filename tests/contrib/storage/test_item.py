import json
import unittest
from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import Condition
from flipper.contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class BaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.now = int(datetime.now().timestamp())  # noqa: DTZ005

    def txt(self):
        return uuid4().hex


class TestToDict(BaseTest):
    def test_includes_correct_feature_name(self) -> None:
        name = self.txt()
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, True, meta)
        assert name == item.to_dict()["feature_name"]

    def test_includes_correct_is_enabled_when_true(self) -> None:
        is_enabled = True
        item = FeatureFlagStoreItem(
            self.txt(),
            is_enabled,
            FeatureFlagStoreMeta(self.now, {}),
        )
        assert is_enabled == item.to_dict()["is_enabled"]

    def test_includes_correct_is_enabled_when_false(self) -> None:
        is_enabled = False
        item = FeatureFlagStoreItem(
            self.txt(),
            is_enabled,
            FeatureFlagStoreMeta(self.now, {}),
        )
        assert is_enabled == item.to_dict()["is_enabled"]

    def test_includes_correct_meta(self) -> None:
        client_data = {"foo": "bar"}
        meta = FeatureFlagStoreMeta(self.now, client_data)
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        assert meta.to_dict() == item.to_dict()["meta"]


class TestSerialize(BaseTest):
    def test_is_base_64_encoded(self) -> None:
        name = self.txt()
        is_enabled = True
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        assert isinstance(item.serialize().decode("utf-8"), str)

    def test_contains_all_fields_from_json(self) -> None:
        name = self.txt()
        is_enabled = True
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        assert json.dumps(item.to_dict()) == item.serialize().decode("utf-8")


class TestDeserialize(BaseTest):
    def test_returns_instance_of_class(self) -> None:
        name = self.txt()
        is_enabled = True
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        serialized = item.serialize()
        deserialized = FeatureFlagStoreItem.deserialize(serialized)
        assert isinstance(deserialized, FeatureFlagStoreItem)

    def test_sets_correct_feature_name(self) -> None:
        name = self.txt()
        is_enabled = True
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        serialized = item.serialize()
        deserialized = FeatureFlagStoreItem.deserialize(serialized)
        assert name == deserialized.to_dict()["feature_name"]

    def test_sets_correct_is_enabled(self) -> None:
        name = self.txt()
        is_enabled = True
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        serialized = item.serialize()
        deserialized = FeatureFlagStoreItem.deserialize(serialized)
        assert is_enabled == deserialized.is_enabled()

    def test_sets_correct_client_data(self) -> None:
        name = self.txt()
        is_enabled = True
        client_data = {"foo": "bar"}
        meta = FeatureFlagStoreMeta(self.now, client_data)
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        serialized = item.serialize()
        deserialized = FeatureFlagStoreItem.deserialize(serialized)
        assert client_data == deserialized.to_dict()["meta"]["client_data"]


class TestIsEnabled(BaseTest):
    def test_is_enabled_is_true(self) -> None:
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        assert item.is_enabled()

    def test_is_enabled_is_false(self) -> None:
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(self.txt(), False, meta)
        assert not item.is_enabled()

    def test_is_true_if_conditions_are_matched(self) -> None:
        meta = FeatureFlagStoreMeta(self.now, conditions=[Condition(foo=True)])
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        assert item.is_enabled(foo=True)

    def test_is_false_if_conditions_are_not_matched(self) -> None:
        meta = FeatureFlagStoreMeta(self.now, conditions=[Condition(foo=True)])
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        assert not item.is_enabled(foo=False)

    def test_is_false_if_one_of_many_conditions_are_not_matched(self) -> None:
        conditions = [Condition(foo=True), Condition(x=9)]
        meta = FeatureFlagStoreMeta(self.now, conditions=conditions)
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        assert not item.is_enabled(foo=True, x=11)

    def test_is_true_if_all_of_many_conditions_are_matched(self) -> None:
        conditions = [Condition(foo=True), Condition(x=9)]
        meta = FeatureFlagStoreMeta(self.now, conditions=conditions)
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        assert item.is_enabled(foo=True, x=9)

    def test_returns_false_if_bucketer_check_returns_false(self) -> None:
        bucketer = MagicMock()
        bucketer.check.return_value = False
        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer)
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        assert not item.is_enabled()

    def test_returns_true_if_bucketer_check_returns_true(self) -> None:
        bucketer = MagicMock()
        bucketer.check.return_value = True
        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer)
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        assert item.is_enabled()

    def test_returns_false_when_bucketer_returns_false_and_conditions_not_specified(
        self,
    ) -> None:
        # flag.is_enabled(user_id=2) # False  # noqa: ERA001
        bucketer = MagicMock()
        bucketer.check.return_value = False
        condition = Condition(is_admin=True)

        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer, conditions=[condition])
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        assert not item.is_enabled()

    def test_returns_true_when_bucketer_returns_false_and_conditions_return_true(
        self,
    ) -> None:
        # flag.is_enabled(user_id=2, is_admin=True) # True  # noqa: ERA001
        bucketer = MagicMock()
        bucketer.check.return_value = False
        condition = Condition(is_admin=True)

        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer, conditions=[condition])
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        assert item.is_enabled(is_admin=True)

    def test_returns_true_when_bucketer_returns_true_and_conditions_not_specified(
        self,
    ) -> None:
        # flag.is_enabled(user_id=1) # True  # noqa: ERA001
        bucketer = MagicMock()
        bucketer.check.return_value = True
        condition = Condition(is_admin=True)

        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer, conditions=[condition])
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        assert item.is_enabled()

    def test_returns_false_when_bucketer_returns_true_and_conditions_return_false(
        self,
    ) -> None:
        # flag.is_enabled(user_id=1, is_admin=False) # False  # noqa: ERA001
        bucketer = MagicMock()
        bucketer.check.return_value = True
        condition = Condition(is_admin=True)

        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer, conditions=[condition])
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        assert not item.is_enabled(is_admin=False)
