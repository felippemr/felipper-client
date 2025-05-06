import unittest
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from flipper import Condition, MemoryFeatureFlagStore
from flipper.bucketing import Percentage, PercentageBucketer
from flipper.client import FeatureFlagClient
from flipper.contrib.storage import FeatureFlagStoreMeta
from flipper.exceptions import FlagDoesNotExistError
from flipper.flag import FeatureFlag


class BaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.name = self.txt()
        self.store = MemoryFeatureFlagStore()
        self.client = FeatureFlagClient(self.store)
        self.flag = FeatureFlag(self.name, self.client)

    def txt(self):
        return uuid4().hex


class TestName(BaseTest):
    def test_name_gets_set(self) -> None:
        assert self.name == self.flag.name


class TestIsEnabled(BaseTest):
    def test_returns_true_when_feature_enabled(self) -> None:
        self.store.create(self.name)

        self.flag.enable()

        assert self.flag.is_enabled()

    def test_returns_false_when_feature_disabled(self) -> None:
        self.store.create(self.name)

        self.flag.enable()
        self.flag.disable()

        assert not self.flag.is_enabled()

    def test_returns_false_when_flag_does_not_exist(self) -> None:
        assert not self.flag.is_enabled()

    def test_returns_true_if_condition_specifies(self) -> None:
        self.store.create(self.name, is_enabled=True)
        self.flag.add_condition(Condition(foo=True))

        assert self.flag.is_enabled(foo=True)

    def test_returns_false_if_condition_specifies(self) -> None:
        self.store.create(self.name, is_enabled=True)
        self.flag.add_condition(Condition(foo=True))

        assert not self.flag.is_enabled(foo=False)

    def test_returns_false_if_feature_disabled_despite_condition(self) -> None:
        self.store.create(self.name, is_enabled=False)
        self.flag.add_condition(Condition(foo=True))

        assert not self.flag.is_enabled(foo=True)

    def test_returns_false_if_bucketer_check_returns_false(self) -> None:
        bucketer = MagicMock()
        bucketer.check.return_value = False

        self.store.create(self.name, is_enabled=True)
        self.flag.set_bucketer(bucketer)

        assert not self.flag.is_enabled()

    def test_returns_true_if_bucketer_check_returns_true(self) -> None:
        bucketer = MagicMock()
        bucketer.check.return_value = True

        self.store.create(self.name, is_enabled=True)
        self.flag.set_bucketer(bucketer)

        assert self.flag.is_enabled()

    def test_forwards_conditions_to_bucketer(self) -> None:
        bucketer = MagicMock()

        self.store.create(self.name, is_enabled=True)
        self.flag.set_bucketer(bucketer)

        self.flag.is_enabled(foo=True)

        bucketer.check.assert_called_with(foo=True)


class TestExists(BaseTest):
    def test_when_object_does_not_exist_returns_false(self) -> None:
        assert not self.flag.exists()

    def test_when_object_does_exist_returns_true(self) -> None:
        self.store.create(self.name)

        assert self.flag.exists()


class TestDestroy(BaseTest):
    def test_object_remains_instance_of_flag_class(self) -> None:
        self.store.create(self.name)

        self.flag.destroy()

        assert isinstance(self.flag, FeatureFlag)

    def test_status_switches_to_disabled(self) -> None:
        self.store.create(self.name)

        self.flag.enable()
        self.flag.destroy()

        assert not self.flag.is_enabled()

    def test_client_is_called_with_correct_args(self) -> None:
        client = MagicMock()
        flag = FeatureFlag(self.name, client)
        flag.destroy()

        client.destroy.assert_called_once_with(self.name)

    def test_raises_for_nonexistent_flag(self) -> None:
        with pytest.raises(FlagDoesNotExistError):
            self.flag.destroy()


class TestEnable(BaseTest):
    def test_is_enabled_will_be_true(self) -> None:
        self.store.create(self.name)

        self.flag.enable()

        assert self.flag.is_enabled()

    def test_is_enabled_will_be_true_if_disable_was_called_earlier(self) -> None:
        self.store.create(self.name)

        self.flag.disable()
        self.flag.enable()

        assert self.flag.is_enabled()

    def test_client_is_called_with_correct_args(self) -> None:
        client = MagicMock()
        flag = FeatureFlag(self.name, client)
        flag.enable()

        client.enable.assert_called_once_with(self.name)

    def test_raises_for_nonexistent_flag(self) -> None:
        with pytest.raises(FlagDoesNotExistError):
            self.flag.enable()


class TestDisable(BaseTest):
    def test_is_enabled_will_be_false(self) -> None:
        self.store.create(self.name, True)
        self.flag.disable()

        assert not self.flag.is_enabled()

    def test_is_enabled_will_be_false_if_enable_was_called_earlier(self) -> None:
        self.store.create(self.name)
        self.flag.enable()
        self.flag.disable()

        assert not self.flag.is_enabled()

    def test_client_is_called_with_correct_args(self) -> None:
        client = MagicMock()
        flag = FeatureFlag(self.name, client)
        flag.disable()

        client.disable.assert_called_once_with(self.name)

    def test_raises_for_nonexistent_flag(self) -> None:
        with pytest.raises(FlagDoesNotExistError):
            self.flag.disable()


