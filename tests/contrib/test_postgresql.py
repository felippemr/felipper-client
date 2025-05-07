import unittest
from collections.abc import Iterable

import pytest
import testing.postgresql

from flipper import PostgreSQLFeatureFlagStore
from flipper.client import FeatureFlagClient
from flipper.conditions.condition import Condition
from flipper.contrib.interface import FlagDoesNotExistError
from flipper.contrib.storage import FeatureFlagStoreMeta
from flipper.contrib.util.date import now

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)


def tearDownModule(self) -> None:
    Postgresql.clear_cache()


class BaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self._db = Postgresql()
        self.store = PostgreSQLFeatureFlagStore(self._db.url())

    def tearDown(self) -> None:
        self._db.stop()


class TestRunMigration(unittest.TestCase):
    def test_run_migration_creates_table(self) -> None:
        db = Postgresql()
        store = PostgreSQLFeatureFlagStore(db.url(), run_migrations=False)

        store.run_migrations()

        assert store.get("") is None


class TestCreate(BaseTest):
    def test_feature_flag_exists_when_created(self) -> None:
        feature_name = "test"

        item = self.store.create(feature_name)

        assert item is not None

    def test_create_overrides_when_existing_feature_flag(self) -> None:
        feature_name = "test"

        self.store.create(feature_name)
        new_item = self.store.create(feature_name, client_data={"test": "data"})

        result = self.store.get(feature_name)
        assert result
        assert new_item.meta == result.meta

    def test_is_enabled_is_false_when_created_with_default(self) -> None:
        item = self.store.create("test")

        assert not item.is_enabled()

    def test_is_enabled_is_true_when_created_with_is_enabled(self) -> None:
        item = self.store.create("test", is_enabled=True)

        assert item.is_enabled()

    def test_is_enabled_is_false_when_created_with_not_is_enabled(self) -> None:
        item = self.store.create("test", is_enabled=False)

        assert not item.is_enabled()

    def test_client_data_is_persisted_when_created_with_client_data(self) -> None:
        client_data = {"test": "data"}

        item = self.store.create("test", client_data=client_data)

        assert item.meta["client_data"] == client_data


class TestGet(BaseTest):
    def test_returns_none_when_no_such_feature_flag(self) -> None:
        item = self.store.get("test")

        assert item is None


class TestList(BaseTest):
    def _create_several(self, names: Iterable[str]) -> None:
        for name in names:
            self.store.create(name)

    def test_returns_empty_iterator_when_no_feature_flags(self) -> None:
        items = list(self.store.list())

        assert len(items) == 0

    def test_returns_feature_flags(self) -> None:
        expected_names = {"test1", "test2"}
        self._create_several(expected_names)

        names = {x.feature_name for x in self.store.list()}

        self.assertSetEqual(names, expected_names)  # noqa: PT009

    def test_limits_return_items_when_limit_is_given(self) -> None:
        self._create_several({"test1", "test2"})

        items = list(self.store.list(limit=1))

        assert len(items) == 1

    def test_starts_with_offset_when_offset_is_given(self) -> None:
        self._create_several({"test1", "test2"})

        items = list(self.store.list(offset=1))

        assert len(items) == 1


class TestSetMeta(BaseTest):
    def test_raises_exception_for_nonexistent_flag(self) -> None:
        meta = FeatureFlagStoreMeta(now())

        with pytest.raises(FlagDoesNotExistError):
            self.store.set_meta("test", meta)

    def test_updated_meta(self) -> None:
        self.store.create("test")
        expected_meta = FeatureFlagStoreMeta(now(), client_data={"test": "date"})

        self.store.set_meta("test", expected_meta)

        result = self.store.get("test")
        assert result is not None
        meta = result.meta
        assert meta == expected_meta.to_dict()

    def test_condition(self) -> None:
        client = FeatureFlagClient(self.store)
        client.create("test")
        client.enable("test")
        client.add_condition("test", Condition(is_administrator=True))

        assert client.is_enabled("test", is_administrator=True)

    def test_condition_in(self) -> None:
        client = FeatureFlagClient(self.store)
        client.create("test")
        client.enable("test")
        client.add_condition("test", Condition(company__in=[1, 2, 3, 4]))

        assert client.is_enabled("test", company=1)


class TestDelete(BaseTest):
    def test_does_not_raise_exception_when_no_existing_flag(self) -> None:
        item = self.store.get("test")

        assert item is None

        self.store.delete("test")

    def test_deletes_existing_flag(self) -> None:
        self.store.create("test")

        self.store.delete("test")

        item = self.store.get("test")
        assert item is None
