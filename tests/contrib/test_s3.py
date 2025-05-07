import datetime
import unittest
from uuid import uuid4

import boto3
import pytest
from moto import mock_aws

from flipper import S3FeatureFlagStore
from flipper.contrib.interface import FlagDoesNotExistError
from flipper.contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class BaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.s3 = mock_aws()
        self.s3.start()
        self.conn = boto3.resource(
            "s3",
            aws_access_key_id="aws_access_key_id",
            aws_secret_access_key="aws_secret_access_key",  # noqa: S106
        )
        self.bucket_name = "flipper"
        self.bucket = self.conn.create_bucket(Bucket=self.bucket_name)  # type: ignore[reportArgumentType]
        self.client = boto3.client(
            "s3",
            aws_access_key_id="aws_access_key_id",
            aws_secret_access_key="aws_secret_access_key",  # noqa: S106
        )
        self.store = S3FeatureFlagStore(self.client, self.bucket_name)

    def tearDown(self) -> None:
        self.s3.stop()

    def txt(self):
        return uuid4().hex

    def date(self):
        return int(datetime.datetime(2018, 1, 1).timestamp())  # noqa: DTZ001


class TestCreate(BaseTest):
    def test_is_enabled_is_true_when_created_with_is_enabled_true(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)

        result = self.store.get(feature_name)
        assert result
        assert result.is_enabled()

    def test_is_enabled_is_true_when_created_with_default_false(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=False)

        result = self.store.get(feature_name)
        assert result
        assert not result.is_enabled()

    def test_is_enabled_is_false_when_created_with_default(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name)

        result = self.store.get(feature_name)
        assert result
        assert not result.is_enabled()

    def test_sets_correct_value_in_s3_with_is_enabled_true(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)

        serialized = self.client.get_object(Bucket=self.bucket_name, Key=feature_name)["Body"].read()

        assert FeatureFlagStoreItem.deserialize(serialized).is_enabled()

    def test_sets_correct_value_in_s3_with_is_enabled_false(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=False)

        serialized = self.client.get_object(Bucket=self.bucket_name, Key=feature_name)["Body"].read()

        assert not FeatureFlagStoreItem.deserialize(serialized).is_enabled()

    def test_sets_correct_value_in_s3_with_default(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name)

        serialized = self.client.get_object(Bucket=self.bucket_name, Key=feature_name)["Body"].read()

        assert not FeatureFlagStoreItem.deserialize(serialized).is_enabled()


class TestGet(BaseTest):
    def test_returns_instance_of_feature_flag(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name)

        assert isinstance(self.store.get(feature_name), FeatureFlagStoreItem)

    def test_returns_none_when_flag_does_not_exist(self) -> None:
        feature_name = self.txt()

        assert self.store.get(feature_name) is None


class TestSet(BaseTest):
    def test_sets_correct_value_when_true(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, True)

        result = self.store.get(feature_name)
        assert result
        assert result.is_enabled()

    def test_sets_correct_value_when_false(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, False)

        result = self.store.get(feature_name)
        assert result
        assert not result.is_enabled()

    def test_sets_correct_value_in_s3_when_true(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.set(feature_name, True)

        serialized = self.client.get_object(Bucket=self.bucket_name, Key=feature_name)["Body"].read()

        assert FeatureFlagStoreItem.deserialize(serialized).is_enabled()

    def test_sets_correct_value_in_s3_when_false(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.set(feature_name, False)

        serialized = self.client.get_object(Bucket=self.bucket_name, Key=feature_name)["Body"].read()

        assert not FeatureFlagStoreItem.deserialize(serialized).is_enabled()

    def test_sets_correct_value_when_not_created(self) -> None:
        feature_name = self.txt()

        self.store.set(feature_name, True)

        result = self.store.get(feature_name)
        assert result
        assert result.is_enabled()


class TestDelete(BaseTest):
    def test_returns_false_after_delete(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, True)
        self.store.delete(feature_name)

        assert self.store.get(feature_name) is None

    def test_does_not_raise_when_deleting_key_that_does_not_exist(self) -> None:
        feature_name = self.txt()

        self.store.delete(feature_name)

        assert self.store.get(feature_name) is None

    def test_deletes_value_from_s3(self) -> None:
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.delete(feature_name)

        with pytest.raises(self.client.exceptions.NoSuchKey):
            self.client.get_object(Bucket=self.bucket_name, Key=feature_name)


class TestList(BaseTest):
    def test_returns_all_features(self) -> None:
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.store.create(name)

        results = self.store.list()

        expected = sorted(feature_names)
        actual = sorted([item.feature_name for item in results])

        assert expected == actual

    def test_returns_features_subject_to_offset(self) -> None:
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.store.create(name)

        offset = 3

        results = self.store.list(offset=offset)

        actual = [item.feature_name for item in results]

        assert len(feature_names) - offset == len(actual)
        for feature_name in actual:
            assert feature_name in feature_names

    def test_returns_features_subject_to_limit(self) -> None:
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.store.create(name)

        limit = 3

        results = self.store.list(limit=limit)

        actual = [item.feature_name for item in results]

        assert limit == len(actual)
        for feature_name in actual:
            assert feature_name in feature_names

    def test_returns_features_subject_to_offset_and_limit(self) -> None:
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.store.create(name)

        offset = 2
        limit = 3

        results = self.store.list(limit=limit, offset=offset)

        actual = [item.feature_name for item in results]

        assert limit == len(actual)
        for feature_name in actual:
            assert feature_name in feature_names


class TestSetMeta(BaseTest):
    def test_sets_client_data_correctly(self) -> None:
        feature_name = self.txt()
        self.store.create(feature_name)

        client_data = {self.txt(): self.txt()}
        meta = FeatureFlagStoreMeta(self.date(), client_data)

        self.store.set_meta(feature_name, meta)

        item = self.store.get(feature_name)

        assert item
        assert client_data == item.meta["client_data"]

    def test_sets_created_date_correctly(self) -> None:
        feature_name = self.txt()
        self.store.create(feature_name)

        client_data = {self.txt(): self.txt()}
        created_date = self.date()
        meta = FeatureFlagStoreMeta(self.date(), client_data)

        self.store.set_meta(feature_name, meta)

        item = self.store.get(feature_name)

        assert item
        assert created_date == item.meta["created_date"]

    def test_raises_exception_for_nonexistent_flag(self) -> None:
        feature_name = self.txt()
        with pytest.raises(FlagDoesNotExistError):
            self.store.set_meta(feature_name, {"a": self.txt()})  # type: ignore[reportArgumentType]