class TestSetClientData(BaseTest):
    def test_calls_backend_with_correct_feature_name(self) -> None:
        self.store.set_meta = MagicMock()

        client_data = {self.txt(): self.txt()}

        self.store.create(self.name)
        self.flag.set_client_data(client_data)

        [actual, _] = self.store.set_meta.call_args[0]

        assert self.name == actual

    def test_calls_backend_with_instance_of_meta(self) -> None:
        self.store.set_meta = MagicMock()

        client_data = {self.txt(): self.txt()}

        self.store.create(self.name)
        self.flag.set_client_data(client_data)

        [_, meta] = self.store.set_meta.call_args[0]

        assert isinstance(meta, FeatureFlagStoreMeta)

    def test_calls_backend_with_correct_meta_client_data(self) -> None:
        self.store.set_meta = MagicMock()

        client_data = {self.txt(): self.txt()}

        self.store.create(self.name)
        self.flag.set_client_data(client_data)

        [_, meta] = self.store.set_meta.call_args[0]

        assert client_data == meta.client_data

    def test_calls_backend_with_non_null_meta_created_date(self) -> None:
        self.store.set_meta = MagicMock()

        client_data = {self.txt(): self.txt()}

        self.store.create(self.name)
        self.flag.set_client_data(client_data)

        [_, meta] = self.store.set_meta.call_args[0]

        assert meta.created_date is not None

    def test_calls_backend_exactly_once(self) -> None:
        self.store.set_meta = MagicMock()

        client_data = {self.txt(): self.txt()}

        self.store.create(self.name)
        self.flag.set_client_data(client_data)

        assert self.store.set_meta.call_count == 1

    def test_merges_new_values_with_existing(self) -> None:
        existing_data = {"existing_key": self.txt()}

        self.store.create(self.name, client_data=existing_data)

        new_data = {"new_key": self.txt()}
        self.flag.set_client_data(new_data)

        item = self.store.get(self.name)

        assert {**existing_data, **new_data} == item.meta["client_data"]

    def test_can_override_existing_values(self) -> None:
        existing_data = {"existing_key": self.txt()}

        self.store.create(self.name, client_data=existing_data)

        new_data = {"existing_key": self.txt(), "new_key": self.txt()}
        self.flag.set_client_data(new_data)

        item = self.store.get(self.name)

        assert new_data == item.meta["client_data"]

    def test_raises_for_nonexistent_flag(self) -> None:
        client_data = {self.txt(): self.txt()}

        with pytest.raises(FlagDoesNotExistError):
            self.flag.set_client_data(client_data)


class TestGetClientData(BaseTest):
    def test_gets_expected_key_value_pairs(self) -> None:
        client_data = {self.txt(): self.txt()}

        self.store.create(self.name, client_data=client_data)

        result = self.flag.get_client_data()

        assert client_data == result

    def test_raises_for_nonexistent_flag(self) -> None:
        with pytest.raises(FlagDoesNotExistError):
            self.flag.get_client_data()


class TestGetMeta(BaseTest):
    def test_includes_created_date(self) -> None:
        client_data = {self.txt(): self.txt()}

        self.store.create(self.name, client_data=client_data)

        meta = self.flag.get_meta()

        assert "created_date" in meta

    def test_includes_client_data(self) -> None:
        client_data = {self.txt(): self.txt()}

        self.store.create(self.name, client_data=client_data)

        meta = self.flag.get_meta()

        assert client_data == meta["client_data"]

    def test_raises_for_nonexistent_flag(self) -> None:
        with pytest.raises(FlagDoesNotExistError):
            self.flag.get_meta()


class TestAddCondition(BaseTest):
    def test_condition_gets_included_in_meta(self) -> None:
        condition_checks = {self.txt(): True}
        condition = Condition(**condition_checks)

        self.store.create(self.name)
        self.flag.add_condition(condition)

        meta = self.flag.get_meta()

        assert condition.to_dict() in meta["conditions"]

    def test_condition_gets_appended_to_meta(self) -> None:
        condition_checks = {self.txt(): True}
        condition = Condition(**condition_checks)

        self.store.create(self.name)
        self.flag.add_condition(condition)
        self.flag.add_condition(condition)

        meta = self.flag.get_meta()

        assert len(meta["conditions"]) == 2  # noqa: PLR2004


class TestSetBucketer(BaseTest):
    def test_bucketer_gets_included_in_meta(self) -> None:
        percentage_value = 0.1
        bucketer = PercentageBucketer(percentage=Percentage(percentage_value))

        self.store.create(self.name)
        self.flag.set_bucketer(bucketer)

        meta = self.flag.get_meta()

        assert bucketer.to_dict() == meta["bucketer"]


class TestSetConditions(BaseTest):
    def test_overrides_previous_conditions(self) -> None:
        self.store.create(self.name)
        overriden_condition = Condition(value=True)
        new_conditions = [Condition(new_value=True), Condition(id__in=[1, 2])]

        self.flag.add_condition(overriden_condition)
        self.flag.set_conditions(new_conditions)

        conditions_array = self.flag.get_meta()["conditions"]
        expected_conditions_array = [
            {"new_value": [{"variable": "new_value", "value": True, "operator": None}]},
            {"id": [{"variable": "id", "value": [1, 2], "operator": "in"}]},
        ]

        assert expected_conditions_array == conditions_array
