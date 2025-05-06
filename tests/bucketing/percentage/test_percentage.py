import unittest

from flipper.bucketing import Percentage


class TestGetType(unittest.TestCase):
    def test_is_correct_value(self) -> None:
        percentage = Percentage()
        assert percentage.get_type() == "Percentage"


class TestValue(unittest.TestCase):
    def test_matches_value_provided_in_constructor(self) -> None:
        value = 0.8
        percentage = Percentage(value=value)
        assert value == percentage.value

    def test_defaults_to_1_dot_0(self) -> None:
        percentage = Percentage()
        assert percentage.value == 1.0


class TestToDict(unittest.TestCase):
    def test_returns_correct_values(self) -> None:
        value = 0.8
        percentage = Percentage(value=value)
        expected = {"value": value, "type": Percentage.get_type()}
        assert expected == percentage.to_dict()


class TestFromDict(unittest.TestCase):
    def test_sets_correct_data(self) -> None:
        data = {"value": 0.8, "type": Percentage.get_type()}
        percentage = Percentage.from_dict(data)
        assert data == percentage.to_dict()
