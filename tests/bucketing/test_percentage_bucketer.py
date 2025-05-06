import unittest
from unittest.mock import MagicMock

from flipper.bucketing import Percentage, PercentageBucketer


class TestGetType(unittest.TestCase):
    def test_is_correct_value(self) -> None:
        bucketer = PercentageBucketer()
        assert bucketer.get_type() == "PercentageBucketer"


class TestPercentage(unittest.TestCase):
    def test_returns_percentage_value_as_float(self) -> None:
        percentage_raw_value = 0.5
        percentage = Percentage(value=percentage_raw_value)
        bucketer = PercentageBucketer(percentage=percentage)
        assert percentage_raw_value == bucketer.percentage


class TestCheck(unittest.TestCase):
    def test_returns_true_when_randomized_is_less_than_percentage(self) -> None:
        percentage = Percentage(value=0.5)
        bucketer = PercentageBucketer(percentage=percentage)
        randomizer = MagicMock(return_value=0.4)
        assert bucketer.check(randomizer=randomizer)

    def test_returns_true_when_randomized_is_equal_to_percentage(self) -> None:
        percentage = Percentage(value=0.5)
        bucketer = PercentageBucketer(percentage=percentage)
        randomizer = MagicMock(return_value=0.5)
        assert bucketer.check(randomizer=randomizer)

    def test_returns_false_when_randomized_is_greater_than_percentage(self) -> None:
        percentage = Percentage(value=0.5)
        bucketer = PercentageBucketer(percentage=percentage)
        randomizer = MagicMock(return_value=0.6)
        assert not bucketer.check(randomizer=randomizer)

    def test_always_returns_false_when_percentage_is_zero(self) -> None:
        percentage = Percentage(value=0.0)
        bucketer = PercentageBucketer(percentage=percentage)
        randomizer = MagicMock(return_value=0.0)
        assert not bucketer.check(randomizer=randomizer)


class TestToDict(unittest.TestCase):
    def test_returns_correct_data(self) -> None:
        percentage = Percentage(value=0.5)
        bucketer = PercentageBucketer(percentage=percentage)
        expected = {
            "type": PercentageBucketer.get_type(),
            "percentage": percentage.to_dict(),
        }
        assert expected == bucketer.to_dict()


class TestFromDict(unittest.TestCase):
    def test_sets_correct_data(self) -> None:
        percentage = Percentage(value=0.5)
        data = {
            "type": PercentageBucketer.get_type(),
            "percentage": percentage.to_dict(),
        }
        bucketer = PercentageBucketer.from_dict(data)
        assert data == bucketer.to_dict()
