import unittest

from flipper.bucketing import ConsistentHashPercentageBucketer, Percentage


class TestGetType(unittest.TestCase):
    def test_is_correct_value(self) -> None:
        bucketer = ConsistentHashPercentageBucketer()
        assert bucketer.get_type() == "ConsistentHashPercentageBucketer"


class TestPercentage(unittest.TestCase):
    def test_returns_percentage_value_as_float(self) -> None:
        percentage_raw_value = 0.5
        percentage = Percentage(value=percentage_raw_value)
        bucketer = ConsistentHashPercentageBucketer(percentage=percentage)
        assert percentage_raw_value == bucketer.percentage


class TestCheck(unittest.TestCase):
    def test_returns_true_when_randomized_is_less_than_percentage(self) -> None:
        percentage = Percentage(value=0.5)
        bucketer = ConsistentHashPercentageBucketer(percentage=percentage)
        assert bucketer.check()  # score = 0.32

    def test_returns_true_when_randomized_is_equal_to_percentage(self) -> None:
        percentage = Percentage(value=0.32)
        bucketer = ConsistentHashPercentageBucketer(percentage=percentage)
        assert bucketer.check()  # score = 0.32

    def test_returns_false_when_randomized_is_greater_than_percentage(self) -> None:
        percentage = Percentage(value=0.2)
        bucketer = ConsistentHashPercentageBucketer(percentage=percentage)
        assert not bucketer.check()  # score = 0.32

    def test_always_returns_false_when_percentage_is_zero(self) -> None:
        percentage = Percentage(value=0.0)
        bucketer = ConsistentHashPercentageBucketer(percentage=percentage)
        assert not bucketer.check()  # score = 0.32

    def test_returns_true_when_conditions_hash_to_value_less_than_percentage(
        self,
    ) -> None:
        percentage = Percentage(value=0.8)
        bucketer = ConsistentHashPercentageBucketer(percentage=percentage)
        assert bucketer.check(foo="bar")  # score = 0.79

    def test_returns_false_when_conditions_hash_to_value_greater_than_percentage(
        self,
    ) -> None:
        percentage = Percentage(value=0.5)
        bucketer = ConsistentHashPercentageBucketer(percentage=percentage)
        assert not bucketer.check(foo="bar")  # score = 0.79

    def test_returns_true_when_conditions_hash_to_value_equal_to_percentage(
        self,
    ) -> None:
        percentage = Percentage(value=0.79)
        bucketer = ConsistentHashPercentageBucketer(percentage=percentage)
        assert bucketer.check(foo="bar")  # score = 0.79

    def test_always_returns_false_when_percentage_is_zero_when_including_conditions(
        self,
    ) -> None:
        percentage = Percentage(value=0.0)
        bucketer = ConsistentHashPercentageBucketer(percentage=percentage)
        assert not bucketer.check(foo="bar")  # score = 0.79

    def test_hashing_is_consistent(self) -> None:
        percentage = Percentage(value=0.67001)
        bucketer = ConsistentHashPercentageBucketer(percentage=percentage)
        for _ in range(10):
            self.assertTrue(  # noqa: PT009
                bucketer.check(foo="bar", herp=99, derp=False),  # score = 0.67
            )


class TestToDict(unittest.TestCase):
    def test_returns_correct_data(self) -> None:
        percentage = Percentage(value=0.5)
        key_whitelist = ["foo"]
        bucketer = ConsistentHashPercentageBucketer(
            key_whitelist=key_whitelist, percentage=percentage,
        )
        expected = {
            "type": ConsistentHashPercentageBucketer.get_type(),
            "key_whitelist": key_whitelist,
            "percentage": percentage.to_dict(),
        }
        assert expected == bucketer.to_dict()


class TestFromDict(unittest.TestCase):
    def test_sets_correct_data(self) -> None:
        percentage = Percentage(value=0.5)
        key_whitelist = ["foo"]
        data = {
            "type": ConsistentHashPercentageBucketer.get_type(),
            "key_whitelist": key_whitelist,
            "percentage": percentage.to_dict(),
        }
        bucketer = ConsistentHashPercentageBucketer.from_dict(data)
        assert data == bucketer.to_dict()
